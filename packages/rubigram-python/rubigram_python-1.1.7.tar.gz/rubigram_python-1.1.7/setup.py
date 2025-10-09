from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="rubigram-python",
    version="1.1.7",
    description="A fast and flexible rubika automation library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="stone",
    author_email="kissme.cloud@example.com",
    url="https://github.com/yourusername/rubigram",
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'pycryptodome',
        'aiofiles',
        'markdownify',
        'mutagen'
    ],
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)