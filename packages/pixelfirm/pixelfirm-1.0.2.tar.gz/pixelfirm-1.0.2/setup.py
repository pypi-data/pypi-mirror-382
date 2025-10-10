from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README.md
this_dir = Path(__file__).parent
long_desc = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="pixelfirm",
    version="1.0.2",  # bumped version
    description="Download latest Google Pixel factory images by codename",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="Android Artisan",
    author_email="romartisan2025@gmail.com",
    url="https://github.com/Android-Artisan/PixelFirm",
    license="GPL-3.0-or-later",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
        "beautifulsoup4",
        "tqdm",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "pixelfirm = pixelfirm.cli:main",  # this creates the command
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
    ],
    python_requires=">=3.7",
)

