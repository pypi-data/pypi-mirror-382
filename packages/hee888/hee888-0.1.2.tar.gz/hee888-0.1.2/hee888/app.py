"""High-speed multi-threaded video downloader using HTTP range requests."""

from __future__ import annotations

import argparse
import concurrent.futures
import math
import os
import re
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional

import requests
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


def make_session(default_headers: Optional[dict] = None) -> requests.Session:
	"""Create and return a requests.Session pre-configured with sensible defaults.

	This is a small helper so other modules (or an installed package user) can
	obtain a Session with the same User-Agent and optional extractor headers.

	Args:
		default_headers: Optional dict of headers to apply to the session.

	Returns:
		A configured requests.Session instance.
	"""
	sess = requests.Session()
	# Provide a reasonable default UA if none is present
	sess.headers.update({"User-Agent": "Mozilla/5.0 (compatible; modfile/1.0)"})
	if default_headers:
		sess.headers.update(default_headers)
	return sess


def create_prepared_request(
	url: str,
	method: str = "GET",
	headers: Optional[dict] = None,
	params: Optional[dict] = None,
	data: Optional[object] = None,
) -> requests.PreparedRequest:
	"""Build and return a PreparedRequest for the given parameters.

	A PreparedRequest can be sent with a Session via Session.send() or used
	to inspect what will be transmitted. This helper is useful for callers
	that want an opaque 'request object' to modify or reuse.
	"""
	req = requests.Request(method=method.upper(), url=url, headers=headers, params=params, data=data)
	sess = requests.Session()
	return sess.prepare_request(req)


@dataclass(frozen=True)
class ChunkSpec:
	"""Descriptor for a byte-range chunk."""

	part_number: int
	start: int
	end: int

	@property
	def header_value(self) -> str:
		return f"bytes={self.start}-{self.end}"

	@property
	def filename(self) -> str:
		return f"part_{self.part_number:04d}.part"


@dataclass(frozen=True)
class FormatOption:
	index: int
	format_id: str
	label: str
	height: Optional[int]
	ext: str
	filesize: Optional[int]
	url: str
	format_note: str
	http_headers: Optional[dict]

	def human_size(self) -> str:
		return human_readable_size(self.filesize)


def human_readable_size(num: Optional[int]) -> str:
	if num is None or num <= 0:
		return "unknown"

	units = ["B", "KiB", "MiB", "GiB", "TiB"]
	value = float(num)
	for unit in units:
		if value < 1024 or unit == units[-1]:
			return f"{value:,.2f} {unit}"
		value /= 1024
	return f"{value:,.2f} PiB"


def sanitize_filename(name: str, fallback: str = "download") -> str:
	name = name.strip() or fallback
	clean = re.sub(r"[\\/*?:\"<>|]", "_", name)
	clean = re.sub(r"\s+", " ", clean).strip()
	return clean or fallback


def collect_format_options(info: dict) -> List[FormatOption]:
	formats = info.get("formats") or []
	options: List[FormatOption] = []
	op_index = 1
	seen = set()
	for fmt in formats:
		if fmt.get("vcodec") == "none" or fmt.get("acodec") == "none":
			continue
		protocol = fmt.get("protocol") or ""
		if "m3u8" in protocol or "dash" in protocol:
			continue
		height = fmt.get("height")
		ext = fmt.get("ext") or info.get("ext") or "mp4"
		label = fmt.get("format_note") or fmt.get("format") or "video"
		filesize = (
			fmt.get("filesize")
			or fmt.get("filesize_approx")
			or fmt.get("tbr") and int(fmt.get("tbr") * 125000)  # rough fall-back
		)
		url = fmt.get("url")
		if not url:
			continue
		key = (height, ext, url)
		if key in seen:
			continue
		seen.add(key)
		format_note = fmt.get("format_note") or ""
		options.append(
			FormatOption(
				index=op_index,
				format_id=fmt.get("format_id", str(op_index)),
				label=label,
				height=height,
				ext=ext,
				filesize=filesize if isinstance(filesize, int) else None,
				url=url,
				format_note=format_note,
				http_headers=fmt.get("http_headers"),
			),
		)
		op_index += 1

	options.sort(key=lambda opt: (opt.height or 0, opt.filesize or 0), reverse=True)
	for idx, option in enumerate(options, start=1):
		options[idx - 1] = OptionWithIndex(option, idx)
	return options


def OptionWithIndex(option: FormatOption, new_index: int) -> FormatOption:
	return FormatOption(
		index=new_index,
		format_id=option.format_id,
		label=option.label,
		height=option.height,
		ext=option.ext,
		filesize=option.filesize,
		url=option.url,
		format_note=option.format_note,
		http_headers=option.http_headers,
	)


def render_format_menu(options: List[FormatOption]) -> None:
	print("Available qualities:")
	for option in options:
		resolution = f"{option.height}p" if option.height else "unknown"
		note = f" ({option.format_note})" if option.format_note else ""
		print(
			f"  {option.index}. {resolution:<7} {option.ext:<4} {option.human_size():>12} - "
			f"format {option.format_id}{note}",
		)


def auto_select_quality(options: List[FormatOption], quality: Optional[str]) -> Optional[FormatOption]:
	if not options:
		return None
	if quality is None:
		return None
	quality = quality.strip().lower()
	if quality in {"best", "max", "highest"}:
		return options[0]
	if quality in {"worst", "min", "lowest"}:
		return options[-1]
	quality = quality.replace("p", "")
	if quality.isdigit():
		desired = int(quality)
		sorted_opts = sorted(
			options,
			key=lambda opt: (abs((opt.height or 0) - desired), -(opt.height or 0)),
		)
		return sorted_opts[0]
	return None


def prompt_for_format_selection(options: List[FormatOption]) -> FormatOption:
	while True:
		try:
			choice = input("Select quality [1]: ").strip()
		except EOFError:
			return options[0]
		if not choice:
			return options[0]
		if choice.isdigit():
			idx = int(choice)
			for option in options:
				if option.index == idx:
					return option
		print("Invalid selection. Please enter one of the listed numbers.")


def gather_format_selection(
	url: str,
	requested_quality: Optional[str],
) -> Optional[tuple[FormatOption, dict]]:
	ydl_opts = {
		"quiet": True,
		"skip_download": True,
		"noplaylist": True,
		"no_warnings": True,
	}
	try:
		with YoutubeDL(ydl_opts) as ydl:
			info = ydl.extract_info(url, download=False)
	except DownloadError:
		return None

	options = collect_format_options(info)
	if not options:
		direct_url = info.get("url")
		if direct_url:
			filesize = info.get("filesize") or info.get("filesize_approx")
			height = info.get("height")
			ext = info.get("ext") or "mp4"
			label = info.get("format") or info.get("resolution") or "direct"
			options = [
				FormatOption(
					index=1,
					format_id=info.get("format_id", "direct"),
					label=label,
					height=height,
					ext=ext,
					filesize=filesize if isinstance(filesize, int) else None,
					url=direct_url,
					format_note=info.get("format_note") or "direct",
					http_headers=info.get("http_headers"),
				)
			]
		else:
			return None

	auto_choice = auto_select_quality(options, requested_quality)
	if auto_choice is None:
		render_format_menu(options)
		selected = prompt_for_format_selection(options)
	else:
		render_format_menu(options)
		print(f"Auto-selected quality: option {auto_choice.index} ({auto_choice.label})")
		selected = auto_choice

	return selected, info



class ProgressTracker:
	"""Thread-safe progress tracker with optional tqdm progress bar."""

	def __init__(self, total_bytes: Optional[int]) -> None:
		self.total = total_bytes
		self.downloaded = 0
		self.lock = threading.Lock()
		self._last_print = 0.0
		self._tqdm = self._load_tqdm(total_bytes)

	@staticmethod
	def _load_tqdm(total_bytes: Optional[int]):
		try:  # pragma: no cover - optional dependency
			from tqdm import tqdm

			return tqdm(total=total_bytes, unit="B", unit_scale=True, unit_divisor=1024)
		except Exception:
			return None

	def update(self, size: int) -> None:
		if size <= 0:
			return

		with self.lock:
			self.downloaded += size
			if self._tqdm is not None:
				self._tqdm.update(size)
				return

			now = time.time()
			should_print = now - self._last_print >= 0.5
			if self.total is not None and self.downloaded >= self.total:
				should_print = True

			if should_print:
				if self.total is not None and self.total > 0:
					percent = (self.downloaded / self.total) * 100
					status = f"{self.downloaded:,}/{self.total:,} bytes ({percent:5.1f}%)"
				else:
					status = f"{self.downloaded:,} bytes"
				sys.stdout.write(f"\rDownloading: {status}")
				sys.stdout.flush()
				self._last_print = now

	def close(self) -> None:
		if self._tqdm is None:
			sys.stdout.write("\n")
			sys.stdout.flush()
		else:  # pragma: no cover - optional dependency
			self._tqdm.close()


def _parse_total_from_content_range(content_range: Optional[str]) -> Optional[int]:
	if not content_range or "/" not in content_range:
		return None
	try:
		return int(content_range.split("/")[-1])
	except ValueError:
		return None


def _probe_size_via_binary_search(
	url: str,
	session: requests.Session,
	timeout: int,
	max_attempts: int = 32,
) -> Optional[int]:
	"""Infer size by probing single-byte ranges with exponential search."""

	# First, double the probe offset until a 416 Range Not Satisfiable is returned.
	probe = 1
	attempts = 0
	while attempts < max_attempts:
		attempts += 1
		headers = {"Range": f"bytes={probe}-{probe}"}
		with session.get(url, headers=headers, timeout=timeout, stream=True) as resp:
			if resp.status_code == 206:
				probe = (probe + 1) * 2  # move to next exponential position
				continue
			if resp.status_code == 416:
				total = _parse_total_from_content_range(resp.headers.get("Content-Range"))
				if total is not None:
					return total
				break
			if resp.status_code == 200:
				content_length = resp.headers.get("Content-Length")
				if content_length:
					return int(content_length)
				break
			resp.raise_for_status()

	return None


def get_file_size(url: str, session: Optional[requests.Session] = None, timeout: int = 15) -> int:
	"""Return Content-Length of the URL, attempting multiple strategies."""

	sess = session or requests.Session()

	head_resp = sess.head(url, allow_redirects=True, timeout=timeout)
	head_resp.raise_for_status()

	content_length = head_resp.headers.get("Content-Length")
	if content_length is not None:
		return int(content_length)

	# Some servers don't return Content-Length on HEAD. Try ranged GET.
	with sess.get(url, headers={"Range": "bytes=0-0"}, timeout=timeout, stream=True) as get_resp:
		if get_resp.status_code in (200, 206):
			content_range = get_resp.headers.get("Content-Range")
			total = _parse_total_from_content_range(content_range)
			if total is not None:
				return total
			if get_resp.status_code == 200:
				length = get_resp.headers.get("Content-Length")
				if length is not None:
					return int(length)
		get_resp.raise_for_status()

	probed_size = _probe_size_via_binary_search(url, sess, timeout)
	if probed_size is not None:
		return probed_size

	raise RuntimeError(
		"Unable to determine file size; server did not provide Content-Length or range support",
	)


def build_chunks(total_size: int, chunk_size: int) -> List[ChunkSpec]:
	chunk_count = math.ceil(total_size / chunk_size)
	chunks: List[ChunkSpec] = []
	for part in range(chunk_count):
		start = part * chunk_size
		end = min(start + chunk_size - 1, total_size - 1)
		chunks.append(ChunkSpec(part_number=part, start=start, end=end))
	return chunks


def download_chunk(
	url: str,
	chunk: ChunkSpec,
	dest_dir: str,
	session_factory,
	progress: ProgressTracker,
	max_retries: int = 5,
	timeout: int = 30,
) -> str:
	"""Download a chunk to dest_dir and return the file path."""

	part_path = os.path.join(dest_dir, chunk.filename)

	for attempt in range(1, max_retries + 1):
		session = session_factory()
		try:
			resp = session.get(
				url,
				headers={"Range": chunk.header_value},
				stream=True,
				timeout=timeout,
			)
			resp.raise_for_status()

			if resp.status_code not in (200, 206):
				raise RuntimeError(f"Unexpected status code {resp.status_code} for {chunk.header_value}")

			with open(part_path, "wb") as handle:
				for data in resp.iter_content(chunk_size=1024 * 128):
					if not data:
						continue
					handle.write(data)
					progress.update(len(data))

			return part_path
		except Exception as exc:
			if os.path.exists(part_path):
				os.remove(part_path)

			if attempt == max_retries:
				raise RuntimeError(f"Failed downloading chunk {chunk.part_number} after {max_retries} attempts") from exc

			backoff = 2 ** (attempt - 1)
			time.sleep(backoff)
		finally:
			session.close()

	raise RuntimeError(f"Exhausted retries for chunk {chunk.part_number}")


def merge_files(parts: Iterable[str], output_file: str) -> None:
	"""Concatenate chunk files into the final output file."""

	with open(output_file, "wb") as dest:
		for part_path in parts:
			with open(part_path, "rb") as part:
				for block in iter(lambda: part.read(1024 * 1024), b""):
					dest.write(block)


def delete_files(parts: Iterable[str]) -> None:
	for part_path in parts:
		try:
			os.remove(part_path)
		except FileNotFoundError:
			pass


def download_without_known_size(
	url: str,
	output_file: str,
	session: requests.Session,
	chunk_size: int,
	max_retries: int = 5,
	timeout: int = 60,
) -> None:
	"""Stream the entire file when size and range support are unavailable."""

	progress = ProgressTracker(None)
	try:
		for attempt in range(1, max_retries + 1):
			temp_fd, temp_path = tempfile.mkstemp(prefix="single_stream_", suffix=".part")
			os.close(temp_fd)
			try:
				with session.get(url, stream=True, timeout=timeout) as resp:
					resp.raise_for_status()
					with open(temp_path, "wb") as dest:
						for data in resp.iter_content(chunk_size=max(1024 * 128, chunk_size)):
							if not data:
								continue
							dest.write(data)
							progress.update(len(data))

				os.replace(temp_path, output_file)
				return
			except Exception as exc:
				if os.path.exists(temp_path):
					os.remove(temp_path)
				progress.downloaded = 0
				if attempt == max_retries:
					raise RuntimeError(
						f"Sequential download failed after {max_retries} attempts",
					) from exc
				backoff = 2 ** (attempt - 1)
				time.sleep(backoff)
	finally:
		progress.close()


def build_argument_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("url", help="Direct URL to the video or large file")
	parser.add_argument(
		"-o",
		"--output",
		default=None,
		help="Destination file name. Defaults to the basename of the URL",
	)
	parser.add_argument(
		"-c",
		"--chunk-size",
		type=int,
		default=1_048_576,
		help="Chunk size in bytes (default: 1 MiB)",
	)
	parser.add_argument(
		"-w",
		"--workers",
		type=int,
		default=os.cpu_count() or 4,
		help="Number of parallel download workers",
	)
	parser.add_argument(
		"--max-retries",
		type=int,
		default=5,
		help="Maximum retry attempts per chunk",
	)
	parser.add_argument(
		"--file-size",
		type=int,
		default=None,
		help="Override total file size in bytes when the server hides it",
	)
	parser.add_argument(
		"-q",
		"--quality",
		help="Preferred quality (e.g., 1080, 720, best). Prompts if omitted.",
	)
	return parser


def main(argv: Optional[List[str]] = None) -> None:
	parser = build_argument_parser()
	args = parser.parse_args(argv)

	url: str = args.url
	output_file: str = args.output or os.path.basename(url.split("?")[0]) or "download.bin"
	chunk_size: int = max(1, args.chunk_size)
	workers: int = max(1, args.workers)
	max_retries: int = max(1, args.max_retries)
	manual_size: Optional[int] = args.file_size if args.file_size and args.file_size > 0 else None
	manual_size_source: Optional[str] = "cli override" if manual_size is not None else None
	requested_quality: Optional[str] = args.quality

	os.makedirs(os.path.dirname(os.path.abspath(output_file)) or ".", exist_ok=True)

	selection = gather_format_selection(url, requested_quality)
	selected_option: Optional[FormatOption] = None
	selected_info: Optional[dict] = None
	if selection is not None:
		selected_option, selected_info = selection
		url = selected_option.url
		if manual_size is None and selected_option.filesize:
			manual_size = selected_option.filesize
			manual_size_source = "extractor metadata"
		if args.output is None:
			title = selected_info.get("title") if selected_info else None
			if title:
				output_file = f"{sanitize_filename(title)}.{selected_option.ext}"
		if selected_info:
			headers = selected_info.get("http_headers") or {}
			format_headers = selected_option.http_headers or {}
			merged_headers = {**headers, **format_headers}
			print("Applying headers from extractor")
		else:
			merged_headers = selected_option.http_headers or {}
	else:
		merged_headers = {}

	if selected_option is not None:
		resolution = f"{selected_option.height}p" if selected_option.height else selected_option.label
		print(f"Selected quality: {resolution} ({selected_option.ext})")

	session = requests.Session()
	if merged_headers:
		session.headers.update(merged_headers)
	progress: Optional[ProgressTracker] = None
	temp_dir: Optional[str] = None
	part_paths: List[str] = []
	try:
		if manual_size is not None:
			total_size = manual_size
			source = manual_size_source or "override"
			print(f"Using {source} for file size")
		else:
			try:
				total_size = get_file_size(url, session=session)
			except RuntimeError as err:
				if manual_size is not None:
					total_size = manual_size
					print("Server did not expose size; using manual override")
				else:
					print("Server did not expose size; falling back to single-stream download")
					download_without_known_size(
						url,
						output_file,
						session,
						chunk_size,
						max_retries,
					)
					return

		print(f"Total size: {total_size:,} bytes")
		chunks = build_chunks(total_size, chunk_size)
		print(f"Downloading in {len(chunks)} chunks using {workers} workers...")

		progress = ProgressTracker(total_size)
		temp_dir = tempfile.mkdtemp(prefix="video_parts_")
		part_paths = [os.path.join(temp_dir, chunk.filename) for chunk in chunks]

		def session_factory() -> requests.Session:
			sess = requests.Session()
			sess.headers.update({"User-Agent": session.headers.get("User-Agent", "Mozilla/5.0")})
			sess.headers.update(merged_headers)
			return sess

		with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
			futures = {
				executor.submit(
					download_chunk,
					url,
					chunk,
					temp_dir,
					session_factory,
					progress,
					max_retries,
				): chunk
				for chunk in chunks
			}

			for future in concurrent.futures.as_completed(futures):
				chunk = futures[future]
				try:
					future.result()
				except Exception as exc:
					raise RuntimeError(f"Chunk {chunk.part_number} failed: {exc}") from exc
	except Exception:
		if part_paths:
			delete_files(part_paths)
		if temp_dir and os.path.isdir(temp_dir):
			try:
				os.rmdir(temp_dir)
			except OSError:
				pass
		raise
	finally:
		if progress is not None:
			progress.close()
		session.close()

	if not part_paths:
		print(f"Download complete: {output_file}")
		return

	print("Merging parts...")
	merge_files(part_paths, output_file)
	delete_files(part_paths)
	if temp_dir and os.path.isdir(temp_dir):
		try:
			os.rmdir(temp_dir)
		except OSError:
			pass
	print(f"Download complete: {output_file}")


if __name__ == "__main__":
	main()
