# AI-Powered Real-Time Speech Translation for Multilingual Content

A comprehensive real-time speech-to-speech translation system that converts live commentary or spoken content from English/Hindi into 12+ languages, designed for seamless integration with OTT digital feeds.

## 🎯 Project Overview

This system utilizes **Azure OpenAI** and **Azure Speech-to-Text** technologies to achieve real-time translation, ensuring smooth integration into existing media platforms and enhancing the viewing experience for a multilingual audience.

## ✨ Key Features

- **Real-time Speech Translation**: Convert live commentary from English/Hindi to 12+ languages in real-time
- **Seamless Integration**: Embed translated speech into OTT digital feeds without affecting user experience
- **Wide Language Support**: Support for 14+ languages with scalable expansion
- **Enhanced Accessibility**: Improve content accessibility for diverse audiences
- **Low Latency**: Optimized pipeline for minimal translation delay
- **High Quality**: Azure Neural TTS voices for natural-sounding output

## 🌍 Supported Languages

- English (en-US)
- Hindi (hi-IN)
- Spanish (es-ES)
- French (fr-FR)
- German (de-DE)
- Italian (it-IT)
- Portuguese (pt-BR)
- Japanese (ja-JP)
- Korean (ko-KR)
- Chinese Simplified (zh-CN)
- Arabic (ar-SA)
- Russian (ru-RU)
- Turkish (tr-TR)
- Dutch (nl-NL)

## 📋 Prerequisites

- Python 3.8 or higher
- Azure subscription with:
  - Azure Speech Services
  - Azure OpenAI Service
- Windows/Linux/macOS operating system
- Microphone (for live speech input)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
cd speech_translation

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your Azure credentials
# Required:
# - AZURE_SPEECH_KEY
# - AZURE_SPEECH_REGION
# - AZURE_OPENAI_KEY
# - AZURE_OPENAI_ENDPOINT
```

### 3. Run the API Server

```bash
# Start the FastAPI server
python module4_deployment/api_server.py

# Server will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

## 📚 Module Documentation

### Module 1: Speech Recognition and Data Collection

**Location**: `module1_speech_recognition/`

**Purpose**: Collect live speech data and enable accurate speech recognition for multiple languages.

**Key Components**:
- `SpeechRecognizer`: Real-time speech recognition using Azure Speech Services
- `MultiLanguageSpeechRecognizer`: Support for multiple source languages
- `SpeechDataCollector`: Collect and manage speech data for training
- `AudioPreprocessor`: Preprocess audio for better recognition

**Example Usage**:
```python
from module1_speech_recognition import SpeechRecognizer
from config import settings

# Initialize recognizer
recognizer = SpeechRecognizer(
    speech_key=settings.azure_speech_key,
    speech_region=settings.azure_speech_region,
    source_language="en-US"
)

# Setup microphone input
recognizer.setup_microphone_input()

# Set callbacks
def on_recognized(result):
    print(f"Recognized: {result['text']}")

recognizer.set_callbacks(on_recognized=on_recognized)

# Start recognition
recognizer.start_continuous_recognition()
```

### Module 2: Translation Model Development and Training

**Location**: `module2_translation/`

**Purpose**: Develop and train machine learning models for real-time speech-to-speech translation.

**Key Components**:
- `AzureOpenAITranslator`: Translation using Azure OpenAI
- `MultiLanguageTranslator`: Translate to multiple languages simultaneously
- `TranslationEvaluator`: Evaluate translation quality (BLEU, WER, CER)
- `LatencyEvaluator`: Monitor and optimize translation latency

**Example Usage**:
```python
from module2_translation import AzureOpenAITranslator, TranslationEvaluator
from config import settings

# Initialize translator
translator = AzureOpenAITranslator(
    api_key=settings.azure_openai_key,
    endpoint=settings.azure_openai_endpoint,
    deployment_name=settings.azure_openai_deployment_name
)

# Translate text
result = translator.translate_text(
    text="Hello, welcome to the game!",
    source_language="en-US",
    target_language="es-ES"
)

print(f"Translation: {result['translated_text']}")

# Evaluate translation quality
evaluator = TranslationEvaluator()
metrics = evaluator.evaluate_translation(
    reference="¡Hola, bienvenido al juego!",
    candidate=result['translated_text']
)
print(f"BLEU Score: {metrics['bleu_score']}")
```

### Module 3: Real-time Speech-to-Speech Integration

**Location**: `module3_realtime_integration/`

**Purpose**: Implement real-time speech-to-speech translation and integrate into digital feeds.

**Key Components**:
- `SpeechToSpeechPipeline`: Complete pipeline for real-time translation
- `StreamingPipeline`: Low-latency streaming translation
- `AudioStreamManager`: Manage audio streams
- `OTTStreamAdapter`: Adapter for OTT platform streams
- `LatencyOptimizer`: Optimize for minimal latency

**Example Usage**:
```python
from module3_realtime_integration import SpeechToSpeechPipeline
from module2_translation import AzureOpenAITranslator
from config import settings

# Initialize translator
translator = AzureOpenAITranslator(
    api_key=settings.azure_openai_key,
    endpoint=settings.azure_openai_endpoint,
    deployment_name=settings.azure_openai_deployment_name
)

# Initialize pipeline
pipeline = SpeechToSpeechPipeline(
    speech_key=settings.azure_speech_key,
    speech_region=settings.azure_speech_region,
    openai_translator=translator,
    source_language="en-US",
    target_languages=["es-ES", "fr-FR", "hi-IN"]
)

# Set callbacks
def on_translation_complete(translations):
    for lang, text in translations.items():
        print(f"{lang}: {text}")

pipeline.on_translation_complete = on_translation_complete

# Start pipeline
pipeline.start_pipeline()

# Keep running...
# pipeline.stop_pipeline() when done
```

### Module 4: Deployment and OTT Platform Integration

**Location**: `module4_deployment/`

**Purpose**: Deploy the translation system and integrate it with OTT platforms.

**Key Components**:
- `api_server.py`: FastAPI REST API server
- `OTTPlatformIntegration`: Integration with OTT platforms
- `MultiDeviceDelivery`: Deliver content to multiple devices
- `StreamQualityMonitor`: Monitor stream quality

**API Endpoints**:

```bash
# Health check
GET /health

# Get supported languages
GET /languages

# Translate text
POST /translate
{
  "text": "Hello world",
  "source_language": "en-US",
  "target_languages": ["es-ES", "fr-FR"]
}

# WebSocket for real-time translation
WS /ws/translate

# Speech recognition
POST /speech/recognize

# Complete speech-to-speech translation
POST /speech/translate
```

## 🔧 Configuration Options

Edit `config/settings.py` or `.env` file:

```python
# Azure Speech Services
AZURE_SPEECH_KEY=your_key
AZURE_SPEECH_REGION=eastus

# Azure OpenAI
AZURE_OPENAI_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Performance Settings
MAX_CONCURRENT_TRANSLATIONS=10
TRANSLATION_TIMEOUT=30
BUFFER_SIZE=4096

# Audio Settings
SAMPLE_RATE=16000
AUDIO_CHUNK_SIZE=1024
```

## 📊 Performance Metrics

The system includes comprehensive evaluation metrics:

- **BLEU Score**: Translation quality (0-1, higher is better)
- **WER (Word Error Rate)**: Recognition accuracy (lower is better)
- **CER (Character Error Rate)**: Character-level accuracy (lower is better)
- **Latency**: End-to-end translation time
- **Throughput**: Translations per second

## 🧪 Testing

```bash
# Run example scripts
python examples/test_speech_recognition.py
python examples/test_translation.py
python examples/test_full_pipeline.py

# Run API tests
python examples/test_api.py
```

## 🎬 Use Cases

1. **Live Sports Commentary**: Translate sports commentary in real-time for international audiences
2. **News Broadcasting**: Provide multilingual news feeds
3. **Educational Content**: Make educational videos accessible in multiple languages
4. **Entertainment Streaming**: Translate movies, shows, and live events
5. **Corporate Communications**: Multilingual webinars and presentations

## 🔒 Security Considerations

- Store API keys securely in environment variables
- Use HTTPS for production deployments
- Implement rate limiting for API endpoints
- Validate and sanitize all inputs
- Monitor for unusual usage patterns

## 📈 Scalability

The system is designed for scalability:

- **Horizontal Scaling**: Deploy multiple API server instances
- **Load Balancing**: Distribute requests across servers
- **Caching**: Translation cache reduces redundant API calls
- **Async Processing**: Non-blocking I/O for high concurrency
- **Queue Management**: Redis for managing translation queues

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Error**
   - Verify Azure credentials in `.env` file
   - Check subscription status

2. **High Latency**
   - Use Azure region closest to your location
   - Enable translation caching
   - Optimize audio chunk size

3. **Poor Recognition Quality**
   - Ensure good audio quality (16kHz sample rate)
   - Reduce background noise
   - Use appropriate language model

4. **API Rate Limits**
   - Implement request throttling
   - Use caching for repeated translations
   - Consider upgrading Azure tier

## 📝 License

This project is provided as-is for educational and commercial purposes.

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📧 Support

For issues and questions:
- Create an issue in the repository
- Check documentation at `/docs`
- Review API documentation at `/docs` endpoint

## 🎓 Additional Resources

- [Azure Speech Services Documentation](https://docs.microsoft.com/azure/cognitive-services/speech-service/)
- [Azure OpenAI Documentation](https://docs.microsoft.com/azure/cognitive-services/openai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🗺️ Roadmap

- [ ] Add support for more languages
- [ ] Implement custom voice training
- [ ] Add real-time quality adaptation
- [ ] Develop mobile SDKs
- [ ] Add offline translation support
- [ ] Implement advanced caching strategies
- [ ] Add monitoring dashboard
- [ ] Develop Kubernetes deployment configs

---

**Built with ❤️ using Azure AI Services**
