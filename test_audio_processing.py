"""
Test Audio Processing
Process audio files through the complete pipeline
"""
from opensource_models import OpenSourcePipeline
import os

print("=" * 60)
print("Audio Processing Test")
print("=" * 60)

# Initialize pipeline
print("\nInitializing pipeline...")
pipeline = OpenSourcePipeline(whisper_model="base")
print("✓ Pipeline ready!")

# Instructions for testing
print("\n" + "=" * 60)
print("HOW TO TEST WITH AUDIO")
print("=" * 60)

print("""
1. PREPARE AUDIO FILE:
   - Record audio in Hindi or English (WAV format preferred)
   - Or convert existing audio to WAV
   - Place it in this directory
   - Name it: test_audio.wav

2. RUN THIS SCRIPT:
   python test_audio_processing.py

3. CHECK OUTPUT:
   - Transcription will be displayed
   - Translations in multiple languages
   - Audio files in 'audio_output' folder
""")

# Check if test audio exists
audio_file = "test_audio.wav"

if os.path.exists(audio_file):
    print(f"\n✓ Found audio file: {audio_file}")
    print("\nProcessing audio...")
    print("-" * 60)
    
    try:
        # Process the audio
        result = pipeline.process_audio(
            audio_path=audio_file,
            source_language="hi",  # Change to "en" if English audio
            target_languages=["en", "es", "fr"],
            output_dir="audio_output"
        )
        
        if result["success"]:
            print("\n✓ Processing Complete!")
            print("\n" + "=" * 60)
            print("RESULTS")
            print("=" * 60)
            
            # Show transcription
            print(f"\n📝 Transcription ({result['transcription']['language']}):")
            print(f"   {result['transcription']['text']}")
            
            # Show translations
            print(f"\n🌍 Translations:")
            for lang, text in result['translations'].items():
                print(f"   {lang}: {text}")
            
            # Show audio outputs
            print(f"\n🔊 Generated Audio Files:")
            for lang, path in result['audio_outputs'].items():
                print(f"   {lang}: {path}")
            
            print("\n✓ All files saved in 'audio_output' folder")
        else:
            print(f"\n✗ Processing failed: {result.get('error')}")
            
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\nTips:")
        print("- Ensure audio is in WAV format")
        print("- Check if file is not corrupted")
        print("- Try with a shorter audio clip first")

else:
    print(f"\n⚠ Audio file not found: {audio_file}")
    print("\nTo test with audio:")
    print("1. Record or find a Hindi/English audio file")
    print("2. Convert to WAV format (mono, 16kHz recommended)")
    print("3. Save as 'test_audio.wav' in this directory")
    print("4. Run this script again")
    
    print("\n" + "=" * 60)
    print("ALTERNATIVE: Test with sample text")
    print("=" * 60)
    
    # Test with text instead
    print("\nSince no audio file found, testing with text...")
    
    sample_texts = [
        ("hi", "नमस्ते, यह एक परीक्षण है"),
        ("en", "Hello, this is a test"),
    ]
    
    for lang, text in sample_texts:
        print(f"\n📢 Sample ({lang}): {text}")
        
        translations = pipeline.translate_only(
            text=text,
            source_lang=lang,
            target_langs=["en", "es", "fr"] if lang == "hi" else ["hi", "es", "fr"]
        )
        
        for target_lang, translated in translations.items():
            print(f"   → {target_lang}: {translated}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
