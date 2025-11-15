"""
Module 1: Speech Recognition and Data Collection
Azure Speech-to-Text integration for real-time speech recognition
"""
import azure.cognitiveservices.speech as speechsdk
from typing import Optional, Callable, List
from loguru import logger
import asyncio
from datetime import datetime
import json


class SpeechRecognizer:
    """Real-time speech recognition using Azure Speech Services"""
    
    def __init__(
        self,
        speech_key: str,
        speech_region: str,
        source_language: str = "en-US"
    ):
        """
        Initialize the speech recognizer
        
        Args:
            speech_key: Azure Speech Services API key
            speech_region: Azure region (e.g., 'eastus')
            source_language: Source language code (e.g., 'en-US', 'hi-IN')
        """
        self.speech_key = speech_key
        self.speech_region = speech_region
        self.source_language = source_language
        
        # Configure speech recognition
        self.speech_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=speech_region
        )
        self.speech_config.speech_recognition_language = source_language
        
        # Enable detailed results
        self.speech_config.output_format = speechsdk.OutputFormat.Detailed
        
        # Audio configuration
        self.audio_config = None
        self.recognizer = None
        
        # Callbacks
        self.on_recognized_callback: Optional[Callable] = None
        self.on_recognizing_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
        
        logger.info(f"Speech recognizer initialized for language: {source_language}")
    
    def setup_microphone_input(self):
        """Setup audio input from microphone"""
        self.audio_config = speechsdk.AudioConfig(use_default_microphone=True)
        self._create_recognizer()
        logger.info("Microphone input configured")
    
    def setup_file_input(self, audio_file_path: str):
        """
        Setup audio input from file
        
        Args:
            audio_file_path: Path to audio file
        """
        self.audio_config = speechsdk.AudioConfig(filename=audio_file_path)
        self._create_recognizer()
        logger.info(f"File input configured: {audio_file_path}")
    
    def setup_stream_input(self, stream):
        """
        Setup audio input from stream
        
        Args:
            stream: Audio stream object
        """
        self.audio_config = speechsdk.AudioConfig(stream=stream)
        self._create_recognizer()
        logger.info("Stream input configured")
    
    def _create_recognizer(self):
        """Create the speech recognizer with configured audio input"""
        self.recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=self.audio_config
        )
        
        # Connect callbacks
        self.recognizer.recognized.connect(self._on_recognized)
        self.recognizer.recognizing.connect(self._on_recognizing)
        self.recognizer.canceled.connect(self._on_canceled)
        self.recognizer.session_started.connect(self._on_session_started)
        self.recognizer.session_stopped.connect(self._on_session_stopped)
    
    def _on_recognized(self, evt):
        """Handle recognized speech event"""
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            result_data = {
                "text": evt.result.text,
                "language": self.source_language,
                "timestamp": datetime.utcnow().isoformat(),
                "duration": evt.result.duration,
                "offset": evt.result.offset
            }
            
            logger.info(f"Recognized: {evt.result.text}")
            
            if self.on_recognized_callback:
                self.on_recognized_callback(result_data)
    
    def _on_recognizing(self, evt):
        """Handle recognizing (interim) speech event"""
        if evt.result.reason == speechsdk.ResultReason.RecognizingSpeech:
            result_data = {
                "text": evt.result.text,
                "language": self.source_language,
                "timestamp": datetime.utcnow().isoformat(),
                "is_interim": True
            }
            
            logger.debug(f"Recognizing: {evt.result.text}")
            
            if self.on_recognizing_callback:
                self.on_recognizing_callback(result_data)
    
    def _on_canceled(self, evt):
        """Handle canceled event"""
        logger.error(f"Recognition canceled: {evt.reason}")
        
        if evt.reason == speechsdk.CancellationReason.Error:
            error_data = {
                "error_code": evt.error_code,
                "error_details": evt.error_details,
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.error(f"Error details: {evt.error_details}")
            
            if self.on_error_callback:
                self.on_error_callback(error_data)
    
    def _on_session_started(self, evt):
        """Handle session started event"""
        logger.info("Speech recognition session started")
    
    def _on_session_stopped(self, evt):
        """Handle session stopped event"""
        logger.info("Speech recognition session stopped")
    
    def start_continuous_recognition(self):
        """Start continuous speech recognition"""
        if not self.recognizer:
            raise ValueError("Recognizer not initialized. Call setup_*_input() first.")
        
        self.recognizer.start_continuous_recognition()
        logger.info("Continuous recognition started")
    
    def stop_continuous_recognition(self):
        """Stop continuous speech recognition"""
        if self.recognizer:
            self.recognizer.stop_continuous_recognition()
            logger.info("Continuous recognition stopped")
    
    async def recognize_once_async(self) -> dict:
        """
        Recognize speech once asynchronously
        
        Returns:
            Dictionary containing recognition result
        """
        if not self.recognizer:
            raise ValueError("Recognizer not initialized. Call setup_*_input() first.")
        
        result = self.recognizer.recognize_once()
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return {
                "success": True,
                "text": result.text,
                "language": self.source_language,
                "timestamp": datetime.utcnow().isoformat()
            }
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return {
                "success": False,
                "error": "No speech could be recognized"
            }
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            return {
                "success": False,
                "error": f"Recognition canceled: {cancellation.reason}",
                "error_details": cancellation.error_details
            }
    
    def set_callbacks(
        self,
        on_recognized: Optional[Callable] = None,
        on_recognizing: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ):
        """
        Set callback functions for recognition events
        
        Args:
            on_recognized: Callback for final recognized speech
            on_recognizing: Callback for interim recognition results
            on_error: Callback for errors
        """
        self.on_recognized_callback = on_recognized
        self.on_recognizing_callback = on_recognizing
        self.on_error_callback = on_error


class MultiLanguageSpeechRecognizer:
    """Speech recognizer supporting multiple source languages"""
    
    def __init__(self, speech_key: str, speech_region: str):
        """
        Initialize multi-language speech recognizer
        
        Args:
            speech_key: Azure Speech Services API key
            speech_region: Azure region
        """
        self.speech_key = speech_key
        self.speech_region = speech_region
        self.recognizers = {}
        
        logger.info("Multi-language speech recognizer initialized")
    
    def add_language(self, language_code: str) -> SpeechRecognizer:
        """
        Add support for a new language
        
        Args:
            language_code: Language code (e.g., 'en-US', 'hi-IN')
        
        Returns:
            SpeechRecognizer instance for the language
        """
        if language_code not in self.recognizers:
            recognizer = SpeechRecognizer(
                self.speech_key,
                self.speech_region,
                language_code
            )
            self.recognizers[language_code] = recognizer
            logger.info(f"Added language support: {language_code}")
        
        return self.recognizers[language_code]
    
    def get_recognizer(self, language_code: str) -> Optional[SpeechRecognizer]:
        """
        Get recognizer for a specific language
        
        Args:
            language_code: Language code
        
        Returns:
            SpeechRecognizer instance or None
        """
        return self.recognizers.get(language_code)
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self.recognizers.keys())
