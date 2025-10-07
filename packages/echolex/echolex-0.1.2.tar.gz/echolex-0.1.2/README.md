<p align="center">
  <img src="images/echolex_log.png" alt="EchoLex Logo" width="250">
</p>

[![PyPI version](https://badge.fury.io/py/echolex.svg)](https://badge.fury.io/py/echolex)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

EchoLex is a CLI tool for audio transcription using OpenAI's Whisper model for speech-to-text conversion.

The name “EchoLex” combines “Echo” — the voice or sound we capture — with “Lex,” drawn from lexicon, meaning words or language. 
Together, EchoLex reflects the tool’s purpose: transforming spoken echoes into written words with accuracy and clarity.

## Features

- Transcribe single audio files or batch process multiple files
- Support for multiple audio formats (m4a, mp3, wav, flac, ogg, etc.)
- Multiple output formats: plain text, JSON with timestamps, and SRT subtitles
- AI-powered summarization with ChatGPT or Google Gemini
- Audio file information extraction
- Configurable Whisper model sizes (tiny, base, small, medium, large)
- Automatic audio file detection in `audio_files/` directory
- Organized output in `transcripts/` directory
- Built-in dependency checking
- SSL certificate handling for model downloads

## Installation

### Prerequisites
- Python 3.8+ (3.12 recommended)
- FFmpeg for audio processing:
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Install from PyPI (Recommended)

```bash
# Install EchoLex
pip install echolex

# Install with summarization support (ChatGPT/Gemini)
pip install echolex[summarize]

# Verify installation
echolex --help
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/ramonfigueiredo/echolex.git
cd echolex

# Option 1: Quick setup script
chmod +x setup.sh
./setup.sh

# Option 2: Manual installation
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Troubleshooting Installation Issues

If you encounter installation errors:

1. **For virtual environments:**
```bash
# Install packages one by one
pip install --upgrade pip setuptools wheel
pip install certifi
pip install ffmpeg-python
pip install openai-whisper
```

2. **Use the simplified script (no certifi required):**
```bash
python transcribe_simple.py audio_file.m4a
```

## Project Structure

```
echolex/
├── audio_files/              # Place your audio files here
├── transcripts/              # Transcribed files will be saved here
├── echolex.py                # EchoLex CLI tool
├── test_echolex.py           # Unit tests
├── setup.sh                  # Automated setup script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Quick Start Tutorial

### 1. Install EchoLex

```bash
# Install from PyPI
pip install echolex

# Or install with AI summarization support
pip install echolex[summarize]

# Verify installation
echolex --version
```

### 2. Install FFmpeg (Required)

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows: Download from https://ffmpeg.org/download.html
```

### 3. Transcribe Your First Audio File

```bash
# Transcribe a single file
echolex transcribe meeting.m4a

# The transcript will be saved to transcripts/audio_transcript.txt
```

### 4. Try Different Options

```bash
# Use a larger model for better accuracy
echolex transcribe meeting.m4a --model medium

# Generate multiple output formats
echolex transcribe meeting.m4a --output txt json srt

# Get audio file information
echolex info meeting.m4a
```

### 5. AI-Powered Summarization (Optional)

```bash
# Install summarization support if not already installed
pip install echolex[summarize]

# Set up your API key
export OPENAI_API_KEY="your-api-key-here"

# Transcribe and summarize with ChatGPT
echolex transcribe meeting.m4a --summarize chatgpt

# Or use Google Gemini
export GEMINI_API_KEY="your-api-key-here"
echolex transcribe meeting.m4a --summarize gemini
```

### 6. Batch Process Multiple Files

```bash
# Create audio_files directory
mkdir -p audio_files

# Copy your audio files
cp *.m4a audio_files/

# Process all files at once
echolex batch audio_files/*.m4a

# With summarization
echolex batch audio_files/*.m4a --summarize chatgpt
```

## Usage

### Getting Help

```bash
# Show main help
echolex --help
echolex -h

# Show version
echolex --version
echolex -v

# Show help for specific command
echolex transcribe --help
echolex batch --help
echolex info --help
echolex check --help
```

**Note:** If you installed from source, use `python echolex.py` instead of `echolex`.

### Commands

EchoLex provides four main commands:

#### 1. Transcribe a Single File

```bash
echolex transcribe audio_file.m4a
```

With specific options:
```bash
echolex transcribe audio_file.m4a --model medium --output txt json srt
```

Specify output directory:
```bash
echolex transcribe audio_file.m4a --output-dir custom_output
```

Available options:
- `--model`: Model size (tiny, base, small, medium, large)
- `--language`: Language code (e.g., 'en', 'es')
- `--output`: Output formats (txt, json, srt)
- `--output-dir`: Output directory
- `--device`: Device to use (cuda, cpu, or None for auto)
- `--verbose`: Show verbose output
- `--quiet`: Don't show transcript preview
- `-s, --summarize`: Generate AI summary (chatgpt or gemini)

#### 2. Batch Process Multiple Files

Process all audio files matching a pattern:
```bash
echolex batch *.m4a *.mp3
```

With custom settings:
```bash
echolex batch *.m4a --model small --output txt json srt --output-dir results
```

Available options:
- `--model`: Model size (tiny, base, small, medium, large)
- `--output`: Output formats (txt, json, srt)
- `--output-dir`: Output directory
- `--verbose`: Show verbose output
- `-s, --summarize`: Generate AI summaries (chatgpt or gemini)

#### 3. Get Audio File Information

Display detailed information about an audio file:
```bash
echolex info audio_file.m4a
```

#### 4. Check Dependencies

Verify that all required dependencies are installed:
```bash
echolex check
```

### Command-Line Help

Every command supports `--help` or `-h` for detailed usage information:

```bash
# Main help menu
echolex --help

# Command-specific help
echolex transcribe -h
echolex batch -h
echolex info -h
echolex check -h
```

**Example help output:**
```
usage: echolex [-h] {transcribe,batch,info,check} ...

Audio transcription tool using OpenAI Whisper

positional arguments:
  {transcribe,batch,info,check}
                        Available commands
    transcribe          Transcribe a single audio file
    batch               Batch transcribe multiple audio files
    info                Display audio file information
    check               Check system dependencies

options:
  -h, --help            show this help message and exit

Examples:
  # Transcribe a single file
  echolex transcribe audio.m4a

  # Transcribe with specific model
  echolex transcribe audio.m4a --model medium

  # Batch transcribe multiple files
  echolex batch *.m4a *.mp3

  # Get audio file information
  echolex info audio.m4a

  # Check dependencies
  echolex check
```

### Model Options

Available models (speed vs accuracy tradeoff):
- `tiny`: Fastest, least accurate (~39 MB)
- `base`: Good balance - default (~74 MB)
- `small`: Better accuracy (~244 MB)
- `medium`: Even better accuracy (~769 MB)
- `large`: Best accuracy, slowest (~1550 MB)

### AI Summarization

EchoLex can generate concise summaries of transcripts using ChatGPT or Google Gemini.

#### Setup

**Install summarization dependencies:**
```bash
pip install echolex[summarize]
```

**Set up API keys:**
```bash
# For ChatGPT (OpenAI)
export OPENAI_API_KEY="your-api-key-here"

# For Gemini (Google)
export GEMINI_API_KEY="your-api-key-here"
```

To make API keys permanent, add them to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Google Gemini: https://makersuite.google.com/app/apikey

#### Usage

**Summarize with ChatGPT:**
```bash
echolex transcribe audio.m4a --summarize chatgpt
# or use short form
echolex transcribe audio.m4a -s chatgpt
```

**Summarize with Gemini:**
```bash
echolex transcribe audio.m4a --summarize gemini
# or use short form
echolex transcribe audio.m4a -s gemini
```

**Batch summarization:**
```bash
echolex batch *.m4a --summarize chatgpt
```

#### Default Models

- **ChatGPT**: `gpt-4o-mini` (fast and cost-effective)
- **Gemini**: `gemini-1.5-flash` (with automatic fallback to `gemini-1.5-pro` and `gemini-pro`)

#### Customization Options

You can customize the summarization with these options:

- `--summary-model`: Specify a different AI model
- `--summary-system-message`: Customize the system prompt
- `--summary-user-message`: Customize the user prompt (use `{text}` for transcript)
- `--summary-temperature`: Control creativity (0.0-2.0, default: 0.7)
- `--summary-max-tokens`: Set maximum summary length (default: 500)

**Examples:**

```bash
# Use GPT-4o with longer summary
echolex transcribe audio.m4a -s chatgpt \
  --summary-model gpt-4o \
  --summary-max-tokens 1000

# Custom prompt for meeting summaries
echolex transcribe meeting.m4a -s chatgpt \
  --summary-system-message "You are an expert meeting summarizer" \
  --summary-user-message "Create action items from this meeting:\n\n{text}"

# More creative summaries with Gemini
echolex transcribe audio.m4a -s gemini \
  --summary-temperature 1.2

# Batch with custom settings
echolex batch *.m4a -s chatgpt \
  --summary-model gpt-4o-mini \
  --summary-max-tokens 800
```

#### Output

Summaries are saved in three ways:
- Separate text file: `*_summary.txt`
- Summary details JSON: `*_summary.json` (includes summary, provider, parameters, and timestamp)
- Included in transcript JSON: `*_transcript.json` (with `summary` and `summary_provider` fields)
- Displayed in console after transcription

## Output Files

All transcripts are saved to the `transcripts/` directory by default. For each audio file, the tool can create:

- `*_transcript.txt`: Plain text transcript
- `*_summary.txt`: AI-generated summary (when using `--summarize`)
- `*_summary.json`: Summary details with provider and parameters (when using `--summarize`)
- `*_transcript.json`: Detailed JSON with timestamps, segments, and metadata
- `*_transcript.srt`: SRT subtitle file for video synchronization

### JSON Output Format
The JSON output includes:
- Complete transcript text
- Timestamped segments
- Detected language
- Processing timestamp
- Source audio file path
- Summary and summary provider (when using `--summarize`)

### Summary JSON Format
The `*_summary.json` file includes:
- **summary**: The generated summary text
- **provider**: The AI provider used (chatgpt or gemini)
- **parameters**: All parameters used for generation:
  - model: The specific AI model (e.g., gpt-4o-mini, gemini-1.5-flash)
  - system_message: The system prompt used
  - user_message: The user prompt template
  - temperature: The temperature setting
  - max_tokens: The maximum token limit
- **generated_at**: ISO timestamp of when the summary was created

## Requirements

- Python 3.8+
- FFmpeg
- 4-8GB RAM (depending on model size)
- Disk space for Whisper models:
  - Tiny: ~39 MB
  - Base: ~74 MB
  - Small: ~244 MB
  - Medium: ~769 MB
  - Large: ~1550 MB

## Performance Notes

- First run will download the selected Whisper model automatically
- Processing time depends on audio length and model size
- Approximate processing speeds on modern CPUs:
  - Tiny: ~10-15x real-time
  - Base: ~5-8x real-time
  - Small: ~3-5x real-time
  - Medium: ~2-3x real-time
  - Large: ~1-2x real-time
- GPU acceleration available with CUDA-enabled PyTorch (significantly faster)

## Troubleshooting

### Common Issues and Solutions

#### 1. SSL Certificate Errors
```bash
# EchoLex includes SSL certificate handling
# If you still get SSL errors, ensure certifi is installed:
pip install certifi
```

#### 2. Virtual Environment Installation Issues
```bash
# If pip install fails in virtual environment:
pip install --upgrade pip setuptools wheel
pip install certifi ffmpeg-python
pip install openai-whisper

# Or create a fresh environment:
deactivate
python3 -m venv venv_new
source venv_new/bin/activate
pip install openai-whisper ffmpeg-python
```

#### 3. Module Import Errors
```bash
# EchoLex will auto-install Whisper if missing
# For other missing modules:
pip install [missing_module_name]
```

#### 4. Missing Audio Files
EchoLex automatically checks for audio files in:
- Current directory
- `audio_files/` folder

#### 5. Memory Issues
- Use smaller models: `--model tiny` or `--model base`
- Process shorter audio segments
- Close other applications to free up RAM

#### 6. FFmpeg Not Found
```bash
# Check dependencies
echolex check

# Install FFmpeg
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt-get install ffmpeg
```

## Example Workflow

### Using PyPI Installation (Recommended)

#### 1. Install and Setup
```bash
# Install EchoLex with summarization support
pip install echolex[summarize]

# Verify installation
echolex --version
echolex check

# Install FFmpeg if needed
brew install ffmpeg  # macOS
```

#### 2. Prepare Audio Files
```bash
# Create directories
mkdir -p audio_files transcripts

# Place your audio files
cp *.m4a audio_files/
```

#### 3. Transcribe
```bash
# Transcribe a file
echolex transcribe meeting.m4a

# With custom options
echolex transcribe meeting.m4a --model medium --output txt json srt

# With AI summary
export OPENAI_API_KEY="your-api-key"
echolex transcribe meeting.m4a -s chatgpt

# Get help
echolex transcribe --help
```

### Using Source Installation

#### 1. First Time Setup
```bash
# Clone the project
git clone https://github.com/ramonfigueiredo/echolex.git
cd echolex

# Run setup (recommended)
chmod +x setup.sh
./setup.sh

# OR create virtual environment manually
python3 -m venv venv
source venv/bin/activate
pip install openai-whisper ffmpeg-python
```

#### 2. Transcribe
```bash
# Use python command when installed from source
python echolex.py transcribe meeting.m4a

# With custom options
python echolex.py transcribe meeting.m4a --model medium --output txt json srt

# Get help
python echolex.py transcribe --help
```

### Review Output (Both Methods)

```bash
# View the transcript
cat transcripts/audio_transcript.txt

# View the AI summary (if generated)
cat transcripts/audio_summary.txt

# Open JSON for detailed segments
open transcripts/audio_transcript.json

# View summary details
cat transcripts/audio_summary.json

# Check processing summary (for batch jobs)
cat transcripts/batch_transcription_summary.json
```

## Testing

EchoLex includes a comprehensive test suite with unit tests covering all functionality.

### Run All Tests

**Using unittest (built-in, no extra dependencies):**
```bash
python3 -m unittest test_echolex -v
```

**Using pytest (enhanced output, requires pytest):**
```bash
# Install pytest (optional)
pip install pytest

# Run tests
pytest test_echolex.py -v

# Run with more detailed output
pytest test_echolex.py -v -s

# Run with coverage (requires pytest-cov)
pip install pytest-cov
pytest test_echolex.py --cov=echolex --cov-report=html
```

### Run Specific Test Classes

**Using unittest:**
```bash
# Test AudioProcessor
python3 -m unittest test_echolex.TestAudioProcessor -v

# Test AudioTranscriber
python3 -m unittest test_echolex.TestAudioTranscriber -v

# Test CLI commands
python3 -m unittest test_echolex.TestCommandTranscribe -v
python3 -m unittest test_echolex.TestCommandBatch -v
```

**Using pytest:**
```bash
# Test by class name
pytest test_echolex.py::TestAudioProcessor -v
pytest test_echolex.py::TestAudioTranscriber -v

# Test by keyword
pytest test_echolex.py -k "AudioProcessor" -v
pytest test_echolex.py -k "batch" -v
```

### Run Individual Tests

**Using unittest:**
```bash
python3 -m unittest test_echolex.TestAudioTranscriber.test_save_results_srt -v
```

**Using pytest:**
```bash
pytest test_echolex.py::TestAudioTranscriber::test_save_results_srt -v
```

### Test Coverage

The test suite includes:
- **AudioProcessor tests** - Dependency checking and audio file analysis
- **AudioTranscriber tests** - Model loading, transcription, and output generation
- **Helper function tests** - File finding and path resolution
- **Command tests** - All CLI commands (transcribe, batch, info, check)
- **Main CLI tests** - Argument parsing and command routing

All tests use mocking to avoid external dependencies and ensure fast, isolated testing.

## Publishing to PyPI

### Prerequisites

1. Install build tools:
```bash
pip install --upgrade build twine
```

2. Set up PyPI credentials in `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PYPI_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

Get tokens at:
- PyPI: https://pypi.org/manage/account/token/
- TestPyPI: https://test.pypi.org/manage/account/token/

### Publish to TestPyPI (for testing)

```bash
# Using the publish script
./pypi_publish.sh test

# Or manually
python3 -m build
python3 -m twine upload --repository testpypi dist/*
```

**Test the installation:**
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple echolex
```

### Publish to Production PyPI

```bash
# Update version in VERSION.in first
echo "0.1.2" > VERSION.in

# Using the publish script (recommended)
./pypi_publish.sh prod

# Or manually
python3 -m build
python3 -m twine check dist/*
python3 -m twine upload dist/*
```

**After publishing:**
```bash
# Create git tag
git tag v0.1.2
git push origin v0.1.2
```

### Publish Script Usage

The `pypi_publish.sh` script automates the entire process:

- **Test mode**: `./pypi_publish.sh test` - Publishes to TestPyPI
- **Production mode**: `./pypi_publish.sh prod` - Publishes to PyPI

The script will:
1. Read version from VERSION.in
2. Clean previous builds
3. Run all tests
4. Build the package
5. Check distribution with twine
6. Upload to the selected repository
7. Display installation and verification instructions

## License

Apache License, Version 2.0