"""
OTT Platform Integration Module
Integrates speech translation with OTT streaming platforms
"""
import asyncio
from typing import Dict, List, Optional, Callable
from loguru import logger
import aiohttp
import json
from datetime import datetime


class OTTPlatformIntegration:
    """Integration with OTT streaming platforms"""
    
    def __init__(
        self,
        platform_url: str,
        api_key: str,
        translation_pipeline
    ):
        """
        Initialize OTT platform integration
        
        Args:
            platform_url: OTT platform API URL
            api_key: API key for authentication
            translation_pipeline: Speech-to-speech pipeline instance
        """
        self.platform_url = platform_url
        self.api_key = api_key
        self.pipeline = translation_pipeline
        
        self.is_active = False
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info(f"OTT platform integration initialized: {platform_url}")
    
    async def connect(self):
        """Connect to OTT platform"""
        try:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            # Test connection
            async with self.session.get(f"{self.platform_url}/health") as response:
                if response.status == 200:
                    self.is_active = True
                    logger.info("Connected to OTT platform")
                else:
                    logger.error(f"Failed to connect: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            raise
    
    async def disconnect(self):
        """Disconnect from OTT platform"""
        if self.session:
            await self.session.close()
            self.is_active = False
            logger.info("Disconnected from OTT platform")
    
    async def register_translation_stream(
        self,
        stream_id: str,
        languages: List[str]
    ) -> Dict:
        """
        Register a new translation stream
        
        Args:
            stream_id: Original stream identifier
            languages: List of target languages
        
        Returns:
            Registration response
        """
        if not self.is_active:
            raise RuntimeError("Not connected to OTT platform")
        
        payload = {
            "stream_id": stream_id,
            "languages": languages,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            async with self.session.post(
                f"{self.platform_url}/streams/register",
                json=payload
            ) as response:
                result = await response.json()
                logger.info(f"Stream registered: {stream_id}")
                return result
                
        except Exception as e:
            logger.error(f"Stream registration error: {str(e)}")
            raise
    
    async def publish_translated_audio(
        self,
        stream_id: str,
        language: str,
        audio_data: bytes,
        metadata: Optional[Dict] = None
    ):
        """
        Publish translated audio to OTT platform
        
        Args:
            stream_id: Stream identifier
            language: Language code
            audio_data: Translated audio data
            metadata: Optional metadata
        """
        if not self.is_active:
            raise RuntimeError("Not connected to OTT platform")
        
        try:
            # Prepare multipart data
            data = aiohttp.FormData()
            data.add_field('stream_id', stream_id)
            data.add_field('language', language)
            data.add_field('audio', audio_data, filename=f'{language}.wav')
            
            if metadata:
                data.add_field('metadata', json.dumps(metadata))
            
            async with self.session.post(
                f"{self.platform_url}/streams/publish",
                data=data
            ) as response:
                if response.status == 200:
                    logger.debug(f"Published audio for {language}")
                else:
                    logger.error(f"Publish failed: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"Publish error: {str(e)}")
    
    async def start_live_translation(
        self,
        stream_id: str,
        source_language: str,
        target_languages: List[str]
    ):
        """
        Start live translation for a stream
        
        Args:
            stream_id: Stream identifier
            source_language: Source language code
            target_languages: List of target language codes
        """
        logger.info(f"Starting live translation for stream: {stream_id}")
        
        # Register stream
        await self.register_translation_stream(stream_id, target_languages)
        
        # Start translation pipeline
        # This would connect to the actual audio stream
        # For now, this is a placeholder for the integration logic
        
        logger.info(f"Live translation started for stream: {stream_id}")
    
    async def stop_live_translation(self, stream_id: str):
        """
        Stop live translation for a stream
        
        Args:
            stream_id: Stream identifier
        """
        if not self.is_active:
            return
        
        try:
            async with self.session.post(
                f"{self.platform_url}/streams/stop",
                json={"stream_id": stream_id}
            ) as response:
                if response.status == 200:
                    logger.info(f"Stopped translation for stream: {stream_id}")
                    
        except Exception as e:
            logger.error(f"Stop translation error: {str(e)}")


class MultiDeviceDelivery:
    """Manages delivery of translated content to multiple devices"""
    
    def __init__(self):
        """Initialize multi-device delivery manager"""
        self.active_connections = {}
        logger.info("Multi-device delivery manager initialized")
    
    async def register_device(
        self,
        device_id: str,
        preferred_language: str,
        device_type: str
    ):
        """
        Register a device for content delivery
        
        Args:
            device_id: Device identifier
            preferred_language: Preferred language
            device_type: Type of device (mobile, tv, web, etc.)
        """
        self.active_connections[device_id] = {
            "language": preferred_language,
            "device_type": device_type,
            "connected_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        logger.info(f"Device registered: {device_id} ({device_type}, {preferred_language})")
    
    async def unregister_device(self, device_id: str):
        """
        Unregister a device
        
        Args:
            device_id: Device identifier
        """
        if device_id in self.active_connections:
            del self.active_connections[device_id]
            logger.info(f"Device unregistered: {device_id}")
    
    async def deliver_content(
        self,
        stream_id: str,
        audio_data_by_language: Dict[str, bytes]
    ):
        """
        Deliver translated content to all connected devices
        
        Args:
            stream_id: Stream identifier
            audio_data_by_language: Dictionary mapping languages to audio data
        """
        for device_id, device_info in self.active_connections.items():
            language = device_info["language"]
            
            if language in audio_data_by_language:
                audio_data = audio_data_by_language[language]
                await self._send_to_device(device_id, audio_data, stream_id)
    
    async def _send_to_device(
        self,
        device_id: str,
        audio_data: bytes,
        stream_id: str
    ):
        """
        Send audio data to specific device
        
        Args:
            device_id: Device identifier
            audio_data: Audio data
            stream_id: Stream identifier
        """
        # Implement actual device delivery logic
        # This would depend on the device type and delivery protocol
        logger.debug(f"Sending content to device: {device_id}")
    
    def get_active_devices(self) -> List[Dict]:
        """
        Get list of active devices
        
        Returns:
            List of device information
        """
        return [
            {"device_id": device_id, **info}
            for device_id, info in self.active_connections.items()
        ]


class StreamQualityMonitor:
    """Monitors quality of translated streams"""
    
    def __init__(self):
        """Initialize stream quality monitor"""
        self.quality_metrics = {}
        logger.info("Stream quality monitor initialized")
    
    def record_metric(
        self,
        stream_id: str,
        metric_type: str,
        value: float
    ):
        """
        Record quality metric
        
        Args:
            stream_id: Stream identifier
            metric_type: Type of metric (latency, quality, etc.)
            value: Metric value
        """
        if stream_id not in self.quality_metrics:
            self.quality_metrics[stream_id] = {}
        
        if metric_type not in self.quality_metrics[stream_id]:
            self.quality_metrics[stream_id][metric_type] = []
        
        self.quality_metrics[stream_id][metric_type].append({
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_stream_quality(self, stream_id: str) -> Dict:
        """
        Get quality metrics for a stream
        
        Args:
            stream_id: Stream identifier
        
        Returns:
            Quality metrics dictionary
        """
        if stream_id not in self.quality_metrics:
            return {"error": "No metrics available"}
        
        metrics = self.quality_metrics[stream_id]
        summary = {}
        
        for metric_type, values in metrics.items():
            metric_values = [v["value"] for v in values]
            summary[metric_type] = {
                "current": metric_values[-1] if metric_values else 0,
                "average": sum(metric_values) / len(metric_values) if metric_values else 0,
                "min": min(metric_values) if metric_values else 0,
                "max": max(metric_values) if metric_values else 0
            }
        
        return summary
    
    def check_quality_threshold(
        self,
        stream_id: str,
        metric_type: str,
        threshold: float
    ) -> bool:
        """
        Check if quality meets threshold
        
        Args:
            stream_id: Stream identifier
            metric_type: Type of metric
            threshold: Threshold value
        
        Returns:
            True if quality meets threshold
        """
        quality = self.get_stream_quality(stream_id)
        
        if metric_type in quality:
            return quality[metric_type]["average"] <= threshold
        
        return False
