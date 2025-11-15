"""
Example: Test Open-Source Pipeline
Demonstrates Whisper + Helsinki-NLP + gTTS pipeline
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from opensource_models import OpenSourcePipeline
from pathlib import Path


def main():
    """Test open-source pipeline"""
    print("=" * 60)
    print("Open-Source Speech Translation Pipeline Test")
    print("Whisper (STT) → Helsinki-NLP (MT) → gTTS (TTS)")
    print("=" * 60)
    
    # Initialize pipeline
    print("\n1. Initializing pipeline...")
    print("   - Whisper: base model")
    print("   - Helsinki-NLP: MarianMT models")
    print("   - gTTS: Google Text-to-Speech")
    
    pipeline = OpenSourcePipeline(whisper_model="base")
    
    # Example 1: Transcribe only
    print("\n2. Example 1: Transcription Only")
    print("   Note: You need an audio file to test this")
    print("   Usage: pipeline.transcribe_only('path/to/audio.wav', language='hi')")
    
    # Example 2: Translate only
    print("\n3. Example 2: Translation Only")
    test_text = "नमस्ते, आप कैसे हैं?"
    print(f"   Original (Hindi): {test_text}")
    
    translations = pipeline.translate_only(
        text=test_text,
        source_lang="hi",
        target_langs=["en", "es", "fr"]
    )
    
    for lang, translated in translations.items():
        print(f"   {lang}: {translated}")
    
    # Example 3: Synthesize only
    print("\n4. Example 3: Text-to-Speech Only")
    print("   Synthesizing translations to speech...")
    
    audio_files = pipeline.synthesize_only(
        translations=translations,
        output_dir="tts_output"
    )
    
    for lang, audio_path in audio_files.items():
        if audio_path:
            print(f"   {lang}: {audio_path}")
    
    # Example 4: Complete pipeline
    print("\n5. Example 4: Complete Pipeline")
    print("   To test complete pipeline with audio file:")
    print("""
   result = pipeline.process_audio(
       audio_path="your_audio.wav",
       source_language="hi",
       target_languages=["en", "es", "fr"],
       output_dir="output"
   )
   
   print(f"Transcription: {result['transcription']['text']}")
   print(f"Translations: {result['translations']}")
   print(f"Audio outputs: {result['audio_outputs']}")
   """)
    
    # Example 5: Batch processing
    print("\n6. Example 5: Batch Processing")
    print("   To process multiple audio files:")
    print("""
   audio_files = ["audio1.wav", "audio2.wav", "audio3.wav"]
   
   results = pipeline.process_batch(
       audio_files=audio_files,
       source_language="hi",
       target_languages=["en", "es"],
       output_dir="batch_output"
   )
   
   for audio_file, result in results:
       print(f"File: {audio_file}")
       print(f"Transcription: {result['transcription']['text']}")
   """)
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Record or upload audio files (Hindi/English)")
    print("2. Use pipeline.process_audio() for complete translation")
    print("3. Check output directory for generated audio files")
    print("\nModel downloads:")
    print("- Whisper models: Downloaded automatically on first use")
    print("- Helsinki-NLP: Downloaded automatically per language pair")
    print("- gTTS: No download required (uses Google API)")


if __name__ == "__main__":
    main()
