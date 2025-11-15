"""
Unit tests for Module 1: Speech Recognition
"""
import pytest
from module1_speech_recognition import SpeechRecognizer, AudioPreprocessor
import numpy as np


class TestAudioPreprocessor:
    """Test audio preprocessing functions"""
    
    def test_normalize_audio(self):
        """Test audio normalization"""
        audio = np.array([0.5, 1.0, -0.5, -1.0])
        normalized = AudioPreprocessor.normalize_audio(audio)
        
        assert np.max(np.abs(normalized)) == 1.0
        assert normalized.shape == audio.shape
    
    def test_normalize_zero_audio(self):
        """Test normalization of zero audio"""
        audio = np.zeros(100)
        normalized = AudioPreprocessor.normalize_audio(audio)
        
        assert np.all(normalized == 0)
    
    def test_remove_silence(self):
        """Test silence removal"""
        # Create audio with silence
        audio = np.concatenate([
            np.zeros(100),
            np.ones(100) * 0.5,
            np.zeros(100)
        ])
        
        filtered = AudioPreprocessor.remove_silence(audio, 16000, threshold=0.1)
        
        assert len(filtered) < len(audio)
    
    def test_resample_audio(self):
        """Test audio resampling"""
        audio = np.random.randn(16000)  # 1 second at 16kHz
        
        # Resample to 8kHz
        resampled = AudioPreprocessor.resample_audio(audio, 16000, 8000)
        
        assert len(resampled) == 8000
    
    def test_apply_filters(self):
        """Test audio filtering"""
        audio = np.random.randn(1000)
        filtered = AudioPreprocessor.apply_filters(audio, 16000)
        
        # Check DC offset removed
        assert abs(np.mean(filtered)) < 0.01


class TestSpeechRecognizer:
    """Test speech recognizer initialization"""
    
    def test_recognizer_initialization(self):
        """Test recognizer can be initialized"""
        # This test requires actual Azure credentials
        # Skip if not available
        pytest.skip("Requires Azure credentials")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
