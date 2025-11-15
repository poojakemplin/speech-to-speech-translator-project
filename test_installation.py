"""
Test Installation Script
Verifies all required packages are installed correctly
"""

print("=" * 60)
print("Testing Installation...")
print("=" * 60)

# Test 1: Check imports
print("\n1. Checking Core Packages:")
print("-" * 60)

try:
    import whisper
    print("✓ Whisper installed")
except ImportError as e:
    print(f"✗ Whisper not installed: {e}")

try:
    from transformers import MarianMTModel, MarianTokenizer
    print("✓ Transformers installed")
except ImportError as e:
    print(f"✗ Transformers not installed: {e}")

try:
    from gtts import gTTS
    print("✓ gTTS installed")
except ImportError as e:
    print(f"✗ gTTS not installed: {e}")

try:
    from pydub import AudioSegment
    print("✓ pydub installed")
except ImportError as e:
    print(f"✗ pydub not installed: {e}")

try:
    import torch
    print(f"✓ PyTorch installed (version: {torch.__version__})")
    print(f"  - CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  - CUDA version: {torch.version.cuda}")
except ImportError as e:
    print(f"✗ PyTorch not installed: {e}")

try:
    from fastapi import FastAPI
    print("✓ FastAPI installed")
except ImportError as e:
    print(f"✗ FastAPI not installed: {e}")

try:
    from loguru import logger
    print("✓ Loguru installed")
except ImportError as e:
    print(f"✗ Loguru not installed: {e}")

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv installed")
except ImportError as e:
    print(f"✗ python-dotenv not installed: {e}")

# Test 2: Check project modules
print("\n2. Checking Project Modules:")
print("-" * 60)

try:
    from opensource_models import WhisperSTT
    print("✓ WhisperSTT module available")
except ImportError as e:
    print(f"✗ WhisperSTT module not available: {e}")

try:
    from opensource_models import HelsinkiTranslator
    print("✓ HelsinkiTranslator module available")
except ImportError as e:
    print(f"✗ HelsinkiTranslator module not available: {e}")

try:
    from opensource_models import GTTSTextToSpeech
    print("✓ GTTSTextToSpeech module available")
except ImportError as e:
    print(f"✗ GTTSTextToSpeech module not available: {e}")

try:
    from opensource_models import OpenSourcePipeline
    print("✓ OpenSourcePipeline module available")
except ImportError as e:
    print(f"✗ OpenSourcePipeline module not available: {e}")

# Test 3: Quick functionality test
print("\n3. Quick Functionality Test:")
print("-" * 60)

try:
    from opensource_models import HelsinkiTranslator
    
    print("Testing translation...")
    translator = HelsinkiTranslator()
    
    # Simple translation test
    result = translator.translate_text(
        text="Hello world",
        source_lang="en",
        target_lang="es"
    )
    
    if result["success"]:
        print(f"✓ Translation works!")
        print(f"  Input: Hello world")
        print(f"  Output: {result['translated_text']}")
    else:
        print(f"✗ Translation failed: {result.get('error')}")
        
except Exception as e:
    print(f"✗ Translation test failed: {e}")

try:
    from opensource_models import GTTSTextToSpeech
    
    print("\nTesting text-to-speech...")
    tts = GTTSTextToSpeech()
    
    result = tts.synthesize_speech(
        text="Hello",
        language="en",
        output_path="test_audio.mp3"
    )
    
    if result["success"]:
        print(f"✓ Text-to-speech works!")
        print(f"  Audio saved to: {result['output_path']}")
    else:
        print(f"✗ Text-to-speech failed: {result.get('error')}")
        
except Exception as e:
    print(f"✗ TTS test failed: {e}")

# Summary
print("\n" + "=" * 60)
print("Installation Test Complete!")
print("=" * 60)
print("\n✓ If all tests passed, you're ready to use the pipeline!")
print("\nNext steps:")
print("1. Run: python examples/demo_complete_workflow.py")
print("2. Run: python examples/test_opensource_pipeline.py")
print("3. Test with your own audio files")
print("\n")
