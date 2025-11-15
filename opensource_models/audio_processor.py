"""
Audio Processing using pydub
Converts audio to consistent format (WAV, mono, 16kHz)
"""
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    import warnings
    warnings.warn("pydub not available. Audio conversion features will be limited.")

from pathlib import Path
from loguru import logger
from typing import Optional
import subprocess
import os


class AudioProcessor:
    """Process audio files for model compatibility"""
    
    @staticmethod
    def convert_to_wav(
        input_path: str,
        output_path: Optional[str] = None,
        sample_rate: int = 16000,
        channels: int = 1
    ) -> str:
        """
        Convert audio to WAV format (mono, 16kHz)
        
        Args:
            input_path: Input audio file path
            output_path: Output WAV file path (optional)
            sample_rate: Target sample rate (default: 16000)
            channels: Number of channels (1=mono, 2=stereo)
        
        Returns:
            Path to converted audio file
        """
        try:
            logger.info(f"Converting audio: {input_path}")
            
            # Generate output path if not provided
            if output_path is None:
                input_path_obj = Path(input_path)
                output_path = str(input_path_obj.parent / f"{input_path_obj.stem}_converted.wav")
            
            # If input is already WAV, try to use it directly
            if input_path.lower().endswith('.wav'):
                logger.info(f"Input is already WAV format: {input_path}")
                return input_path
            
            # Try pydub first
            if PYDUB_AVAILABLE:
                try:
                    audio = AudioSegment.from_file(input_path)
                    
                    # Convert to mono
                    if channels == 1:
                        audio = audio.set_channels(1)
                    
                    # Set sample rate
                    audio = audio.set_frame_rate(sample_rate)
                    
                    # Export as WAV
                    audio.export(output_path, format="wav")
                    
                    logger.info(f"Audio converted successfully: {output_path}")
                    return output_path
                except Exception as e:
                    logger.warning(f"pydub conversion failed: {e}, trying ffmpeg...")
            
            # Fallback to ffmpeg command line
            logger.info("Using ffmpeg for conversion...")
            cmd = [
                'ffmpeg', '-i', input_path,
                '-ar', str(sample_rate),
                '-ac', str(channels),
                '-y',  # Overwrite output
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Audio converted successfully with ffmpeg: {output_path}")
                return output_path
            else:
                raise Exception(f"ffmpeg conversion failed: {result.stderr}")
            
        except Exception as e:
            logger.error(f"Audio conversion error: {str(e)}")
            logger.info("Tip: Install ffmpeg or ensure input is WAV format")
            raise
    
    @staticmethod
    def get_audio_info(audio_path: str) -> dict:
        """Get audio file information"""
        if PYDUB_AVAILABLE:
            try:
                audio = AudioSegment.from_file(audio_path)
                return {
                    "duration": len(audio) / 1000.0,  # seconds
                    "channels": audio.channels,
                    "sample_rate": audio.frame_rate,
                    "sample_width": audio.sample_width
                }
            except:
                pass
        
        # Fallback: basic info
        return {
            "duration": 0,
            "channels": 1,
            "sample_rate": 16000,
            "sample_width": 2
        }
