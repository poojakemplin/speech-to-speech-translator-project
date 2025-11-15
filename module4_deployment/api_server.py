"""
Module 4: Deployment and OTT Platform Integration
FastAPI server for speech translation services
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
from loguru import logger
import json
from datetime import datetime
import io

from config import settings
from module1_speech_recognition import SpeechRecognizer, SpeechDataCollector
from module2_translation import AzureOpenAITranslator, MultiLanguageTranslator
from module3_realtime_integration import SpeechToSpeechPipeline


# Initialize FastAPI app
app = FastAPI(
    title="Real-Time Speech Translation API",
    description="AI-Powered Real-Time Speech Translation for Multilingual Content",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_languages: List[str]
    context: Optional[str] = None


class TranslationResponse(BaseModel):
    success: bool
    original_text: str
    translations: Dict[str, str]
    source_language: str
    timestamp: str
    latency: Optional[float] = None


class LanguageInfo(BaseModel):
    code: str
    name: str
    supported: bool


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, bool]


# Global instances
translator = None
multi_translator = None
data_collector = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global translator, multi_translator, data_collector
    
    logger.info("Initializing speech translation services...")
    
    try:
        # Initialize translator
        translator = AzureOpenAITranslator(
            api_key=settings.azure_openai_key,
            endpoint=settings.azure_openai_endpoint,
            deployment_name=settings.azure_openai_deployment_name,
            api_version=settings.azure_openai_api_version
        )
        
        # Initialize multi-language translator
        multi_translator = MultiLanguageTranslator(translator)
        multi_translator.set_target_languages(settings.supported_languages)
        
        # Initialize data collector
        data_collector = SpeechDataCollector()
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise


@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "service": "Real-Time Speech Translation API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services_status = {
        "translator": translator is not None,
        "data_collector": data_collector is not None,
        "speech_services": bool(settings.azure_speech_key)
    }
    
    return HealthResponse(
        status="healthy" if all(services_status.values()) else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        services=services_status
    )


@app.get("/languages", response_model=List[LanguageInfo])
async def get_supported_languages():
    """Get list of supported languages"""
    language_names = {
        "en-US": "English (US)",
        "hi-IN": "Hindi (India)",
        "es-ES": "Spanish (Spain)",
        "fr-FR": "French (France)",
        "de-DE": "German (Germany)",
        "it-IT": "Italian (Italy)",
        "pt-BR": "Portuguese (Brazil)",
        "ja-JP": "Japanese (Japan)",
        "ko-KR": "Korean (Korea)",
        "zh-CN": "Chinese (Simplified)",
        "ar-SA": "Arabic (Saudi Arabia)",
        "ru-RU": "Russian (Russia)",
        "tr-TR": "Turkish (Turkey)",
        "nl-NL": "Dutch (Netherlands)"
    }
    
    return [
        LanguageInfo(
            code=code,
            name=language_names.get(code, code),
            supported=True
        )
        for code in settings.supported_languages
    ]


@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text to multiple target languages
    
    Args:
        request: Translation request with text and languages
    
    Returns:
        Translation response with results
    """
    if not translator:
        raise HTTPException(status_code=503, detail="Translation service not available")
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Translate to all target languages
        translations = {}
        for target_lang in request.target_languages:
            result = translator.translate_text(
                request.text,
                request.source_language,
                target_lang,
                request.context
            )
            
            if result["success"]:
                translations[target_lang] = result["translated_text"]
            else:
                translations[target_lang] = f"Error: {result.get('error', 'Unknown error')}"
        
        latency = asyncio.get_event_loop().time() - start_time
        
        return TranslationResponse(
            success=True,
            original_text=request.text,
            translations=translations,
            source_language=request.source_language,
            timestamp=datetime.utcnow().isoformat(),
            latency=latency
        )
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate/batch")
async def translate_batch(requests: List[TranslationRequest]):
    """
    Batch translation endpoint
    
    Args:
        requests: List of translation requests
    
    Returns:
        List of translation responses
    """
    results = []
    for req in requests:
        result = await translate_text(req)
        results.append(result)
    
    return results


@app.websocket("/ws/translate")
async def websocket_translate(websocket: WebSocket):
    """
    WebSocket endpoint for real-time translation
    
    Receives text and sends back translations in real-time
    """
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            text = message.get("text")
            source_lang = message.get("source_language", "en-US")
            target_langs = message.get("target_languages", ["es-ES"])
            
            # Translate
            translations = {}
            for target_lang in target_langs:
                result = await translator.translate_text_async(
                    text,
                    source_lang,
                    target_lang
                )
                
                if result["success"]:
                    translations[target_lang] = result["translated_text"]
            
            # Send response
            response = {
                "original_text": text,
                "translations": translations,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()


@app.post("/speech/recognize")
async def recognize_speech(
    audio_file: UploadFile = File(...),
    language: str = "en-US"
):
    """
    Recognize speech from audio file
    
    Args:
        audio_file: Audio file upload
        language: Source language code
    
    Returns:
        Recognition result
    """
    try:
        # Save uploaded file temporarily
        audio_data = await audio_file.read()
        temp_file = f"temp_audio_{datetime.utcnow().timestamp()}.wav"
        
        with open(temp_file, "wb") as f:
            f.write(audio_data)
        
        # Recognize speech
        recognizer = SpeechRecognizer(
            settings.azure_speech_key,
            settings.azure_speech_region,
            language
        )
        recognizer.setup_file_input(temp_file)
        
        result = await recognizer.recognize_once_async()
        
        # Clean up
        import os
        os.remove(temp_file)
        
        return result
        
    except Exception as e:
        logger.error(f"Speech recognition error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/speech/translate")
async def speech_to_speech_translate(
    audio_file: UploadFile = File(...),
    source_language: str = "en-US",
    target_languages: List[str] = ["es-ES"]
):
    """
    Complete speech-to-speech translation
    
    Args:
        audio_file: Audio file upload
        source_language: Source language code
        target_languages: List of target language codes
    
    Returns:
        Translation results with audio
    """
    try:
        # Recognize speech
        recognition_result = await recognize_speech(audio_file, source_language)
        
        if not recognition_result.get("success"):
            raise HTTPException(status_code=400, detail="Speech recognition failed")
        
        text = recognition_result["text"]
        
        # Translate
        translations = {}
        for target_lang in target_languages:
            result = translator.translate_text(
                text,
                source_language,
                target_lang
            )
            
            if result["success"]:
                translations[target_lang] = result["translated_text"]
        
        return {
            "success": True,
            "recognized_text": text,
            "translations": translations,
            "source_language": source_language,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Speech-to-speech translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats/collection")
async def get_collection_stats():
    """Get data collection statistics"""
    if not data_collector:
        raise HTTPException(status_code=503, detail="Data collector not available")
    
    return data_collector.get_collection_stats()


@app.post("/admin/clear-cache")
async def clear_translation_cache():
    """Clear translation cache (admin endpoint)"""
    if translator:
        translator.clear_cache()
        return {"success": True, "message": "Cache cleared"}
    
    raise HTTPException(status_code=503, detail="Translator not available")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
