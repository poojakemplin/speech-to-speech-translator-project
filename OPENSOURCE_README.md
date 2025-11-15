# Open-Source Speech Translation Pipeline

## Overview

This is a **completely open-source** alternative to the Azure-based implementation, using:
- **Whisper** (OpenAI) for Speech-to-Text
- **Helsinki-NLP MarianMT** for Translation
- **gTTS** (Google Text-to-Speech) for Text-to-Speech

## ✨ Key Advantages

✅ **No API Keys Required** - Fully open-source models  
✅ **Works Offline** - After initial model download  
✅ **Free to Use** - No cloud service costs  
✅ **Privacy-Friendly** - All processing happens locally  
✅ **Customizable** - Full control over models and parameters  

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: First run will download models automatically (~500MB-1GB)

### 2. Basic Usage

```python
from opensource_models import OpenSourcePipeline

# Initialize pipeline
pipeline = OpenSourcePipeline(whisper_model="base")

# Process audio file
result = pipeline.process_audio(
    audio_path="your_audio.wav",
    source_language="hi",  # Hindi
    target_languages=["en", "es", "fr"],
    output_dir="output"
)

# Access results
print(f"Transcription: {result['transcription']['text']}")
print(f"Translations: {result['translations']}")
print(f"Audio files: {result['audio_outputs']}")
```

## 📋 Pipeline Steps

### Step 1: Audio Input
- Upload or record audio (Hindi/English)
- Supported formats: WAV, MP3, M4A, FLAC, etc.

### Step 2: Audio Conversion (pydub)
```python
from opensource_models import AudioProcessor

processor = AudioProcessor()
converted = processor.convert_to_wav(
    "input.mp3",
    output_path="output.wav",
    sample_rate=16000,  # 16 kHz
    channels=1  # Mono
)
```

### Step 3: Speech-to-Text (Whisper)
```python
from opensource_models import WhisperSTT

stt = WhisperSTT(model_size="base")
result = stt.transcribe_audio("audio.wav", language="hi")

print(result['text'])  # "नमस्ते, आप कैसे हैं?"
```

### Step 4: Machine Translation (Helsinki-NLP)
```python
from opensource_models import HelsinkiTranslator

translator = HelsinkiTranslator()
result = translator.translate_text(
    text="नमस्ते, आप कैसे हैं?",
    source_lang="hi",
    target_lang="en"
)

print(result['translated_text'])  # "Hello, how are you?"
```

### Step 5: Text-to-Speech (gTTS)
```python
from opensource_models import GTTSTextToSpeech

tts = GTTSTextToSpeech()
result = tts.synthesize_speech(
    text="Hello, how are you?",
    language="en",
    output_path="output.mp3"
)
```

### Step 6: Batch Processing
```python
audio_files = ["audio1.wav", "audio2.wav", "audio3.wav"]

results = pipeline.process_batch(
    audio_files=audio_files,
    source_language="en",
    target_languages=["hi", "es", "fr"],
    output_dir="batch_output"
)

# Returns: List of tuples (audio_file, result_dict)
for audio_file, result in results:
    print(f"{audio_file}: {result['transcription']['text']}")
```

## 🎯 Use Cases

### 1. Live Sports Commentary Translation
```python
# Process live commentary
result = pipeline.process_audio(
    audio_path="cricket_commentary.wav",
    source_language="en",
    target_languages=["hi", "es", "fr", "de"],
    output_dir="commentary_output"
)
```

### 2. Educational Content
```python
# Translate lecture audio
result = pipeline.process_audio(
    audio_path="lecture.wav",
    source_language="en",
    target_languages=["hi", "es", "zh"],
    output_dir="lecture_translations"
)
```

### 3. News Broadcasting
```python
# Batch process news segments
news_files = ["news1.wav", "news2.wav", "news3.wav"]
results = pipeline.process_batch(
    audio_files=news_files,
    source_language="en",
    target_languages=["hi", "es", "ar"],
    output_dir="news_output"
)
```

## 🔧 Model Selection

### Whisper Models

| Model | Size | VRAM | Speed | Use Case |
|-------|------|------|-------|----------|
| tiny | 39M | ~1GB | ~32x | Quick testing |
| base | 74M | ~1GB | ~16x | **Recommended** |
| small | 244M | ~2GB | ~6x | Better accuracy |
| medium | 769M | ~5GB | ~2x | High accuracy |
| large | 1550M | ~10GB | ~1x | Best accuracy |

```python
# Choose model based on your needs
pipeline = OpenSourcePipeline(whisper_model="base")  # Balanced
pipeline = OpenSourcePipeline(whisper_model="small")  # More accurate
pipeline = OpenSourcePipeline(whisper_model="large")  # Best quality
```

### GPU Acceleration

```python
# Automatically uses GPU if available
pipeline = OpenSourcePipeline(whisper_model="base", device="cuda")

# Force CPU
pipeline = OpenSourcePipeline(whisper_model="base", device="cpu")
```

## 🌍 Supported Languages

### Whisper STT (99 languages)
English, Hindi, Spanish, French, German, Italian, Portuguese, Japanese, Korean, Chinese, Arabic, Russian, Turkish, Dutch, and 85+ more

### Helsinki-NLP Translation
Common language pairs available:
- English ↔ Hindi, Spanish, French, German, Italian, Portuguese
- English ↔ Japanese, Korean, Chinese, Arabic, Russian
- And many more combinations

### gTTS (50+ languages)
English, Hindi, Spanish, French, German, Italian, Portuguese, Japanese, Korean, Chinese, Arabic, Russian, Turkish, Dutch, Bengali, Tamil, Telugu, and more

## 📊 Performance Comparison

### Open-Source vs Azure

| Feature | Open-Source | Azure |
|---------|-------------|-------|
| **Cost** | Free | ~$4-8/hour |
| **Privacy** | Local processing | Cloud-based |
| **Internet** | Offline capable | Requires connection |
| **Setup** | Model download | API keys needed |
| **Latency** | Depends on hardware | ~2-5 seconds |
| **Quality** | Excellent | Excellent |
| **Customization** | Full control | Limited |

### Typical Processing Times (base model, CPU)

| Audio Duration | Processing Time |
|----------------|-----------------|
| 10 seconds | ~2-3 seconds |
| 1 minute | ~10-15 seconds |
| 5 minutes | ~45-60 seconds |

**With GPU**: 5-10x faster

## 🛠️ Advanced Usage

### Individual Components

```python
from opensource_models import WhisperSTT, HelsinkiTranslator, GTTSTextToSpeech

# Use components separately
stt = WhisperSTT(model_size="base")
translator = HelsinkiTranslator()
tts = GTTSTextToSpeech()

# Transcribe
transcription = stt.transcribe_audio("audio.wav", language="hi")

# Translate
translation = translator.translate_text(
    transcription['text'],
    source_lang="hi",
    target_lang="en"
)

# Synthesize
tts.synthesize_speech(
    translation['translated_text'],
    language="en",
    output_path="output.mp3"
)
```

### Language Detection

```python
# Auto-detect language
stt = WhisperSTT(model_size="base")
detection = stt.detect_language("audio.wav")

print(f"Detected: {detection['language']}")
print(f"Confidence: {detection['confidence']}")
```

### Batch Translation

```python
translator = HelsinkiTranslator()

texts = [
    "Hello world",
    "How are you?",
    "Good morning"
]

results = translator.translate_batch(
    texts=texts,
    source_lang="en",
    target_lang="hi"
)
```

## 📝 Examples

### Example 1: Simple Translation
```bash
python examples/test_opensource_pipeline.py
```

### Example 2: Complete Workflow Demo
```bash
python examples/demo_complete_workflow.py
```

### Example 3: Custom Script
```python
from opensource_models import OpenSourcePipeline

pipeline = OpenSourcePipeline(whisper_model="base")

# Hindi to English + Spanish
result = pipeline.process_audio(
    audio_path="hindi_speech.wav",
    source_language="hi",
    target_languages=["en", "es"],
    output_dir="my_output"
)

print(f"Hindi: {result['transcription']['text']}")
print(f"English: {result['translations']['en']}")
print(f"Spanish: {result['translations']['es']}")
```

## 🐛 Troubleshooting

### Issue: Models not downloading

**Solution**:
```bash
# Manually download Whisper model
python -c "import whisper; whisper.load_model('base')"

# Check internet connection
# Models are cached in ~/.cache/whisper/
```

### Issue: CUDA out of memory

**Solution**:
```python
# Use smaller model
pipeline = OpenSourcePipeline(whisper_model="tiny")

# Or force CPU
pipeline = OpenSourcePipeline(whisper_model="base", device="cpu")
```

### Issue: Translation model not found

**Solution**:
```python
# Some language pairs may not be available
# Check supported pairs:
from opensource_models import HelsinkiTranslator
pairs = HelsinkiTranslator.get_supported_language_pairs()
print(pairs)
```

### Issue: Audio format not supported

**Solution**:
```bash
# Install ffmpeg
# Windows: Download from ffmpeg.org
# Linux: sudo apt-get install ffmpeg
# Mac: brew install ffmpeg
```

## 🔄 Comparison with Azure Implementation

Both implementations are available in this project:

### Use Azure when:
- You need the absolute best quality
- You want minimal setup
- You have budget for cloud services
- You need enterprise support

### Use Open-Source when:
- You want zero cost
- Privacy is important
- You need offline capability
- You want full customization
- You're processing large volumes

## 📦 Model Downloads

First run will download:
- **Whisper base**: ~150MB
- **Helsinki-NLP models**: ~300MB per language pair
- **gTTS**: No download (uses Google API)

Models are cached for subsequent runs.

## 🎓 Learning Resources

- [Whisper Documentation](https://github.com/openai/whisper)
- [Helsinki-NLP Models](https://huggingface.co/Helsinki-NLP)
- [gTTS Documentation](https://gtts.readthedocs.io/)

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Add more translation models
- Optimize batch processing
- Implement streaming support
- Add quality metrics
- Create web interface

---

**Ready to translate!** 🚀

Start with: `python examples/demo_complete_workflow.py`
