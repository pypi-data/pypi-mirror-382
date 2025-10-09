modfile (hee888)
===================

Fast multi-threaded video downloader and utilities.

This project provides a small CLI and helpers for high-speed multi-threaded downloads using HTTP range requests. The package is distributed under the name `modfile` while the Python package code remains in the `hee888` package directory.

Features
- Multi-threaded chunked downloader with retries and progress tracking
- Helpers to create configured `requests.Session` instances and `PreparedRequest` objects
- Optional `yt-dlp` integration to select video formats

Quick usage
-----------
After installing the package you can use the `modfile` console script:

PowerShell:

```powershell
modfile "https://example.com/video.mp4" -o myvideo.mp4
```

Use helpers from Python:

```python
from hee888 import app
sess = app.make_session({"X-Custom": "value"})
preq = app.create_prepared_request("https://httpbin.org/get")
resp = sess.send(preq)
print(resp.status_code)
```

Building and publishing to PyPI (step-by-step)
---------------------------------------------
1) Prepare an account and API token
   - Create an account on https://pypi.org if you don't have one.
   - Create an API token on your account settings page ("API tokens") and copy it.

2) Install build and twine

PowerShell:

```powershell
python -m pip install --upgrade pip
python -m pip install --upgrade build twine
```

3) Ensure `README.md` exists (setup.py reads it). If you edited `setup.py` to reference a README, make sure the file path is correct.

4) Bump the version in `setup.py` (e.g., `version='0.1.1'`) for each new release.

5) Build distributions

PowerShell:

```powershell
# from project root (where setup.py / pyproject.toml live)
python -m build
```

This will produce files under `dist/` (a source tarball and a wheel).

6) Test upload to Test PyPI (recommended)
   - Create an API token scoped to Test PyPI at https://test.pypi.org if you'd like to test.

PowerShell (recommended: use environment variables for the token):

```powershell
# provide credentials via environment variables
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "<your-pypi-token-here>"
python -m twine upload --repository testpypi dist/*
```

Install from Test PyPI to verify:

```powershell
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps modfile
```

7) Publish to production PyPI

PowerShell:

```powershell
# set the real token
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "<your-pypi-token-here>"
python -m twine upload dist/*
```

8) Post-release housekeeping (optional but recommended)
   - Tag in git, push tags, create a GitHub release that references the PyPI release:

```powershell
git add .
git commit -m "Release v0.1.1"
git tag v0.1.1
git push && git push --tags
```

Troubleshooting
---------------
- If `python setup.py sdist bdist_wheel` fails with a FileNotFoundError for `README.md`, make sure `README.md` exists. This repo now includes `README.md`.
- If `yt-dlp` import fails when importing `hee888.app`, install dependencies first: `python -m pip install -r requirements.txt` or `python -m pip install requests tqdm yt-dlp`.
- Use Test PyPI first to verify packaging and installability.

Security note
-------------
- Use PyPI API tokens (not your username/password) and treat tokens like secrets. Do not commit tokens into source control. Use CI secrets for automated publishing.

License & author
----------------
Author: Khumi

(Adjust license metadata in `setup.py` as needed.)
