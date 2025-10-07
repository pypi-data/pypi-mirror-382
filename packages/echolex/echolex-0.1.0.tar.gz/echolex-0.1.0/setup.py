#!/usr/bin/env python3
"""Setup configuration for EchoLex package."""

import os
from pathlib import Path

from setuptools import setup

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Get email from environment variable or use placeholder
AUTHOR_EMAIL = os.getenv("ECHOLEX_AUTHOR_EMAIL", "author@example.com")

setup(
    name="echolex",
    version="0.1.0",
    author="Ramon Figueiredo",
    author_email=AUTHOR_EMAIL,
    description="A CLI tool for audio transcription using OpenAI's Whisper model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ramonfigueiredo/echolex",
    project_urls={
        "Bug Tracker": "https://github.com/ramonfigueiredo/echolex/issues",
        "Documentation": "https://github.com/ramonfigueiredo/echolex#readme",
        "Source Code": "https://github.com/ramonfigueiredo/echolex",
    },
    py_modules=["echolex"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai-whisper",
        "ffmpeg-python>=0.2.0",
        "certifi",
        "torch>=2.0.0",
        "tqdm",
        "numpy>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "echolex=echolex:main",
        ],
    },
    keywords=[
        "whisper",
        "audio",
        "transcription",
        "speech-to-text",
        "stt",
        "openai",
        "ai",
        "machine-learning",
        "cli",
    ],
    include_package_data=True,
    zip_safe=False,
)
