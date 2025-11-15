"""
Module 3: Real-time Speech-to-Speech Integration
Complete pipeline for real-time speech translation
"""
import azure.cognitiveservices.speech as speechsdk
from typing import Dict, List, Optional, Callable
import asyncio
from loguru import logger
from datetime import datetime
import queue
import threading


class SpeechToSpeechPipeline:
    """Complete pipeline for real-time speech-to-speech translation"""
    
    def __init__(
        self,
        speech_key: str,
        speech_region: str,
        openai_translator,
        source_language: str = "en-US",
        target_languages: List[str] = None
    ):
        """
        Initialize speech-to-speech pipeline
        
        Args:
            speech_key: Azure Speech Services API key
            speech_region: Azure region
            openai_translator: AzureOpenAITranslator instance
            source_language: Source language code
            target_languages: List of target language codes
        """
        self.speech_key = speech_key
        self.speech_region = speech_region
        self.translator = openai_translator
        self.source_language = source_language
        self.target_languages = target_languages or []
        
        # Speech recognition setup
        self.speech_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=speech_region
        )
        self.speech_config.speech_recognition_language = source_language
        
        # Speech synthesis configs for each target language
        self.synthesis_configs = {}
        self._setup_synthesis_configs()
        
        # Processing queues
        self.recognition_queue = queue.Queue()
        self.translation_queue = queue.Queue()
        self.synthesis_queue = queue.Queue()
        
        # State
        self.is_running = False
        self.recognizer = None
        
        # Callbacks
        self.on_translation_complete: Optional[Callable] = None
        self.on_synthesis_complete: Optional[Callable] = None
        
        logger.info(f"Speech-to-speech pipeline initialized: {source_language} -> {target_languages}")
    
    def _setup_synthesis_configs(self):
        """Setup speech synthesis configurations for target languages"""
        for lang in self.target_languages:
            config = speechsdk.SpeechConfig(
                subscription=self.speech_key,
                region=self.speech_region
            )
            
            # Set appropriate voice for each language
            voice_name = self._get_voice_name(lang)
            config.speech_synthesis_voice_name = voice_name
            
            self.synthesis_configs[lang] = config
            logger.info(f"Synthesis configured for {lang} with voice: {voice_name}")
    
    def _get_voice_name(self, language_code: str) -> str:
        """
        Get appropriate voice name for language
        
        Args:
            language_code: Language code
        
        Returns:
            Voice name for Azure Speech Services
        """
        voice_map = {
            "en-US": "en-US-JennyNeural",
            "hi-IN": "hi-IN-SwaraNeural",
            "es-ES": "es-ES-ElviraNeural",
            "fr-FR": "fr-FR-DeniseNeural",
            "de-DE": "de-DE-KatjaNeural",
            "it-IT": "it-IT-ElsaNeural",
            "pt-BR": "pt-BR-FranciscaNeural",
            "ja-JP": "ja-JP-NanamiNeural",
            "ko-KR": "ko-KR-SunHiNeural",
            "zh-CN": "zh-CN-XiaoxiaoNeural",
            "ar-SA": "ar-SA-ZariyahNeural",
            "ru-RU": "ru-RU-SvetlanaNeural",
            "tr-TR": "tr-TR-EmelNeural",
            "nl-NL": "nl-NL-ColetteNeural"
        }
        return voice_map.get(language_code, "en-US-JennyNeural")
    
    def start_pipeline(self, audio_config=None):
        """
        Start the real-time translation pipeline
        
        Args:
            audio_config: Optional audio configuration
        """
        if self.is_running:
            logger.warning("Pipeline is already running")
            return
        
        self.is_running = True
        
        # Setup audio input
        if audio_config is None:
            audio_config = speechsdk.AudioConfig(use_default_microphone=True)
        
        # Create recognizer
        self.recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )
        
        # Connect callbacks
        self.recognizer.recognized.connect(self._on_recognized)
        self.recognizer.recognizing.connect(self._on_recognizing)
        self.recognizer.canceled.connect(self._on_canceled)
        
        # Start continuous recognition
        self.recognizer.start_continuous_recognition()
        
        # Start processing threads
        self.translation_thread = threading.Thread(target=self._translation_worker)
        self.synthesis_thread = threading.Thread(target=self._synthesis_worker)
        
        self.translation_thread.start()
        self.synthesis_thread.start()
        
        logger.info("Real-time translation pipeline started")
    
    def stop_pipeline(self):
        """Stop the real-time translation pipeline"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Stop recognition
        if self.recognizer:
            self.recognizer.stop_continuous_recognition()
        
        # Wait for threads to finish
        if hasattr(self, 'translation_thread'):
            self.translation_thread.join(timeout=5)
        if hasattr(self, 'synthesis_thread'):
            self.synthesis_thread.join(timeout=5)
        
        logger.info("Real-time translation pipeline stopped")
    
    def _on_recognized(self, evt):
        """Handle recognized speech"""
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = evt.result.text
            logger.info(f"Recognized: {text}")
            
            # Add to translation queue
            self.recognition_queue.put({
                "text": text,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def _on_recognizing(self, evt):
        """Handle interim recognition results"""
        if evt.result.reason == speechsdk.ResultReason.RecognizingSpeech:
            logger.debug(f"Recognizing: {evt.result.text}")
    
    def _on_canceled(self, evt):
        """Handle cancellation"""
        logger.error(f"Recognition canceled: {evt.reason}")
    
    def _translation_worker(self):
        """Worker thread for translation"""
        logger.info("Translation worker started")
        
        while self.is_running:
            try:
                # Get recognized text
                recognition_data = self.recognition_queue.get(timeout=1)
                text = recognition_data["text"]
                
                # Translate to all target languages
                translations = {}
                for target_lang in self.target_languages:
                    result = self.translator.translate_text(
                        text,
                        self.source_language,
                        target_lang
                    )
                    
                    if result["success"]:
                        translations[target_lang] = result["translated_text"]
                        logger.info(f"Translated to {target_lang}: {result['translated_text']}")
                
                # Add to synthesis queue
                self.translation_queue.put({
                    "original_text": text,
                    "translations": translations,
                    "timestamp": recognition_data["timestamp"]
                })
                
                # Callback
                if self.on_translation_complete:
                    self.on_translation_complete(translations)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Translation worker error: {str(e)}")
        
        logger.info("Translation worker stopped")
    
    def _synthesis_worker(self):
        """Worker thread for speech synthesis"""
        logger.info("Synthesis worker started")
        
        while self.is_running:
            try:
                # Get translations
                translation_data = self.translation_queue.get(timeout=1)
                translations = translation_data["translations"]
                
                # Synthesize speech for each language
                audio_outputs = {}
                for lang, text in translations.items():
                    audio_data = self._synthesize_speech(text, lang)
                    if audio_data:
                        audio_outputs[lang] = audio_data
                        logger.info(f"Synthesized speech for {lang}")
                
                # Add to output queue
                self.synthesis_queue.put({
                    "original_text": translation_data["original_text"],
                    "audio_outputs": audio_outputs,
                    "timestamp": translation_data["timestamp"]
                })
                
                # Callback
                if self.on_synthesis_complete:
                    self.on_synthesis_complete(audio_outputs)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Synthesis worker error: {str(e)}")
        
        logger.info("Synthesis worker stopped")
    
    def _synthesize_speech(self, text: str, language: str) -> Optional[bytes]:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            language: Target language
        
        Returns:
            Audio data as bytes or None
        """
        try:
            config = self.synthesis_configs.get(language)
            if not config:
                logger.error(f"No synthesis config for language: {language}")
                return None
            
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=config,
                audio_config=None  # Return audio data instead of playing
            )
            
            result = synthesizer.speak_text(text)
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            else:
                logger.error(f"Speech synthesis failed: {result.reason}")
                return None
                
        except Exception as e:
            logger.error(f"Synthesis error: {str(e)}")
            return None
    
    def get_output(self, timeout: float = 1.0) -> Optional[Dict]:
        """
        Get synthesized output from queue
        
        Args:
            timeout: Timeout in seconds
        
        Returns:
            Output dictionary or None
        """
        try:
            return self.synthesis_queue.get(timeout=timeout)
        except queue.Empty:
            return None


class StreamingPipeline:
    """Streaming pipeline with minimal latency"""
    
    def __init__(
        self,
        speech_key: str,
        speech_region: str,
        translator,
        source_language: str,
        target_language: str
    ):
        """
        Initialize streaming pipeline for single language pair
        
        Args:
            speech_key: Azure Speech Services API key
            speech_region: Azure region
            translator: Translator instance
            source_language: Source language code
            target_language: Target language code
        """
        self.speech_key = speech_key
        self.speech_region = speech_region
        self.translator = translator
        self.source_language = source_language
        self.target_language = target_language
        
        self.is_streaming = False
        self.stream_callback: Optional[Callable] = None
        
        logger.info(f"Streaming pipeline initialized: {source_language} -> {target_language}")
    
    async def start_streaming(self, audio_stream):
        """
        Start streaming translation
        
        Args:
            audio_stream: Audio input stream
        """
        self.is_streaming = True
        
        # Setup speech recognition
        speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key,
            region=self.speech_region
        )
        speech_config.speech_recognition_language = self.source_language
        
        audio_config = speechsdk.AudioConfig(stream=audio_stream)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        
        # Process recognition results
        def on_result(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                asyncio.create_task(self._process_and_stream(evt.result.text))
        
        recognizer.recognized.connect(on_result)
        recognizer.start_continuous_recognition()
        
        logger.info("Streaming started")
        
        # Keep streaming until stopped
        while self.is_streaming:
            await asyncio.sleep(0.1)
        
        recognizer.stop_continuous_recognition()
        logger.info("Streaming stopped")
    
    async def _process_and_stream(self, text: str):
        """Process and stream translation"""
        # Translate
        result = await self.translator.translate_text_async(
            text,
            self.source_language,
            self.target_language
        )
        
        if result["success"] and self.stream_callback:
            await self.stream_callback(result)
    
    def stop_streaming(self):
        """Stop streaming"""
        self.is_streaming = False
