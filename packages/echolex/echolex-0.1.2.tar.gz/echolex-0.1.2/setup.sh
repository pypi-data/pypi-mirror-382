#!/bin/bash

echo "Setting up Audio Transcription Tool..."
echo "========================================"

# Upgrade pip and setuptools
echo "1. Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install certifi first
echo "2. Installing certifi..."
pip install certifi

# Install numpy
echo "3. Installing numpy..."
pip install numpy

# Install other dependencies
echo "4. Installing other dependencies..."
pip install ffmpeg-python tqdm

# Install torch (CPU version for macOS)
echo "5. Installing PyTorch..."
pip install torch torchvision torchaudio

# Install whisper last
echo "6. Installing Whisper..."
pip install openai-whisper

echo ""
echo "========================================"
echo "Installation complete!"
