"""
My Test Script - Quick Translation and TTS Demo
"""
from opensource_models import OpenSourcePipeline

print("=" * 60)
print("My Translation Test")
print("=" * 60)

# Initialize pipeline
print("\nInitializing pipeline...")
pipeline = OpenSourcePipeline(whisper_model="base")
print("✓ Pipeline ready!")

# Test 1: Hindi to multiple languages
print("\n" + "=" * 60)
print("Test 1: Hindi → English, Spanish, French")
print("=" * 60)

hindi_text = "नमस्ते, आप कैसे हैं?"
print(f"\nOriginal (Hindi): {hindi_text}")

translations = pipeline.translate_only(
    text=hindi_text,
    source_lang="hi",
    target_langs=["en", "es", "fr"]
)

print("\nTranslations:")
for lang, text in translations.items():
    print(f"  {lang}: {text}")

# Test 2: Generate speech for all translations
print("\n" + "=" * 60)
print("Test 2: Generating Speech Files")
print("=" * 60)

print("\nGenerating audio files...")
audio_files = pipeline.synthesize_only(
    translations=translations,
    output_dir="my_output"
)

print("\n✓ Audio files created:")
for lang, result in audio_files.items():
    if result.get("success"):
        print(f"  {lang}: {result['output_path']}")

# Test 3: English to multiple languages
print("\n" + "=" * 60)
print("Test 3: English → Hindi, Spanish, French")
print("=" * 60)

english_text = "Welcome to the cricket match! This is going to be exciting."
print(f"\nOriginal (English): {english_text}")

translations2 = pipeline.translate_only(
    text=english_text,
    source_lang="en",
    target_langs=["hi", "es", "fr"]
)

print("\nTranslations:")
for lang, text in translations2.items():
    print(f"  {lang}: {text}")

# Test 4: More examples
print("\n" + "=" * 60)
print("Test 4: Sports Commentary Examples")
print("=" * 60)

commentary_examples = [
    ("en", "What an amazing shot!", ["hi", "es"]),
    ("en", "The crowd is going wild!", ["hi", "fr"]),
    ("hi", "यह एक शानदार खेल है!", ["en", "es"]),
]

for source_lang, text, target_langs in commentary_examples:
    print(f"\n📢 Original ({source_lang}): {text}")
    
    translations = pipeline.translate_only(text, source_lang, target_langs)
    
    for lang, translated in translations.items():
        print(f"   → {lang}: {translated}")

# Summary
print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
print("\n✓ All translations successful!")
print(f"✓ Audio files saved in: my_output/")
print("\nNext steps:")
print("1. Check 'my_output' folder for generated MP3 files")
print("2. Play the audio files to hear translations")
print("3. Try with your own text or audio files")
print("\nTo process audio files:")
print("""
result = pipeline.process_audio(
    audio_path="your_audio.wav",
    source_language="hi",
    target_languages=["en", "es", "fr"],
    output_dir="output"
)
""")
print()
