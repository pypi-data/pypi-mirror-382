# setup.py
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="shelldog",
    version="0.1.0",
    author="Ansuman Bhujabala",
    author_email="ansumanbhujabala@gmail.com",
    description="🐕 Your loyal companion for tracking shell commands - silent, smart, and adorable!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ansumanbhujabal/shelldog",
    project_urls={
        "Bug Tracker": "https://github.com/Ansumanbhujabal/shelldog/issues",
        "Documentation": "https://github.com/Ansumanbhujabal/shelldog/blob/main/README.md",
        "Source Code": "https://github.com/Ansumanbhujabal/shelldog",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Environment :: Console",
    ],
    keywords="shell, terminal, command, history, tracking, logger, development, cli, bash, zsh",
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "shelldog=shelldog.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)