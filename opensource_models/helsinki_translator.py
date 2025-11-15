"""
Open-Source Translation using Helsinki-NLP Models
Alternative to Azure OpenAI Translation
"""
from transformers import MarianMTModel, MarianTokenizer
from typing import Dict, List, Optional
from loguru import logger
import torch


class HelsinkiTranslator:
    """Translation using Helsinki-NLP MarianMT models"""
    
    def __init__(self, device: Optional[str] = None):
        """
        Initialize Helsinki translator
        
        Args:
            device: Device to run on (cuda/cpu). Auto-detect if None
        """
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        self.models = {}
        self.tokenizers = {}
        
        logger.info(f"Helsinki translator initialized on {self.device}")
    
    def _get_model_name(self, source_lang: str, target_lang: str) -> str:
        """
        Get Helsinki-NLP model name for language pair
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            Model name
        """
        # Map language codes to Helsinki-NLP format
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
            "zh": "zh",
            "ar": "ar",
            "ru": "ru",
            "tr": "tr",
            "nl": "nl"
        }
        
        src = lang_map.get(source_lang.split("-")[0], source_lang)
        tgt = lang_map.get(target_lang.split("-")[0], target_lang)
        
        # Helsinki-NLP model naming convention
        return f"Helsinki-NLP/opus-mt-{src}-{tgt}"
    
    def load_model(self, source_lang: str, target_lang: str):
        """
        Load translation model for language pair
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
        """
        model_name = self._get_model_name(source_lang, target_lang)
        
        if model_name in self.models:
            logger.debug(f"Model already loaded: {model_name}")
            return
        
        try:
            logger.info(f"Loading model: {model_name}")
            
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name).to(self.device)
            
            self.tokenizers[model_name] = tokenizer
            self.models[model_name] = model
            
            logger.info(f"Model loaded successfully: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            raise
    
    def _needs_pivot_translation(self, source_lang: str, target_lang: str) -> bool:
        """Check if translation needs to go through English as pivot"""
        # Direct translation pairs that exist
        direct_pairs = [
            ("en", "hi"), ("hi", "en"),
            ("en", "es"), ("es", "en"),
            ("en", "fr"), ("fr", "en"),
            ("en", "de"), ("de", "en"),
            ("en", "it"), ("it", "en"),
            ("en", "pt"), ("pt", "en"),
            ("en", "ja"), ("ja", "en"),
            ("en", "zh"), ("zh", "en"),
            ("en", "ar"), ("ar", "en"),
            ("en", "ru"), ("ru", "en"),
            ("en", "ko"), ("ko", "en"),
            ("en", "tr"), ("tr", "en"),
            ("en", "nl"), ("nl", "en"),
        ]
        
        src = source_lang.split("-")[0]
        tgt = target_lang.split("-")[0]
        
        return (src, tgt) not in direct_pairs
    
    def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        max_length: int = 512
    ) -> Dict:
        """
        Translate text from source to target language
        Uses pivot translation through English if direct model unavailable
        
        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en', 'hi')
            target_lang: Target language code
            max_length: Maximum length of translation
        
        Returns:
            Dictionary with translation result
        """
        if not text.strip():
            return {
                "success": False,
                "error": "Empty text provided"
            }
        
        try:
            # Check if we need pivot translation
            if self._needs_pivot_translation(source_lang, target_lang):
                logger.info(f"Using pivot translation: {source_lang} → en → {target_lang}")
                
                # Step 1: Translate to English
                if source_lang.split("-")[0] != "en":
                    intermediate = self.translate_text(text, source_lang, "en", max_length)
                    if not intermediate["success"]:
                        return intermediate
                    text = intermediate["translated_text"]
                    source_lang = "en"
                
                # Step 2: Translate from English to target
                if target_lang.split("-")[0] != "en":
                    return self.translate_text(text, "en", target_lang, max_length)
            
            # Direct translation
            # Load model if not already loaded
            model_name = self._get_model_name(source_lang, target_lang)
            if model_name not in self.models:
                self.load_model(source_lang, target_lang)
            
            tokenizer = self.tokenizers[model_name]
            model = self.models[model_name]
            
            # Tokenize
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Translate
            with torch.no_grad():
                outputs = model.generate(**inputs, max_length=max_length)
            
            # Decode
            translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return {
                "success": True,
                "original_text": text,
                "translated_text": translated_text,
                "source_language": source_lang,
                "target_language": target_lang,
                "model": model_name
            }
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "original_text": text
            }
    
    def translate_batch(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str,
        max_length: int = 512
    ) -> List[Dict]:
        """
        Translate multiple texts
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            max_length: Maximum length of translations
        
        Returns:
            List of translation results
        """
        try:
            # Load model if not already loaded
            model_name = self._get_model_name(source_lang, target_lang)
            if model_name not in self.models:
                self.load_model(source_lang, target_lang)
            
            tokenizer = self.tokenizers[model_name]
            model = self.models[model_name]
            
            # Tokenize batch
            inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Translate
            with torch.no_grad():
                outputs = model.generate(**inputs, max_length=max_length)
            
            # Decode all
            translated_texts = [
                tokenizer.decode(output, skip_special_tokens=True)
                for output in outputs
            ]
            
            # Format results
            results = []
            for original, translated in zip(texts, translated_texts):
                results.append({
                    "success": True,
                    "original_text": original,
                    "translated_text": translated,
                    "source_language": source_lang,
                    "target_language": target_lang
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Batch translation error: {str(e)}")
            return [{
                "success": False,
                "error": str(e),
                "original_text": text
            } for text in texts]
    
    def translate_to_multiple_languages(
        self,
        text: str,
        source_lang: str,
        target_langs: List[str]
    ) -> Dict[str, Dict]:
        """
        Translate text to multiple target languages
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_langs: List of target language codes
        
        Returns:
            Dictionary mapping language codes to translation results
        """
        results = {}
        
        for target_lang in target_langs:
            if target_lang == source_lang:
                results[target_lang] = {
                    "success": True,
                    "original_text": text,
                    "translated_text": text,
                    "is_original": True
                }
            else:
                results[target_lang] = self.translate_text(text, source_lang, target_lang)
        
        return results
    
    def clear_cache(self):
        """Clear loaded models from memory"""
        self.models.clear()
        self.tokenizers.clear()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        logger.info("Model cache cleared")
    
    @staticmethod
    def get_supported_language_pairs() -> List[tuple]:
        """Get list of commonly supported language pairs"""
        # Common language pairs available in Helsinki-NLP
        pairs = [
            ("en", "hi"), ("hi", "en"),
            ("en", "es"), ("es", "en"),
            ("en", "fr"), ("fr", "en"),
            ("en", "de"), ("de", "en"),
            ("en", "it"), ("it", "en"),
            ("en", "pt"), ("pt", "en"),
            ("en", "ja"), ("ja", "en"),
            ("en", "zh"), ("zh", "en"),
            ("en", "ar"), ("ar", "en"),
            ("en", "ru"), ("ru", "en"),
        ]
        return pairs
