from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quillai-filescanner",
    version="1.0.5",
    author="Quillai Mohammed Eise Mohammed",
    author_email="quillai20011114@gmail.com",
    description="A comprehensive file system scanner for organizing and analyzing files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/quillaiMohammed/filescanner-",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "filescanner=quillai_filescanner.cli:main",
        ],
    },
    include_package_data=True,
)
