from setuptools import setup, find_packages

setup(
    name="rubigram-python",
    version="1.1.5",
    description="A fast and flexible rubika automation library",
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