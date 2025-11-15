"""
Demo: Complete Workflow with Sample Audio
Shows the complete pipeline in action
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from opensource_models import OpenSourcePipeline
from pathlib import Path


def demo_workflow():
    """Demonstrate complete workflow"""
    print("=" * 70)
    print(" COMPLETE SPEECH TRANSLATION WORKFLOW DEMO")
    print("=" * 70)
    
    # Initialize
    print("\n📦 Initializing Pipeline Components...")
    print("   ├─ Whisper STT (base model)")
    print("   ├─ Helsinki-NLP Translator")
    print("   └─ gTTS Text-to-Speech")
    
    pipeline = OpenSourcePipeline(whisper_model="base")
    
    print("\n✓ Pipeline ready!")
    
    # Workflow steps
    print("\n" + "=" * 70)
    print(" WORKFLOW STEPS")
    print("=" * 70)
    
    print("""
1️⃣  AUDIO INPUT
   • User uploads or records audio (Hindi/English)
   • Supported formats: WAV, MP3, M4A, etc.
   
2️⃣  AUDIO CONVERSION (pydub)
   • Convert to WAV format
   • Set to mono channel
   • Resample to 16 kHz
   • Ensures model compatibility
   
3️⃣  SPEECH-TO-TEXT (Whisper)
   • Transcribe audio to text
   • Auto-detect language or specify
   • Example: Hindi speech → "नमस्ते, आप कैसे हैं?"
   
4️⃣  MACHINE TRANSLATION (Helsinki-NLP)
   • Translate text to target languages
   • Uses MarianMT transformer models
   • Example: "नमस्ते, आप कैसे हैं?" → "Hello, how are you?"
   
5️⃣  TEXT-TO-SPEECH (gTTS)
   • Convert translated text to speech
   • Generate audio in target language
   • Output: MP3 audio file
   
6️⃣  BATCH PROCESSING
   • Process multiple audio files automatically
   • Returns tuples: (input_file, result_dict)
   • Organized output directories
    """)
    
    # Example usage
    print("=" * 70)
    print(" EXAMPLE USAGE")
    print("=" * 70)
    
    print("\n📝 Example 1: Single Audio File")
    print("-" * 70)
    print("""
from opensource_models import OpenSourcePipeline

# Initialize pipeline
pipeline = OpenSourcePipeline(whisper_model="base")

# Process audio file
result = pipeline.process_audio(
    audio_path="hindi_speech.wav",
    source_language="hi",
    target_languages=["en", "es", "fr"],
    output_dir="output"
)

# Access results
print(f"Original: {result['transcription']['text']}")
print(f"English: {result['translations']['en']}")
print(f"Audio: {result['audio_outputs']['en']}")
    """)
    
    print("\n📝 Example 2: Batch Processing")
    print("-" * 70)
    print("""
# Process multiple files
audio_files = [
    "commentary1.wav",
    "commentary2.wav",
    "commentary3.wav"
]

results = pipeline.process_batch(
    audio_files=audio_files,
    source_language="en",
    target_languages=["hi", "es", "fr"],
    output_dir="batch_output"
)

# Process results
for audio_file, result in results:
    if result['success']:
        print(f"✓ {audio_file}: {result['transcription']['text']}")
    """)
    
    print("\n📝 Example 3: Individual Components")
    print("-" * 70)
    print("""
# Just transcription
transcription = pipeline.transcribe_only("audio.wav", language="hi")
print(transcription['text'])

# Just translation
translations = pipeline.translate_only(
    text="Hello world",
    source_lang="en",
    target_langs=["hi", "es", "fr"]
)

# Just TTS
audio_files = pipeline.synthesize_only(
    translations={"en": "Hello", "hi": "नमस्ते"},
    output_dir="audio_output"
)
    """)
    
    # Real example with text
    print("\n" + "=" * 70)
    print(" LIVE DEMO: Translation Only")
    print("=" * 70)
    
    test_sentences = [
        ("en", "Welcome to the cricket match!", ["hi", "es"]),
        ("hi", "यह एक शानदार खेल है!", ["en", "es"]),
        ("en", "What an amazing shot!", ["hi", "fr"])
    ]
    
    for source_lang, text, target_langs in test_sentences:
        print(f"\n📢 Original ({source_lang}): {text}")
        
        translations = pipeline.translate_only(text, source_lang, target_langs)
        
        for lang, translated in translations.items():
            print(f"   └─ {lang}: {translated}")
    
    print("\n" + "=" * 70)
    print(" PERFORMANCE NOTES")
    print("=" * 70)
    print("""
⚡ Model Sizes & Speed:
   • Whisper tiny:   ~32x realtime, 1GB VRAM
   • Whisper base:   ~16x realtime, 1GB VRAM
   • Whisper small:  ~6x realtime, 2GB VRAM
   • Whisper medium: ~2x realtime, 5GB VRAM
   • Whisper large:  ~1x realtime, 10GB VRAM

💾 First Run:
   • Models download automatically
   • Whisper base: ~150MB
   • Helsinki-NLP: ~300MB per language pair
   • Subsequent runs use cached models

🚀 Optimization Tips:
   • Use GPU for faster processing (CUDA)
   • Start with 'base' model, upgrade if needed
   • Batch process multiple files for efficiency
   • Cache translations for repeated content
    """)
    
    print("\n" + "=" * 70)
    print(" READY TO USE!")
    print("=" * 70)
    print("\n✓ Pipeline is ready for production use")
    print("✓ No API keys required (fully open-source)")
    print("✓ Works offline after model download")
    print("✓ Supports 14+ languages")
    print("\n")


if __name__ == "__main__":
    demo_workflow()
