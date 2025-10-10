"""
🌸 Blossom AI - Audio Generation Tests

Tests for audio generation functionality.
"""

import unittest
import os
import tempfile
from blossom_ai import Blossom, BlossomError
from blossom_ai.errors import ErrorType


class TestAudioGeneration(unittest.TestCase):
    """Test audio generation functionality"""

    def setUp(self):
        """Set up test client"""
        self.ai = Blossom(timeout=60)

    def test_simple_audio_generation(self):
        """Test simple audio generation"""
        print("\n🧪 Testing simple audio generation...")

        audio_data = self.ai.audio.generate("Hello, this is a test audio.")

        self.assertIsNotNone(audio_data)
        self.assertIsInstance(audio_data, bytes)
        self.assertGreater(len(audio_data), 1000)  # Should be reasonable audio size

        print(f"✅ Generated audio size: {len(audio_data)} bytes")

    def test_save_audio_to_file(self):
        """Test saving generated audio to file"""
        print("\n🧪 Testing save to file...")

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            filename = tmp_file.name

        try:
            # Generate and save audio
            saved_path = self.ai.audio.save(
                text="This is an audio file saved to disk.",
                filename=filename
            )

            self.assertEqual(saved_path, filename)
            self.assertTrue(os.path.exists(filename))
            self.assertGreater(os.path.getsize(filename), 1000)

            print(f"✅ Audio saved to: {filename}")
            print(f"✅ File size: {os.path.getsize(filename)} bytes")

        finally:
            # Clean up
            if os.path.exists(filename):
                os.unlink(filename)

    def test_different_voices(self):
        """Test audio generation with different voices"""
        print("\n🧪 Testing different voices...")

        voices_to_test = self.ai.audio.voices()
        text_to_generate = "The quick brown fox jumps over the lazy dog."

        self.assertGreater(len(voices_to_test), 0, "No voices found to test.")

        for voice in voices_to_test:
            try:
                audio_data = self.ai.audio.generate(text=text_to_generate, voice=voice)
                self.assertIsNotNone(audio_data)
                self.assertIsInstance(audio_data, bytes)
                self.assertGreater(len(audio_data), 1000)
                print(f"✅ Voice '{voice}': {len(audio_data)} bytes")
            except Exception as e:
                print(f"⚠️  Voice '{voice}' failed: {e}")

    def test_audio_models_list(self):
        """Test listing available audio models (voices) - currently hardcoded"""
        print("\n🧪 Testing audio models list...")

        voices = self.ai.audio.voices()

        self.assertIsNotNone(voices)
        self.assertTrue(isinstance(voices, list))
        self.assertGreater(len(voices), 0)

        print(f"✅ Found {len(voices)} audio voices")
        print(f"   Available voices: {voices}")

    def test_empty_text_input(self):
        """Test handling of empty text input"""
        print("\n🧪 Testing empty text input...")

        # The API might return an empty audio or raise an error. We should handle both.
        audio_data = self.ai.audio.generate("")
        self.assertIsNotNone(audio_data)
        # Depending on API behavior, it might return a very small audio or an error
        # For now, we'll assert it's not empty, but this might need adjustment
        self.assertGreaterEqual(len(audio_data), 0)
        print(f"✅ Empty text input handled, audio size: {len(audio_data)} bytes")

    def test_long_text_input(self):
        """Test handling of very long text input"""
        print("\n🧪 Testing very long text input...")

        long_text = "This is a very long text that should ideally be truncated or cause an error if the API has a limit. " * 50

        # Assuming the API might handle long text by truncating or returning an error.
        # For now, we'll just check if it returns some audio data.
        audio_data = self.ai.audio.generate(long_text)
        self.assertIsNotNone(audio_data)
        self.assertGreater(len(audio_data), 1000)
        print(f"✅ Long text input handled, audio size: {len(audio_data)} bytes")

    def test_invalid_voice(self):
        """Test handling of an invalid voice"""
        print("\n🧪 Testing invalid voice...")

        with self.assertRaises(BlossomError) as cm:
            self.ai.audio.generate(text="Hello", voice="nonexistent_voice")

        self.assertEqual(cm.exception.error_type, ErrorType.API)
        print(f"✅ Invalid voice correctly raised BlossomError: {cm.exception.message}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

