"""
Open-Source Speech-to-Text using OpenAI Whisper
Alternative to Azure Speech Services
"""
import whisper
import torch
from typing import Optional, Dict, List
from loguru import logger
from pathlib import Path
import numpy as np


class WhisperSTT:
    """Speech-to-Text using OpenAI Whisper model"""
    
    def __init__(self, model_size: str = "base", device: Optional[str] = None):
        """
        Initialize Whisper STT
        
        Args:
            model_size: Model size (tiny, base, small, medium, large)
            device: Device to run on (cuda/cpu). Auto-detect if None
        """
        self.model_size = model_size
        
        # Auto-detect device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        logger.info(f"Loading Whisper model: {model_size} on {self.device}")
        self.model = whisper.load_model(model_size, device=self.device)
        logger.info("Whisper model loaded successfully")
    
    def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict:
        """
        Transcribe audio file
        
        Args:
            audio_path: Path to audio file
            language: Source language code (e.g., 'en', 'hi', 'es')
            task: 'transcribe' or 'translate' (translate converts to English)
        
        Returns:
            Dictionary with transcription results
        """
        try:
            logger.info(f"Transcribing audio: {audio_path}")
            
            # Transcribe
            result = self.model.transcribe(
                audio_path,
                language=language,
                task=task,
                fp16=(self.device == "cuda")
            )
            
            return {
                "success": True,
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "segments": result.get("segments", []),
                "duration": sum(seg["end"] - seg["start"] for seg in result.get("segments", []))
            }
            
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def transcribe_audio_array(
        self,
        audio_array: np.ndarray,
        sample_rate: int = 16000,
        language: Optional[str] = None
    ) -> Dict:
        """
        Transcribe audio from numpy array
        
        Args:
            audio_array: Audio data as numpy array
            sample_rate: Sample rate of audio
            language: Source language code
        
        Returns:
            Dictionary with transcription results
        """
        try:
            # Whisper expects audio at 16kHz
            if sample_rate != 16000:
                logger.warning(f"Resampling audio from {sample_rate}Hz to 16000Hz")
                # Simple resampling (use librosa for better quality)
                audio_array = self._resample(audio_array, sample_rate, 16000)
            
            # Normalize audio
            audio_array = audio_array.astype(np.float32)
            if audio_array.max() > 1.0:
                audio_array = audio_array / 32768.0
            
            result = self.model.transcribe(
                audio_array,
                language=language,
                fp16=(self.device == "cuda")
            )
            
            return {
                "success": True,
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "segments": result.get("segments", [])
            }
            
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def transcribe_batch(
        self,
        audio_paths: List[str],
        language: Optional[str] = None
    ) -> List[Dict]:
        """
        Transcribe multiple audio files
        
        Args:
            audio_paths: List of audio file paths
            language: Source language code
        
        Returns:
            List of transcription results
        """
        results = []
        for audio_path in audio_paths:
            result = self.transcribe_audio(audio_path, language)
            results.append(result)
        
        return results
    
    def detect_language(self, audio_path: str) -> Dict:
        """
        Detect language of audio
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary with detected language and confidence
        """
        try:
            # Load audio
            audio = whisper.load_audio(audio_path)
            audio = whisper.pad_or_trim(audio)
            
            # Make log-Mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            
            # Detect language
            _, probs = self.model.detect_language(mel)
            
            detected_lang = max(probs, key=probs.get)
            confidence = probs[detected_lang]
            
            return {
                "success": True,
                "language": detected_lang,
                "confidence": confidence,
                "all_probabilities": probs
            }
            
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _resample(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Simple resampling (for better quality, use librosa)"""
        duration = len(audio) / orig_sr
        target_length = int(duration * target_sr)
        indices = np.linspace(0, len(audio) - 1, target_length)
        return np.interp(indices, np.arange(len(audio)), audio)
    
    @staticmethod
    def get_available_models() -> List[str]:
        """Get list of available Whisper models"""
        return ["tiny", "base", "small", "medium", "large"]
    
    @staticmethod
    def get_model_info(model_size: str) -> Dict:
        """Get information about a model"""
        model_info = {
            "tiny": {"params": "39M", "vram": "~1GB", "speed": "~32x"},
            "base": {"params": "74M", "vram": "~1GB", "speed": "~16x"},
            "small": {"params": "244M", "vram": "~2GB", "speed": "~6x"},
            "medium": {"params": "769M", "vram": "~5GB", "speed": "~2x"},
            "large": {"params": "1550M", "vram": "~10GB", "speed": "~1x"}
        }
        return model_info.get(model_size, {})
