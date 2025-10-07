#!/usr/bin/env python3
"""
EchoLex - Audio Transcription CLI Tool
A unified tool for transcribing audio files using OpenAI's Whisper model.
"""

import argparse
import os
import sys
import ssl
import glob
import subprocess
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# Read version from VERSION.in file
try:
    version_file = Path(__file__).parent / "VERSION.in"
    __version__ = version_file.read_text().strip()
except FileNotFoundError:
    __version__ = "unknown"  # Fallback version

# SSL certificate handling
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    ssl._create_default_https_context = ssl._create_unverified_context
except ImportError:
    pass  # certifi not available, continue without SSL fixes

# Import whisper with auto-install fallback
try:
    import whisper
except ImportError:
    print("Whisper not found. Installing openai-whisper...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "openai-whisper"])
    import whisper

# Import ffmpeg with helpful error message
try:
    import ffmpeg
except ImportError:
    ffmpeg = None


class AudioProcessor:
    """Handles audio file processing and analysis."""

    @staticmethod
    def check_dependencies():
        """Check if required dependencies are installed."""
        dependencies = {
            "ffmpeg": "FFmpeg is required for audio processing",
            "ffprobe": "FFprobe is required for audio analysis"
        }

        missing = []
        for cmd, description in dependencies.items():
            try:
                subprocess.run([cmd, "-version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing.append(f"{cmd}: {description}")

        if missing:
            print("Missing dependencies:")
            for dep in missing:
                print(f"  - {dep}")
            print("\nInstall on macOS: brew install ffmpeg")
            print("Install on Ubuntu: sudo apt-get install ffmpeg")
            return False
        return True

    @staticmethod
    def get_audio_info(audio_path):
        """Extract audio file information using ffprobe."""
        if ffmpeg is None:
            return {"error": "ffmpeg-python not installed"}

        try:
            probe = ffmpeg.probe(audio_path)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)

            if audio_stream:
                duration = float(probe['format']['duration'])
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                seconds = int(duration % 60)

                info = {
                    "filename": os.path.basename(audio_path),
                    "format": probe['format']['format_name'],
                    "duration": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
                    "duration_seconds": duration,
                    "codec": audio_stream['codec_name'],
                    "sample_rate": audio_stream.get('sample_rate', 'Unknown'),
                    "channels": audio_stream.get('channels', 'Unknown'),
                    "bitrate": probe['format'].get('bit_rate', 'Unknown'),
                    "size_mb": os.path.getsize(audio_path) / (1024 * 1024)
                }
                return info
        except Exception as e:
            return {"error": str(e)}


class AudioTranscriber:
    """Handles audio transcription using Whisper."""

    def __init__(self, model_size="base", device=None):
        print(f"Loading Whisper {model_size} model...")
        self.model = whisper.load_model(model_size, device=device)
        print("Model loaded successfully!")

    def transcribe(self, audio_path, language=None, verbose=True):
        """Transcribe an audio file."""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        file_size = os.path.getsize(audio_path) / (1024 * 1024)  # Size in MB
        print(f"Processing: {audio_path} ({file_size:.2f} MB)")

        options = {
            "language": language,
            "verbose": verbose,
            "fp16": False  # Disable FP16 for better compatibility
        }

        print("Starting transcription... (this may take a few minutes)")
        result = self.model.transcribe(audio_path, **options)

        return result

    def save_results(self, result, audio_path, output_formats=None, output_dir=None, summary_provider=None,
                     summary_config=None):
        """Save transcription results in various formats."""
        if output_formats is None:
            output_formats = ["txt", "json", "srt"]

        base_name = Path(audio_path).stem

        if output_dir is None:
            output_dir = Path("transcripts")
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(exist_ok=True)

        outputs = {}

        # Generate summary if requested
        summary = None
        if summary_provider:
            if summary_config is None:
                summary_config = {}

            try:
                if summary_provider == "chatgpt":
                    summary = self.summarize_with_chatgpt(result["text"], **summary_config)
                elif summary_provider == "gemini":
                    summary = self.summarize_with_gemini(result["text"], **summary_config)
                print(f"[OK] Summary generated with {summary_provider}")
            except Exception as e:
                print(f"[WARNING] Failed to generate summary: {str(e)}")

        if "txt" in output_formats:
            txt_path = output_dir / f"{base_name}_transcript.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(result["text"])
            outputs["txt"] = str(txt_path)
            print(f"[OK] Text transcript saved to: {txt_path}")

            # Save summary to separate file if generated
            if summary:
                summary_path = output_dir / f"{base_name}_summary.txt"
                with open(summary_path, "w", encoding="utf-8") as f:
                    f.write(summary)
                outputs["summary"] = str(summary_path)
                print(f"[OK] Summary saved to: {summary_path}")

                # Save summary details to JSON file
                summary_json_path = output_dir / f"{base_name}_summary.json"
                summary_details = {
                    "summary": summary,
                    "provider": summary_provider,
                    "parameters": summary_config if summary_config else {},
                    "generated_at": datetime.now().isoformat()
                }
                with open(summary_json_path, "w", encoding="utf-8") as f:
                    json.dump(summary_details, f, indent=2, ensure_ascii=False)
                outputs["summary_json"] = str(summary_json_path)
                print(f"[OK] Summary details saved to: {summary_json_path}")

        if "json" in output_formats:
            json_path = output_dir / f"{base_name}_transcript.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json_data = {
                    "text": result["text"],
                    "segments": result["segments"],
                    "language": result.get("language", "unknown"),
                    "transcribed_at": datetime.now().isoformat(),
                    "audio_file": str(audio_path)
                }
                if summary:
                    json_data["summary"] = summary
                    json_data["summary_provider"] = summary_provider
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            outputs["json"] = str(json_path)
            print(f"[OK] JSON transcript saved to: {json_path}")

        if "srt" in output_formats:
            srt_path = output_dir / f"{base_name}_transcript.srt"
            with open(srt_path, "w", encoding="utf-8") as f:
                for i, segment in enumerate(result["segments"], 1):
                    f.write(f"{i}\n")
                    f.write(f"{self._format_timestamp(segment['start'])} --> {self._format_timestamp(segment['end'])}\n")
                    f.write(f"{segment['text'].strip()}\n\n")
            outputs["srt"] = str(srt_path)
            print(f"[OK] SRT subtitles saved to: {srt_path}")

        return outputs, summary

    def _format_timestamp(self, seconds):
        """Format seconds to SRT timestamp format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ",")

    def summarize_with_chatgpt(self, text, api_key=None, model="gpt-4o-mini",
                               system_message="You are a helpful assistant that creates concise summaries of transcripts.",
                               user_message="Please provide a concise summary of the following transcript:\n\n{text}",
                               temperature=0.7, max_tokens=500):
        """Summarize transcript using ChatGPT (OpenAI)."""
        try:
            import openai
        except ImportError:
            raise ImportError(
                "OpenAI library not installed. Install with: pip install openai\n"
                "Or install with summarization support: pip install echolex[summarize]"
            )

        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass api_key parameter."
                )

        client = openai.OpenAI(api_key=api_key)

        print(f"Generating summary with ChatGPT (model: {model})...")

        # Format user message with transcript
        formatted_user_message = user_message.replace("{text}", text)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": formatted_user_message}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        summary = response.choices[0].message.content.strip()
        return summary

    def summarize_with_gemini(self, text, api_key=None, model="gemini-1.5-flash",
                              system_message="You are a helpful assistant that creates concise summaries of transcripts.",
                              user_message="Please provide a concise summary of the following transcript:\n\n{text}",
                              temperature=0.7, max_tokens=500):
        """Summarize transcript using Google Gemini."""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "Google Generative AI library not installed. Install with: pip install google-generativeai\n"
                "Or install with summarization support: pip install echolex[summarize]"
            )

        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "Gemini API key not found. Set GEMINI_API_KEY environment variable or pass api_key parameter."
                )

        # Suppress gRPC/ALTS warnings
        os.environ['GRPC_VERBOSITY'] = 'ERROR'
        os.environ['GLOG_minloglevel'] = '2'

        genai.configure(api_key=api_key)

        # List available models and try them
        try:
            # If user specified a model, use it; otherwise use default with fallbacks
            if model and model != "gemini-1.5-flash":
                available_models = [model]
                print(f"Generating summary with Gemini (model: {model})...")
            else:
                print(f"Generating summary with Gemini (model: {model})...")
                # Try default model first, then fallbacks
                available_models = [
                    model,  # Default: gemini-1.5-flash
                    'gemini-1.5-pro',
                    'gemini-pro',
                ]

            # Format prompt with system and user messages
            formatted_user_message = user_message.replace("{text}", text)
            prompt = f"{system_message}\n\n{formatted_user_message}"

            generation_config = {
                'temperature': temperature,
                'max_output_tokens': max_tokens,
            }

            # Try each available model
            last_error = None
            for model_name in available_models:
                try:
                    gemini_model = genai.GenerativeModel(model_name)

                    response = gemini_model.generate_content(
                        prompt,
                        generation_config=generation_config
                    )

                    summary = response.text.strip()
                    return summary
                except Exception as e:
                    last_error = e
                    continue

            # If all models failed, raise the last error
            if last_error:
                raise last_error
            else:
                raise Exception("No Gemini models available")

        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")


def find_audio_file(file_path):
    """Find audio file in current directory or audio_files/ directory."""
    audio_path = Path(file_path)
    if audio_path.exists():
        return audio_path

    # Try in audio_files directory
    audio_files_path = Path("audio_files") / audio_path.name
    if audio_files_path.exists():
        return audio_files_path

    # Not found
    print(f"Error: Audio file not found: {file_path}")
    print(f"Also checked: {audio_files_path}")
    sys.exit(1)


def cmd_transcribe(args):
    """Transcribe a single audio file."""
    audio_path = find_audio_file(args.audio_file)

    try:
        transcriber = AudioTranscriber(model_size=args.model, device=args.device)

        result = transcriber.transcribe(
            str(audio_path),
            language=args.language,
            verbose=args.verbose
        )

        # Build summary configuration
        summary_config = {}
        if hasattr(args, 'summary_model') and args.summary_model:
            summary_config['model'] = args.summary_model
        if hasattr(args, 'summary_system_message'):
            summary_config['system_message'] = args.summary_system_message
        if hasattr(args, 'summary_user_message'):
            summary_config['user_message'] = args.summary_user_message
        if hasattr(args, 'summary_temperature'):
            summary_config['temperature'] = args.summary_temperature
        if hasattr(args, 'summary_max_tokens'):
            summary_config['max_tokens'] = args.summary_max_tokens

        outputs, summary = transcriber.save_results(
            result,
            str(audio_path),
            args.output,
            args.output_dir,
            summary_provider=args.summarize if hasattr(args, 'summarize') else None,
            summary_config=summary_config if summary_config else None
        )

        print("\n" + "="*50)
        print("[DONE] Transcription completed successfully!")
        print("="*50)

        if not args.quiet:
            if summary:
                print("\nSummary:")
                print("-"*50)
                print(summary)
                print("-"*50)

            print("\nTranscript preview (first 500 characters):")
            print("-"*50)
            print(result["text"][:500] + "..." if len(result["text"]) > 500 else result["text"])

    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)


def cmd_batch(args):
    """Batch transcribe multiple audio files."""
    audio_files = []
    for pattern in args.patterns:
        # Check both in current directory and audio_files directory
        audio_files.extend(glob.glob(pattern))
        audio_files.extend(glob.glob(str(Path("audio_files") / pattern)))

    if not audio_files:
        print("No audio files found matching the patterns.")
        print("Checked in current directory and audio_files/ directory")
        return

    audio_files = list(set(audio_files))  # Remove duplicates
    print(f"Found {len(audio_files)} audio file(s) to process:")
    for f in audio_files:
        print(f"  - {f}")

    transcriber = AudioTranscriber(model_size=args.model)
    processor = AudioProcessor()

    # Build summary configuration
    summary_config = {}
    if hasattr(args, 'summary_model') and args.summary_model:
        summary_config['model'] = args.summary_model
    if hasattr(args, 'summary_system_message'):
        summary_config['system_message'] = args.summary_system_message
    if hasattr(args, 'summary_user_message'):
        summary_config['user_message'] = args.summary_user_message
    if hasattr(args, 'summary_temperature'):
        summary_config['temperature'] = args.summary_temperature
    if hasattr(args, 'summary_max_tokens'):
        summary_config['max_tokens'] = args.summary_max_tokens

    results = []
    failed = []

    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] Processing: {audio_file}")
        print("-" * 50)

        try:
            info = processor.get_audio_info(audio_file)
            if "error" not in info:
                print(f"Duration: {info['duration']} | Format: {info['format']} | Size: {info['size_mb']:.2f} MB")

            result = transcriber.transcribe(audio_file, verbose=args.verbose)

            outputs, summary = transcriber.save_results(
                result,
                audio_file,
                args.output,
                args.output_dir,
                summary_provider=args.summarize if hasattr(args, 'summarize') else None,
                summary_config=summary_config if summary_config else None
            )

            result_data = {
                "file": audio_file,
                "status": "success",
                "outputs": outputs,
                "word_count": len(result["text"].split()),
                "duration": info.get("duration", "Unknown")
            }
            if summary:
                result_data["summary"] = summary
            results.append(result_data)

        except Exception as e:
            print(f"[ERROR] Failed to process {audio_file}: {str(e)}")
            failed.append({
                "file": audio_file,
                "error": str(e)
            })

    # Save summary
    output_path = Path(args.output_dir)
    output_path.mkdir(exist_ok=True)

    summary_file = output_path / "batch_transcription_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "processed_at": datetime.now().isoformat(),
            "model": args.model,
            "total_files": len(audio_files),
            "successful": len(results),
            "failed": len(failed),
            "results": results,
            "errors": failed
        }, f, indent=2)

    print("\n" + "="*50)
    print("Batch Processing Complete!")
    print(f"Successfully processed: {len(results)}/{len(audio_files)} files")
    if failed:
        print(f"Failed: {len(failed)} files")
    print(f"Summary saved to: {summary_file}")
    print("="*50)


def cmd_info(args):
    """Display audio file information."""
    audio_path = find_audio_file(args.audio_file)

    processor = AudioProcessor()

    if not processor.check_dependencies():
        sys.exit(1)

    print("\nAudio File Information:")
    print("-" * 50)
    info = processor.get_audio_info(str(audio_path))

    if "error" in info:
        print(f"Error: {info['error']}")
    else:
        for key, value in info.items():
            print(f"{key.replace('_', ' ').title()}: {value}")


def cmd_check(args):
    """Check system dependencies."""
    processor = AudioProcessor()

    print("Checking system dependencies...")
    print("-" * 50)

    # Check ffmpeg
    if processor.check_dependencies():
        print("✓ FFmpeg is installed")
    else:
        print("✗ FFmpeg is not installed")

    # Check Python packages
    packages = {
        "whisper": "openai-whisper",
        "ffmpeg": "ffmpeg-python",
        "certifi": "certifi"
    }

    print("\nPython packages:")
    for module, package in packages.items():
        try:
            __import__(module)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is not installed")

    print("-" * 50)
    print("\nIf any dependencies are missing, run:")
    print("  pip install -r requirements.txt")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="echolex",
        description="Audio transcription tool using OpenAI Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transcribe a single file
  echolex transcribe audio.m4a

  # Transcribe with specific model
  echolex transcribe audio.m4a --model medium

  # Transcribe with ChatGPT summary
  echolex transcribe audio.m4a --summarize chatgpt
  echolex transcribe audio.m4a -s chatgpt

  # Transcribe with Gemini summary
  echolex transcribe audio.m4a --summarize gemini
  echolex transcribe audio.m4a -s gemini

  # Custom summarization settings
  echolex transcribe audio.m4a -s chatgpt --summary-model gpt-4o --summary-max-tokens 1000

  # Batch transcribe multiple files
  echolex batch *.m4a *.mp3

  # Batch transcribe with summaries
  echolex batch *.m4a --summarize chatgpt
  echolex batch *.m4a --summarize gemini

  # Get audio file information
  echolex info audio.m4a

  # Check dependencies
  echolex check
        """
    )

    # Add version argument
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Transcribe command
    parser_transcribe = subparsers.add_parser("transcribe", help="Transcribe a single audio file")
    parser_transcribe.add_argument("audio_file", help="Path to the audio file")
    parser_transcribe.add_argument("--model", default="base",
                                   choices=["tiny", "base", "small", "medium", "large"],
                                   help="Whisper model size (default: base)")
    parser_transcribe.add_argument("--language", default=None,
                                   help="Language code (e.g., 'en', 'es')")
    parser_transcribe.add_argument("--output", nargs="+", default=["txt", "json", "srt"],
                                   choices=["txt", "json", "srt"],
                                   help="Output formats (default: txt json srt)")
    parser_transcribe.add_argument("--output-dir", default="transcripts",
                                   help="Output directory (default: transcripts)")
    parser_transcribe.add_argument("--device", default=None,
                                   help="Device to use (cuda, cpu, or None for auto)")
    parser_transcribe.add_argument("--verbose", action="store_true",
                                   help="Show verbose output during transcription")
    parser_transcribe.add_argument("--quiet", action="store_true",
                                   help="Don't show transcript preview")
    parser_transcribe.add_argument("-s", "--summarize",
                                   choices=["chatgpt", "gemini"],
                                   help="Generate summary using ChatGPT or Gemini")
    parser_transcribe.add_argument("--summary-model",
                                   help="AI model for summarization (default: gpt-4o-mini for ChatGPT, gemini-1.5-flash for Gemini)")
    parser_transcribe.add_argument("--summary-system-message",
                                   default="You are a helpful assistant that creates concise summaries of transcripts.",
                                   help="System message for AI summarization (default: 'You are a helpful assistant that creates concise summaries of transcripts.')")
    parser_transcribe.add_argument("--summary-user-message",
                                   default="Please provide a concise summary of the following transcript:\n\n{text}",
                                   help="User message template for AI summarization (use {text} for transcript)")
    parser_transcribe.add_argument("--summary-temperature", type=float, default=0.7,
                                   help="Temperature for AI summarization (default: 0.7)")
    parser_transcribe.add_argument("--summary-max-tokens", type=int, default=500,
                                   help="Maximum tokens for AI summary (default: 500)")
    parser_transcribe.set_defaults(func=cmd_transcribe)

    # Batch command
    parser_batch = subparsers.add_parser("batch", help="Batch transcribe multiple audio files")
    parser_batch.add_argument("patterns", nargs="+", help="File patterns (e.g., *.m4a)")
    parser_batch.add_argument("--model", default="base",
                              choices=["tiny", "base", "small", "medium", "large"],
                              help="Whisper model size (default: base)")
    parser_batch.add_argument("--output", nargs="+", default=["txt", "json"],
                              choices=["txt", "json", "srt"],
                              help="Output formats (default: txt json)")
    parser_batch.add_argument("--output-dir", default="transcripts",
                              help="Output directory (default: transcripts)")
    parser_batch.add_argument("--verbose", action="store_true",
                              help="Show verbose output during transcription")
    parser_batch.add_argument("-s", "--summarize",
                              choices=["chatgpt", "gemini"],
                              help="Generate summaries using ChatGPT or Gemini")
    parser_batch.add_argument("--summary-model",
                              help="AI model for summarization (default: gpt-4o-mini for ChatGPT, gemini-1.5-flash for Gemini)")
    parser_batch.add_argument("--summary-system-message",
                              default="You are a helpful assistant that creates concise summaries of transcripts.",
                              help="System message for AI summarization (default: 'You are a helpful assistant that creates concise summaries of transcripts.')")
    parser_batch.add_argument("--summary-user-message",
                              default="Please provide a concise summary of the following transcript:\n\n{text}",
                              help="User message template for AI summarization (use {text} for transcript)")
    parser_batch.add_argument("--summary-temperature", type=float, default=0.7,
                              help="Temperature for AI summarization (default: 0.7)")
    parser_batch.add_argument("--summary-max-tokens", type=int, default=500,
                              help="Maximum tokens for AI summary (default: 500)")
    parser_batch.set_defaults(func=cmd_batch)

    # Info command
    parser_info = subparsers.add_parser("info", help="Display audio file information")
    parser_info.add_argument("audio_file", help="Path to the audio file")
    parser_info.set_defaults(func=cmd_info)

    # Check command
    parser_check = subparsers.add_parser("check", help="Check system dependencies")
    parser_check.set_defaults(func=cmd_check)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
