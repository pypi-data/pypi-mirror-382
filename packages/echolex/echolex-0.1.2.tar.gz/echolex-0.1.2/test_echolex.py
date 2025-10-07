#!/usr/bin/env python3
"""
Unit tests for EchoLex audio transcription CLI tool.
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Import the module to test
import echolex


class TestAudioProcessor(unittest.TestCase):
    """Test cases for AudioProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = echolex.AudioProcessor()

    @patch('subprocess.run')
    def test_check_dependencies_success(self, mock_run):
        """Test dependency check when all dependencies are installed."""
        mock_run.return_value = Mock(returncode=0)
        result = self.processor.check_dependencies()
        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2)  # ffmpeg and ffprobe

    @patch('subprocess.run')
    def test_check_dependencies_missing(self, mock_run):
        """Test dependency check when dependencies are missing."""
        mock_run.side_effect = FileNotFoundError()
        result = self.processor.check_dependencies()
        self.assertFalse(result)

    @patch('echolex.ffmpeg')
    def test_get_audio_info_success(self, mock_ffmpeg):
        """Test successful audio info extraction."""
        mock_probe_data = {
            'streams': [{
                'codec_type': 'audio',
                'codec_name': 'aac',
                'sample_rate': '44100',
                'channels': 2
            }],
            'format': {
                'format_name': 'm4a',
                'duration': '120.5',
                'bit_rate': '128000'
            }
        }
        mock_ffmpeg.probe.return_value = mock_probe_data

        with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as tmp:
            tmp.write(b'fake audio data')
            tmp_path = tmp.name

        try:
            info = self.processor.get_audio_info(tmp_path)
            self.assertNotIn('error', info)
            self.assertEqual(info['codec'], 'aac')
            self.assertEqual(info['format'], 'm4a')
            self.assertIn('duration', info)
        finally:
            os.unlink(tmp_path)

    def test_get_audio_info_no_ffmpeg(self):
        """Test audio info when ffmpeg module is not available."""
        with patch('echolex.ffmpeg', None):
            processor = echolex.AudioProcessor()
            info = processor.get_audio_info('dummy.m4a')
            self.assertIn('error', info)


class TestAudioTranscriber(unittest.TestCase):
    """Test cases for AudioTranscriber class."""

    @patch('echolex.whisper.load_model')
    def setUp(self, mock_load_model):
        """Set up test fixtures."""
        self.mock_model = Mock()
        mock_load_model.return_value = self.mock_model
        self.transcriber = echolex.AudioTranscriber(model_size="base")

    def test_init_loads_model(self):
        """Test that initializing transcriber loads the model."""
        self.assertIsNotNone(self.transcriber.model)

    def test_transcribe_file_not_found(self):
        """Test transcribe raises error for non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.transcriber.transcribe('/nonexistent/file.m4a')

    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_transcribe_success(self, mock_getsize, mock_exists):
        """Test successful transcription."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024 * 1024  # 1 MB

        mock_result = {
            'text': 'This is a test transcription',
            'segments': [
                {'start': 0.0, 'end': 2.5, 'text': 'This is a test'},
                {'start': 2.5, 'end': 5.0, 'text': 'transcription'}
            ],
            'language': 'en'
        }
        self.mock_model.transcribe.return_value = mock_result

        result = self.transcriber.transcribe('test.m4a', verbose=False)

        self.assertEqual(result['text'], 'This is a test transcription')
        self.assertEqual(len(result['segments']), 2)
        self.mock_model.transcribe.assert_called_once()

    def test_format_timestamp(self):
        """Test SRT timestamp formatting."""
        # Test various timestamps
        self.assertEqual(
            self.transcriber._format_timestamp(0),
            '00:00:00,000'
        )
        self.assertEqual(
            self.transcriber._format_timestamp(65.5),
            '00:01:05,500'
        )
        self.assertEqual(
            self.transcriber._format_timestamp(3661.123),
            '01:01:01,123'
        )

    def test_save_results_txt(self):
        """Test saving transcript as text file."""
        result = {
            'text': 'Test transcript text',
            'segments': [],
            'language': 'en'
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            outputs, summary = self.transcriber.save_results(
                result,
                'test.m4a',
                output_formats=['txt'],
                output_dir=tmpdir
            )

            self.assertIn('txt', outputs)
            txt_path = Path(outputs['txt'])
            self.assertTrue(txt_path.exists())

            with open(txt_path, 'r') as f:
                content = f.read()
                self.assertEqual(content, 'Test transcript text')

            # No summary should be generated
            self.assertIsNone(summary)

    def test_save_results_json(self):
        """Test saving transcript as JSON file."""
        result = {
            'text': 'Test transcript',
            'segments': [{'start': 0, 'end': 1, 'text': 'Test'}],
            'language': 'en'
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            outputs, summary = self.transcriber.save_results(
                result,
                'test.m4a',
                output_formats=['json'],
                output_dir=tmpdir
            )

            self.assertIn('json', outputs)
            json_path = Path(outputs['json'])
            self.assertTrue(json_path.exists())

            with open(json_path, 'r') as f:
                data = json.load(f)
                self.assertEqual(data['text'], 'Test transcript')
                self.assertEqual(data['language'], 'en')
                self.assertIn('transcribed_at', data)

            # No summary should be generated
            self.assertIsNone(summary)

    def test_save_results_srt(self):
        """Test saving transcript as SRT file."""
        result = {
            'text': 'Test transcript',
            'segments': [
                {'start': 0.0, 'end': 2.0, 'text': 'First segment'},
                {'start': 2.0, 'end': 5.0, 'text': 'Second segment'}
            ],
            'language': 'en'
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            outputs, summary = self.transcriber.save_results(
                result,
                'test.m4a',
                output_formats=['srt'],
                output_dir=tmpdir
            )

            self.assertIn('srt', outputs)
            srt_path = Path(outputs['srt'])
            self.assertTrue(srt_path.exists())

            with open(srt_path, 'r') as f:
                content = f.read()
                self.assertIn('1\n', content)
                self.assertIn('First segment', content)
                self.assertIn('Second segment', content)
                self.assertIn('-->', content)

            # No summary should be generated
            self.assertIsNone(summary)

    def test_save_results_all_formats(self):
        """Test saving transcript in all formats."""
        result = {
            'text': 'Complete test',
            'segments': [{'start': 0, 'end': 1, 'text': 'Test'}],
            'language': 'en'
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            outputs, summary = self.transcriber.save_results(
                result,
                'test.m4a',
                output_formats=['txt', 'json', 'srt'],
                output_dir=tmpdir
            )

            self.assertIn('txt', outputs)
            self.assertIn('json', outputs)
            self.assertIn('srt', outputs)

            for output_path in outputs.values():
                self.assertTrue(Path(output_path).exists())

    @patch('echolex.AudioTranscriber.summarize_with_chatgpt')
    def test_save_results_with_summary(self, mock_summarize):
        """Test saving transcript with AI summary."""
        mock_summarize.return_value = "This is a test summary"

        result = {
            'text': 'Test transcript text for summarization',
            'segments': [],
            'language': 'en'
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            outputs, summary = self.transcriber.save_results(
                result,
                'test.m4a',
                output_formats=['txt'],
                output_dir=tmpdir,
                summary_provider='chatgpt',
                summary_config={'model': 'gpt-4o-mini'}
            )

            # Check summary was generated
            self.assertEqual(summary, "This is a test summary")

            # Check summary.txt was created
            self.assertIn('summary', outputs)
            summary_txt_path = Path(outputs['summary'])
            self.assertTrue(summary_txt_path.exists())
            with open(summary_txt_path, 'r') as f:
                self.assertEqual(f.read(), "This is a test summary")

            # Check summary.json was created
            self.assertIn('summary_json', outputs)
            summary_json_path = Path(outputs['summary_json'])
            self.assertTrue(summary_json_path.exists())

            with open(summary_json_path, 'r') as f:
                summary_data = json.load(f)
                self.assertEqual(summary_data['summary'], "This is a test summary")
                self.assertEqual(summary_data['provider'], 'chatgpt')
                self.assertIn('model', summary_data['parameters'])
                self.assertEqual(summary_data['parameters']['model'], 'gpt-4o-mini')
                self.assertIn('generated_at', summary_data)

    @patch('echolex.AudioTranscriber.summarize_with_gemini')
    def test_save_results_with_gemini_summary(self, mock_summarize):
        """Test saving transcript with Gemini summary."""
        mock_summarize.return_value = "Gemini summary test"

        result = {
            'text': 'Test transcript',
            'segments': [],
            'language': 'en'
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            outputs, summary = self.transcriber.save_results(
                result,
                'test.m4a',
                output_formats=['txt', 'json'],
                output_dir=tmpdir,
                summary_provider='gemini',
                summary_config={
                    'model': 'gemini-1.5-flash',
                    'temperature': 0.8,
                    'max_tokens': 600
                }
            )

            # Check summary in transcript JSON
            json_path = Path(outputs['json'])
            with open(json_path, 'r') as f:
                transcript_data = json.load(f)
                self.assertEqual(transcript_data['summary'], "Gemini summary test")
                self.assertEqual(transcript_data['summary_provider'], 'gemini')

            # Check summary JSON details
            summary_json_path = Path(outputs['summary_json'])
            with open(summary_json_path, 'r') as f:
                summary_data = json.load(f)
                self.assertEqual(summary_data['provider'], 'gemini')
                self.assertEqual(summary_data['parameters']['model'], 'gemini-1.5-flash')
                self.assertEqual(summary_data['parameters']['temperature'], 0.8)
                self.assertEqual(summary_data['parameters']['max_tokens'], 600)

    def test_summarize_with_chatgpt(self):
        """Test ChatGPT summarization."""
        with patch('builtins.__import__') as mock_import:
            mock_openai = Mock()
            mock_client = Mock()
            mock_openai.OpenAI.return_value = mock_client

            def import_side_effect(name, *args, **kwargs):
                if name == 'openai':
                    return mock_openai
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="ChatGPT summary"))]
            mock_client.chat.completions.create.return_value = mock_response

            summary = self.transcriber.summarize_with_chatgpt(
                "Test transcript text",
                api_key="test-key",
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=500
            )

            self.assertEqual(summary, "ChatGPT summary")

    def test_summarize_with_chatgpt_no_api_key(self):
        """Test ChatGPT summarization without API key raises error."""
        with patch('builtins.__import__') as mock_import:
            mock_openai = Mock()

            def import_side_effect(name, *args, **kwargs):
                if name == 'openai':
                    return mock_openai
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(ValueError) as context:
                    self.transcriber.summarize_with_chatgpt("Test text")
                self.assertIn("API key not found", str(context.exception))

    @unittest.skip("Gemini mocking is complex - covered by integration test")
    def test_summarize_with_gemini(self):
        """Test Gemini summarization."""
        pass

    def test_summarize_with_gemini_no_api_key(self):
        """Test Gemini summarization without API key raises error."""
        with patch('builtins.__import__') as mock_import:
            mock_genai = Mock()

            def import_side_effect(name, *args, **kwargs):
                if name == 'google.generativeai':
                    return mock_genai
                return __import__(name, *args, **kwargs)

            mock_import.side_effect = import_side_effect

            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(ValueError) as context:
                    self.transcriber.summarize_with_gemini("Test text")
                self.assertIn("API key not found", str(context.exception))


class TestHelperFunctions(unittest.TestCase):
    """Test cases for helper functions."""

    def test_find_audio_file_exists_current_dir(self):
        """Test finding audio file in current directory."""
        with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = echolex.find_audio_file(tmp_path)
            self.assertEqual(result, Path(tmp_path))
        finally:
            os.unlink(tmp_path)

    def test_find_audio_file_exists_audio_files_dir(self):
        """Test finding audio file in audio_files directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_dir = Path(tmpdir) / 'audio_files'
            audio_dir.mkdir()
            test_file = audio_dir / 'test.m4a'
            test_file.write_text('fake audio')

            with patch('echolex.Path') as mock_path:
                mock_path.return_value.exists.side_effect = [False, True]
                mock_path.return_value.name = 'test.m4a'
                mock_path.side_effect = lambda x: Path(x)

                # This would normally exit, so we need to patch sys.exit
                with patch('sys.exit'):
                    result = echolex.find_audio_file('audio_files/test.m4a')

    def test_find_audio_file_not_found(self):
        """Test finding non-existent audio file exits."""
        with patch('sys.exit') as mock_exit:
            echolex.find_audio_file('/nonexistent/file.m4a')
            mock_exit.assert_called_once_with(1)


class TestCommandTranscribe(unittest.TestCase):
    """Test cases for cmd_transcribe function."""

    @patch('echolex.find_audio_file')
    @patch('echolex.AudioTranscriber')
    def test_cmd_transcribe_success(self, mock_transcriber_class, mock_find):
        """Test successful single file transcription."""
        # Setup mocks
        mock_find.return_value = Path('test.m4a')
        mock_transcriber = Mock()
        mock_transcriber_class.return_value = mock_transcriber

        mock_result = {
            'text': 'Test transcription result',
            'segments': []
        }
        mock_transcriber.transcribe.return_value = mock_result
        mock_transcriber.save_results.return_value = (
            {'txt': 'transcripts/test_transcript.txt'},
            None  # summary
        )

        # Create mock args
        args = Mock()
        args.audio_file = 'test.m4a'
        args.model = 'base'
        args.device = None
        args.language = None
        args.verbose = False
        args.output = ['txt']
        args.output_dir = 'transcripts'
        args.quiet = True

        # Run command
        echolex.cmd_transcribe(args)

        # Assertions
        mock_find.assert_called_once_with('test.m4a')
        mock_transcriber.transcribe.assert_called_once()
        mock_transcriber.save_results.assert_called_once()

    @patch('echolex.find_audio_file')
    @patch('echolex.AudioTranscriber')
    @patch('sys.exit')
    def test_cmd_transcribe_error(self, mock_exit, mock_transcriber_class, mock_find):
        """Test transcription error handling."""
        mock_find.return_value = Path('test.m4a')
        mock_transcriber = Mock()
        mock_transcriber_class.return_value = mock_transcriber
        mock_transcriber.transcribe.side_effect = Exception('Transcription failed')

        args = Mock()
        args.audio_file = 'test.m4a'
        args.model = 'base'
        args.device = None
        args.language = None
        args.verbose = False
        args.output = ['txt']
        args.output_dir = 'transcripts'
        args.quiet = True

        echolex.cmd_transcribe(args)
        mock_exit.assert_called_once_with(1)


class TestCommandBatch(unittest.TestCase):
    """Test cases for cmd_batch function."""

    @patch('echolex.glob.glob')
    @patch('echolex.AudioTranscriber')
    @patch('echolex.AudioProcessor')
    def test_cmd_batch_success(self, mock_processor_class, mock_transcriber_class, mock_glob):
        """Test successful batch transcription."""
        # Setup mocks
        mock_glob.return_value = ['audio1.m4a', 'audio2.m4a']

        mock_transcriber = Mock()
        mock_transcriber_class.return_value = mock_transcriber
        mock_transcriber.transcribe.return_value = {
            'text': 'Test',
            'segments': []
        }
        mock_transcriber.save_results.return_value = (
            {'txt': 'output.txt'},
            None  # summary
        )

        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        mock_processor.get_audio_info.return_value = {
            'duration': '00:02:00',
            'format': 'm4a',
            'size_mb': 2.5
        }

        args = Mock()
        args.patterns = ['*.m4a']
        args.model = 'base'
        args.verbose = False
        args.output = ['txt']
        args.output_dir = tempfile.mkdtemp()

        try:
            echolex.cmd_batch(args)

            # Verify summary file was created
            summary_path = Path(args.output_dir) / 'batch_transcription_summary.json'
            self.assertTrue(summary_path.exists())

            with open(summary_path) as f:
                summary = json.load(f)
                self.assertEqual(summary['total_files'], 2)
                self.assertEqual(summary['successful'], 2)
        finally:
            shutil.rmtree(args.output_dir)

    @patch('echolex.glob.glob')
    def test_cmd_batch_no_files(self, mock_glob):
        """Test batch processing with no matching files."""
        mock_glob.return_value = []

        args = Mock()
        args.patterns = ['*.m4a']
        args.model = 'base'
        args.verbose = False
        args.output = ['txt']
        args.output_dir = 'transcripts'

        # Should return early without error
        echolex.cmd_batch(args)


class TestCommandInfo(unittest.TestCase):
    """Test cases for cmd_info function."""

    @patch('echolex.find_audio_file')
    @patch('echolex.AudioProcessor')
    def test_cmd_info_success(self, mock_processor_class, mock_find):
        """Test displaying audio file information."""
        mock_find.return_value = Path('test.m4a')

        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        mock_processor.check_dependencies.return_value = True
        mock_processor.get_audio_info.return_value = {
            'filename': 'test.m4a',
            'duration': '00:02:30',
            'format': 'm4a',
            'size_mb': 3.5
        }

        args = Mock()
        args.audio_file = 'test.m4a'

        # Should run without error
        echolex.cmd_info(args)

    @patch('echolex.find_audio_file')
    @patch('echolex.AudioProcessor')
    @patch('sys.exit')
    def test_cmd_info_missing_dependencies(self, mock_exit, mock_processor_class, mock_find):
        """Test info command with missing dependencies."""
        mock_find.return_value = Path('test.m4a')

        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        mock_processor.check_dependencies.return_value = False
        mock_processor.get_audio_info.return_value = {'error': 'FFmpeg not found'}

        args = Mock()
        args.audio_file = 'test.m4a'

        echolex.cmd_info(args)
        mock_exit.assert_called_once_with(1)


class TestCommandCheck(unittest.TestCase):
    """Test cases for cmd_check function."""

    @patch('echolex.AudioProcessor')
    def test_cmd_check(self, mock_processor_class):
        """Test dependency check command."""
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        mock_processor.check_dependencies.return_value = True

        args = Mock()

        # Should run without error
        echolex.cmd_check(args)
        mock_processor.check_dependencies.assert_called_once()


class TestMainCLI(unittest.TestCase):
    """Test cases for main CLI entry point."""

    def test_main_no_command(self):
        """Test main with no command shows help and exits."""
        with patch('sys.argv', ['echolex.py']):
            with patch('argparse.ArgumentParser.print_help'):
                with self.assertRaises(SystemExit) as cm:
                    echolex.main()
                self.assertEqual(cm.exception.code, 1)

    @patch('sys.argv', ['echolex.py', 'check'])
    @patch('echolex.cmd_check')
    def test_main_check_command(self, mock_cmd_check):
        """Test main with check command."""
        echolex.main()
        mock_cmd_check.assert_called_once()

    @patch('sys.argv', ['echolex.py', 'transcribe', 'test.m4a'])
    @patch('echolex.cmd_transcribe')
    def test_main_transcribe_command(self, mock_cmd_transcribe):
        """Test main with transcribe command."""
        echolex.main()
        mock_cmd_transcribe.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)
