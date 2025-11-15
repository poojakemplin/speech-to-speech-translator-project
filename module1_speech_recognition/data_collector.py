"""
Data Collection Module for Speech Recognition
Collects and preprocesses speech data for training and evaluation
"""
import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import wave
import numpy as np
from loguru import logger


class SpeechDataCollector:
    """Collects and manages speech data for training and evaluation"""
    
    def __init__(self, data_dir: str = "data/collected_speech"):
        """
        Initialize data collector
        
        Args:
            data_dir: Directory to store collected data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.audio_dir = self.data_dir / "audio"
        self.transcripts_dir = self.data_dir / "transcripts"
        self.metadata_dir = self.data_dir / "metadata"
        
        for dir_path in [self.audio_dir, self.transcripts_dir, self.metadata_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.collection_log = []
        logger.info(f"Data collector initialized at: {self.data_dir}")
    
    def save_audio_sample(
        self,
        audio_data: bytes,
        language: str,
        sample_rate: int = 16000,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Save audio sample with metadata
        
        Args:
            audio_data: Raw audio data
            language: Language code
            sample_rate: Audio sample rate
            metadata: Additional metadata
        
        Returns:
            Sample ID
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        sample_id = f"{language}_{timestamp}"
        
        # Save audio file
        audio_file = self.audio_dir / f"{sample_id}.wav"
        
        # Save metadata
        sample_metadata = {
            "sample_id": sample_id,
            "language": language,
            "sample_rate": sample_rate,
            "timestamp": datetime.utcnow().isoformat(),
            "audio_file": str(audio_file),
            "duration": len(audio_data) / (sample_rate * 2),  # Approximate
            **(metadata or {})
        }
        
        metadata_file = self.metadata_dir / f"{sample_id}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(sample_metadata, f, indent=2, ensure_ascii=False)
        
        self.collection_log.append(sample_metadata)
        logger.info(f"Saved audio sample: {sample_id}")
        
        return sample_id
    
    def save_transcript(
        self,
        sample_id: str,
        transcript: str,
        confidence: Optional[float] = None
    ):
        """
        Save transcript for an audio sample
        
        Args:
            sample_id: Sample identifier
            transcript: Transcribed text
            confidence: Recognition confidence score
        """
        transcript_data = {
            "sample_id": sample_id,
            "transcript": transcript,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        transcript_file = self.transcripts_dir / f"{sample_id}.json"
        with open(transcript_file, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved transcript for: {sample_id}")
    
    def save_recognition_result(
        self,
        result_data: Dict,
        audio_data: Optional[bytes] = None
    ) -> str:
        """
        Save complete recognition result with audio
        
        Args:
            result_data: Recognition result dictionary
            audio_data: Optional audio data
        
        Returns:
            Sample ID
        """
        language = result_data.get("language", "unknown")
        text = result_data.get("text", "")
        
        sample_id = None
        if audio_data:
            sample_id = self.save_audio_sample(
                audio_data,
                language,
                metadata=result_data
            )
        else:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
            sample_id = f"{language}_{timestamp}"
        
        self.save_transcript(sample_id, text)
        
        return sample_id
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about collected data
        
        Returns:
            Dictionary with collection statistics
        """
        stats = {
            "total_samples": len(list(self.audio_dir.glob("*.wav"))),
            "total_transcripts": len(list(self.transcripts_dir.glob("*.json"))),
            "languages": {},
            "total_duration": 0
        }
        
        # Analyze metadata
        for metadata_file in self.metadata_dir.glob("*.json"):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                language = metadata.get("language", "unknown")
                duration = metadata.get("duration", 0)
                
                if language not in stats["languages"]:
                    stats["languages"][language] = {
                        "count": 0,
                        "duration": 0
                    }
                
                stats["languages"][language]["count"] += 1
                stats["languages"][language]["duration"] += duration
                stats["total_duration"] += duration
        
        return stats
    
    def export_dataset(self, output_file: str):
        """
        Export collected data as a dataset
        
        Args:
            output_file: Output JSON file path
        """
        dataset = []
        
        for metadata_file in self.metadata_dir.glob("*.json"):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            sample_id = metadata["sample_id"]
            transcript_file = self.transcripts_dir / f"{sample_id}.json"
            
            if transcript_file.exists():
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    transcript_data = json.load(f)
                
                dataset.append({
                    **metadata,
                    "transcript": transcript_data.get("transcript"),
                    "confidence": transcript_data.get("confidence")
                })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dataset exported to: {output_file}")
    
    def load_sample_data(self, sample_file: str) -> List[Dict]:
        """
        Load sample commentary data for testing
        
        Args:
            sample_file: Path to sample data file
        
        Returns:
            List of sample data dictionaries
        """
        if os.path.exists(sample_file):
            with open(sample_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []


class AudioPreprocessor:
    """Preprocesses audio data for speech recognition"""
    
    @staticmethod
    def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
        """
        Normalize audio amplitude
        
        Args:
            audio_data: Audio data as numpy array
        
        Returns:
            Normalized audio data
        """
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val
        return audio_data
    
    @staticmethod
    def remove_silence(
        audio_data: np.ndarray,
        sample_rate: int,
        threshold: float = 0.01
    ) -> np.ndarray:
        """
        Remove silence from audio
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate
            threshold: Silence threshold
        
        Returns:
            Audio data with silence removed
        """
        # Simple energy-based silence removal
        energy = np.abs(audio_data)
        mask = energy > threshold
        return audio_data[mask]
    
    @staticmethod
    def resample_audio(
        audio_data: np.ndarray,
        orig_rate: int,
        target_rate: int
    ) -> np.ndarray:
        """
        Resample audio to target sample rate
        
        Args:
            audio_data: Audio data as numpy array
            orig_rate: Original sample rate
            target_rate: Target sample rate
        
        Returns:
            Resampled audio data
        """
        if orig_rate == target_rate:
            return audio_data
        
        # Simple linear interpolation resampling
        duration = len(audio_data) / orig_rate
        target_length = int(duration * target_rate)
        
        indices = np.linspace(0, len(audio_data) - 1, target_length)
        return np.interp(indices, np.arange(len(audio_data)), audio_data)
    
    @staticmethod
    def apply_filters(audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply audio filters for better recognition
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate
        
        Returns:
            Filtered audio data
        """
        # Normalize
        audio_data = AudioPreprocessor.normalize_audio(audio_data)
        
        # Remove DC offset
        audio_data = audio_data - np.mean(audio_data)
        
        return audio_data
