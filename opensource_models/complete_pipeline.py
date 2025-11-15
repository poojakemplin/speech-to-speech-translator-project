"""
Complete Open-Source Speech Translation Pipeline
Whisper (STT) → Helsinki-NLP (Translation) → gTTS (TTS)
"""
from .whisper_stt import WhisperSTT
from .helsinki_translator import HelsinkiTranslator
from .gtts_tts import GTTSTextToSpeech
from .audio_processor import AudioProcessor
from typing import List, Dict, Tuple, Optional
from loguru import logger
from pathlib import Path


class OpenSourcePipeline:
    """Complete open-source speech translation pipeline"""
    
    def __init__(
        self,
        whisper_model: str = "base",
        device: Optional[str] = None
    ):
        """
        Initialize pipeline
        
        Args:
            whisper_model: Whisper model size (tiny, base, small, medium, large)
            device: Device to run on (cuda/cpu)
        """
        logger.info("Initializing open-source translation pipeline...")
        
        # Initialize components
        self.audio_processor = AudioProcessor()
        self.stt = WhisperSTT(model_size=whisper_model, device=device)
        self.translator = HelsinkiTranslator(device=device)
        self.tts = GTTSTextToSpeech()
        
        logger.info("Pipeline initialized successfully")
    
    def process_audio(
        self,
        audio_path: str,
        source_language: str,
        target_languages: List[str],
        output_dir: str = "output"
    ) -> Dict:
        """
        Complete pipeline: Audio → Transcription → Translation → Speech
        
        Args:
            audio_path: Path to input audio file
            source_language: Source language code (e.g., 'hi', 'en')
            target_languages: List of target language codes
            output_dir: Directory to save output files
        
        Returns:
            Dictionary with all results
        """
        logger.info(f"Processing audio: {audio_path}")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Convert audio to WAV (mono, 16kHz)
        logger.info("Step 1: Converting audio format...")
        converted_audio = self.audio_processor.convert_to_wav(
            audio_path,
            output_path=str(output_path / "converted.wav")
        )
        
        # Step 2: Speech-to-Text (Whisper)
        logger.info("Step 2: Transcribing speech...")
        transcription = self.stt.transcribe_audio(
            converted_audio,
            language=source_language
        )
        
        if not transcription["success"]:
            return {
                "success": False,
                "error": "Transcription failed",
                "details": transcription
            }
        
        transcribed_text = transcription["text"]
        logger.info(f"Transcribed: {transcribed_text}")
        
        # Step 3: Translation (Helsinki-NLP)
        logger.info("Step 3: Translating text...")
        translations = {}
        for target_lang in target_languages:
            translation = self.translator.translate_text(
                transcribed_text,
                source_language,
                target_lang
            )
            
            if translation["success"]:
                translations[target_lang] = translation["translated_text"]
                logger.info(f"Translated to {target_lang}: {translation['translated_text']}")
        
        # Step 4: Text-to-Speech (gTTS)
        logger.info("Step 4: Synthesizing speech...")
        audio_outputs = {}
        for lang, text in translations.items():
            output_file = output_path / f"output_{lang}.mp3"
            synthesis = self.tts.synthesize_speech(
                text,
                lang,
                output_path=str(output_file)
            )
            
            if synthesis["success"]:
                audio_outputs[lang] = str(output_file)
                logger.info(f"Audio generated for {lang}: {output_file}")
        
        return {
            "success": True,
            "input_audio": audio_path,
            "converted_audio": converted_audio,
            "transcription": {
                "text": transcribed_text,
                "language": transcription["language"]
            },
            "translations": translations,
            "audio_outputs": audio_outputs
        }
    
    def process_batch(
        self,
        audio_files: List[str],
        source_language: str,
        target_languages: List[str],
        output_dir: str = "batch_output"
    ) -> List[Tuple[str, Dict]]:
        """
        Process multiple audio files
        
        Args:
            audio_files: List of audio file paths
            source_language: Source language code
            target_languages: List of target language codes
            output_dir: Base output directory
        
        Returns:
            List of tuples (audio_file, result_dict)
        """
        results = []
        
        for i, audio_file in enumerate(audio_files):
            logger.info(f"Processing file {i+1}/{len(audio_files)}: {audio_file}")
            
            # Create separate output directory for each file
            file_output_dir = Path(output_dir) / f"file_{i+1}"
            
            result = self.process_audio(
                audio_file,
                source_language,
                target_languages,
                str(file_output_dir)
            )
            
            results.append((audio_file, result))
        
        logger.info(f"Batch processing completed: {len(results)} files")
        return results
    
    def transcribe_only(self, audio_path: str, language: Optional[str] = None) -> Dict:
        """
        Only transcribe audio (no translation)
        
        Args:
            audio_path: Path to audio file
            language: Source language (optional, auto-detect if None)
        
        Returns:
            Transcription result
        """
        # Convert audio
        converted = self.audio_processor.convert_to_wav(audio_path)
        
        # Transcribe
        return self.stt.transcribe_audio(converted, language)
    
    def translate_only(
        self,
        text: str,
        source_lang: str,
        target_langs: List[str]
    ) -> Dict[str, str]:
        """
        Only translate text (no STT/TTS)
        
        Args:
            text: Text to translate
            source_lang: Source language
            target_langs: Target languages
        
        Returns:
            Dictionary mapping languages to translations
        """
        translations = {}
        for target_lang in target_langs:
            result = self.translator.translate_text(text, source_lang, target_lang)
            if result["success"]:
                translations[target_lang] = result["translated_text"]
        
        return translations
    
    def synthesize_only(
        self,
        translations: Dict[str, str],
        output_dir: str = "tts_output"
    ) -> Dict[str, str]:
        """
        Only synthesize speech (no STT/translation)
        
        Args:
            translations: Dictionary mapping languages to text
            output_dir: Output directory
        
        Returns:
            Dictionary mapping languages to audio file paths
        """
        return self.tts.synthesize_multiple_languages(translations, output_dir)
