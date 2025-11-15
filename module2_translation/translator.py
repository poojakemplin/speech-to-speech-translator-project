"""
Module 2: Translation Model Development and Training
Azure OpenAI-based translation for real-time speech translation
"""
from openai import AzureOpenAI
from typing import List, Dict, Optional
from loguru import logger
import asyncio
import time
from datetime import datetime


class AzureOpenAITranslator:
    """Translation service using Azure OpenAI"""
    
    def __init__(
        self,
        api_key: str,
        endpoint: str,
        deployment_name: str,
        api_version: str = "2023-12-01-preview"
    ):
        """
        Initialize Azure OpenAI translator
        
        Args:
            api_key: Azure OpenAI API key
            endpoint: Azure OpenAI endpoint URL
            deployment_name: Deployment name
            api_version: API version
        """
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        self.deployment_name = deployment_name
        
        # Translation cache for performance
        self.translation_cache = {}
        
        logger.info(f"Azure OpenAI translator initialized with deployment: {deployment_name}")
    
    def translate_text(
        self,
        text: str,
        source_language: str,
        target_language: str,
        context: Optional[str] = None
    ) -> Dict:
        """
        Translate text from source to target language
        
        Args:
            text: Text to translate
            source_language: Source language code
            target_language: Target language code
            context: Optional context for better translation
        
        Returns:
            Dictionary with translation result
        """
        if not text.strip():
            return {
                "success": False,
                "error": "Empty text provided"
            }
        
        # Check cache
        cache_key = f"{text}:{source_language}:{target_language}"
        if cache_key in self.translation_cache:
            logger.debug(f"Cache hit for translation: {text[:50]}...")
            return self.translation_cache[cache_key]
        
        start_time = time.time()
        
        try:
            # Create translation prompt
            system_prompt = self._create_system_prompt(source_language, target_language)
            user_prompt = self._create_user_prompt(text, context)
            
            # Call Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            translated_text = response.choices[0].message.content.strip()
            latency = time.time() - start_time
            
            result = {
                "success": True,
                "original_text": text,
                "translated_text": translated_text,
                "source_language": source_language,
                "target_language": target_language,
                "latency": latency,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache the result
            self.translation_cache[cache_key] = result
            
            logger.info(f"Translation completed in {latency:.2f}s: {text[:50]}... -> {translated_text[:50]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "original_text": text,
                "source_language": source_language,
                "target_language": target_language
            }
    
    def _create_system_prompt(self, source_lang: str, target_lang: str) -> str:
        """Create system prompt for translation"""
        return f"""You are a professional translator specializing in real-time speech translation.
Your task is to translate text from {source_lang} to {target_lang} accurately and naturally.

Guidelines:
- Maintain the original meaning and tone
- Use natural, conversational language appropriate for live commentary
- Preserve technical terms and proper nouns when appropriate
- Keep translations concise and clear
- For sports commentary, maintain the excitement and energy
- Only output the translated text, nothing else"""
    
    def _create_user_prompt(self, text: str, context: Optional[str] = None) -> str:
        """Create user prompt for translation"""
        if context:
            return f"Context: {context}\n\nTranslate the following text:\n{text}"
        return f"Translate the following text:\n{text}"
    
    async def translate_text_async(
        self,
        text: str,
        source_language: str,
        target_language: str,
        context: Optional[str] = None
    ) -> Dict:
        """
        Asynchronous translation
        
        Args:
            text: Text to translate
            source_language: Source language code
            target_language: Target language code
            context: Optional context
        
        Returns:
            Dictionary with translation result
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.translate_text,
            text,
            source_language,
            target_language,
            context
        )
    
    def translate_batch(
        self,
        texts: List[str],
        source_language: str,
        target_language: str
    ) -> List[Dict]:
        """
        Translate multiple texts
        
        Args:
            texts: List of texts to translate
            source_language: Source language code
            target_language: Target language code
        
        Returns:
            List of translation results
        """
        results = []
        for text in texts:
            result = self.translate_text(text, source_language, target_language)
            results.append(result)
        
        return results
    
    async def translate_batch_async(
        self,
        texts: List[str],
        source_language: str,
        target_language: str
    ) -> List[Dict]:
        """
        Asynchronously translate multiple texts
        
        Args:
            texts: List of texts to translate
            source_language: Source language code
            target_language: Target language code
        
        Returns:
            List of translation results
        """
        tasks = [
            self.translate_text_async(text, source_language, target_language)
            for text in texts
        ]
        return await asyncio.gather(*tasks)
    
    def clear_cache(self):
        """Clear translation cache"""
        self.translation_cache.clear()
        logger.info("Translation cache cleared")


class MultiLanguageTranslator:
    """Manages translation to multiple target languages simultaneously"""
    
    def __init__(self, translator: AzureOpenAITranslator):
        """
        Initialize multi-language translator
        
        Args:
            translator: AzureOpenAITranslator instance
        """
        self.translator = translator
        self.target_languages = []
        logger.info("Multi-language translator initialized")
    
    def set_target_languages(self, languages: List[str]):
        """
        Set target languages for translation
        
        Args:
            languages: List of target language codes
        """
        self.target_languages = languages
        logger.info(f"Target languages set: {', '.join(languages)}")
    
    def translate_to_all_languages(
        self,
        text: str,
        source_language: str,
        context: Optional[str] = None
    ) -> Dict[str, Dict]:
        """
        Translate text to all target languages
        
        Args:
            text: Text to translate
            source_language: Source language code
            context: Optional context
        
        Returns:
            Dictionary mapping language codes to translation results
        """
        results = {}
        
        for target_lang in self.target_languages:
            if target_lang == source_language:
                # Skip translating to the same language
                results[target_lang] = {
                    "success": True,
                    "original_text": text,
                    "translated_text": text,
                    "source_language": source_language,
                    "target_language": target_lang,
                    "is_original": True
                }
            else:
                result = self.translator.translate_text(
                    text,
                    source_language,
                    target_lang,
                    context
                )
                results[target_lang] = result
        
        return results
    
    async def translate_to_all_languages_async(
        self,
        text: str,
        source_language: str,
        context: Optional[str] = None
    ) -> Dict[str, Dict]:
        """
        Asynchronously translate text to all target languages
        
        Args:
            text: Text to translate
            source_language: Source language code
            context: Optional context
        
        Returns:
            Dictionary mapping language codes to translation results
        """
        tasks = {}
        
        for target_lang in self.target_languages:
            if target_lang == source_language:
                tasks[target_lang] = asyncio.create_task(
                    asyncio.sleep(0, result={
                        "success": True,
                        "original_text": text,
                        "translated_text": text,
                        "source_language": source_language,
                        "target_language": target_lang,
                        "is_original": True
                    })
                )
            else:
                tasks[target_lang] = self.translator.translate_text_async(
                    text,
                    source_language,
                    target_lang,
                    context
                )
        
        results = {}
        for lang, task in tasks.items():
            results[lang] = await task
        
        return results
