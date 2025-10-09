from setuptools import setup, find_packages

setup(
    name='hee888',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'tqdm',
        'yt-dlp'
    ],
    entry_points={
        'console_scripts': [
            'modfile = hee888.app:main'
        ]
    },
    python_requires='>=3.8',
    author='Khumi',
    description='Fast multi-threaded video downloader',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
