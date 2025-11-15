"""
Open-Source Text-to-Speech using gTTS (Google Text-to-Speech)
Alternative to Azure Neural TTS
"""
from gtts import gTTS
from typing import Optional, Dict
from loguru import logger
from pathlib import Path
import io


class GTTSTextToSpeech:
    """Text-to-Speech using gTTS"""
    
    def __init__(self):
        """Initialize gTTS TTS"""
        logger.info("gTTS Text-to-Speech initialized")
    
    def synthesize_speech(
        self,
        text: str,
        language: str,
        output_path: Optional[str] = None,
        slow: bool = False
    ) -> Dict:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            language: Language code (e.g., 'en', 'hi', 'es')
            output_path: Path to save audio file (optional)
            slow: Speak slowly
        
        Returns:
            Dictionary with synthesis result
        """
        if not text.strip():
            return {
                "success": False,
                "error": "Empty text provided"
            }
        
        try:
            # Map language codes
            lang_code = self._map_language_code(language)
            
            logger.info(f"Synthesizing speech in {lang_code}: {text[:50]}...")
            
            # Create gTTS object
            tts = gTTS(text=text, lang=lang_code, slow=slow)
            
            # Save to file or return bytes
            if output_path:
                tts.save(output_path)
                logger.info(f"Audio saved to: {output_path}")
                
                return {
                    "success": True,
                    "text": text,
                    "language": language,
                    "output_path": output_path
                }
            else:
                # Return audio as bytes
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                audio_fp.seek(0)
                audio_data = audio_fp.read()
                
                return {
                    "success": True,
                    "text": text,
                    "language": language,
                    "audio_data": audio_data
                }
            
        except Exception as e:
            logger.error(f"Speech synthesis error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "text": text
            }
    
    def synthesize_to_file(
        self,
        text: str,
        language: str,
        output_path: str,
        slow: bool = False
    ) -> bool:
        """
        Synthesize speech and save to file
        
        Args:
            text: Text to synthesize
            language: Language code
            output_path: Path to save audio file
            slow: Speak slowly
        
        Returns:
            True if successful
        """
        result = self.synthesize_speech(text, language, output_path, slow)
        return result.get("success", False)
    
    def synthesize_batch(
        self,
        texts: list,
        language: str,
        output_dir: str,
        slow: bool = False
    ) -> list:
        """
        Synthesize multiple texts
        
        Args:
            texts: List of texts to synthesize
            language: Language code
            output_dir: Directory to save audio files
            slow: Speak slowly
        
        Returns:
            List of synthesis results
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        for i, text in enumerate(texts):
            output_path = output_dir / f"audio_{i+1}.mp3"
            result = self.synthesize_speech(text, language, str(output_path), slow)
            results.append(result)
        
        return results
    
    def synthesize_multiple_languages(
        self,
        translations: Dict[str, str],
        output_dir: str
    ) -> Dict[str, Dict]:
        """
        Synthesize translations in multiple languages
        
        Args:
            translations: Dictionary mapping language codes to translated text
            output_dir: Directory to save audio files
        
        Returns:
            Dictionary mapping language codes to synthesis results
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        for lang, text in translations.items():
            output_path = output_dir / f"audio_{lang}.mp3"
            result = self.synthesize_speech(text, lang, str(output_path))
            results[lang] = result
        
        return results
    
    def _map_language_code(self, language: str) -> str:
        """
        Map language codes to gTTS format
        
        Args:
            language: Language code (e.g., 'en-US', 'hi-IN')
        
        Returns:
            gTTS language code
        """
        # Extract base language code
        base_lang = language.split("-")[0].lower()
        
        # gTTS uses simple 2-letter codes
        lang_map = {
            "en": "en",
            "hi": "hi",
            "es": "es",
            "fr": "fr",
            "de": "de",
            "it": "it",
            "pt": "pt",
            "ja": "ja",
            "ko": "ko",
            "zh": "zh-CN",
            "ar": "ar",
            "ru": "ru",
            "tr": "tr",
            "nl": "nl"
        }
        
        return lang_map.get(base_lang, "en")
    
    @staticmethod
    def get_supported_languages() -> list:
        """Get list of supported languages"""
        return [
            "en", "hi", "es", "fr", "de", "it", "pt", "ja", 
            "ko", "zh-CN", "ar", "ru", "tr", "nl", "bn", "ta",
            "te", "mr", "gu", "kn", "ml", "pa"
        ]
    
    @staticmethod
    def is_language_supported(language: str) -> bool:
        """Check if language is supported"""
        base_lang = language.split("-")[0].lower()
        return base_lang in GTTSTextToSpeech.get_supported_languages()
