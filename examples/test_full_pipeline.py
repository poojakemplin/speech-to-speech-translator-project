"""
Example: Test Full Speech-to-Speech Pipeline
Demonstrates complete real-time translation pipeline
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module3_realtime_integration import SpeechToSpeechPipeline
from module2_translation import AzureOpenAITranslator
from config import settings
import time


def main():
    """Test full speech-to-speech pipeline"""
    print("=" * 60)
    print("Full Speech-to-Speech Translation Pipeline Test")
    print("=" * 60)
    
    # Initialize translator
    print("\n1. Initializing translator...")
    translator = AzureOpenAITranslator(
        api_key=settings.azure_openai_key,
        endpoint=settings.azure_openai_endpoint,
        deployment_name=settings.azure_openai_deployment_name
    )
    
    # Initialize pipeline
    print("2. Initializing speech-to-speech pipeline...")
    target_languages = ["es-ES", "fr-FR", "hi-IN"]
    print(f"   Source: en-US")
    print(f"   Targets: {', '.join(target_languages)}")
    
    pipeline = SpeechToSpeechPipeline(
        speech_key=settings.azure_speech_key,
        speech_region=settings.azure_speech_region,
        openai_translator=translator,
        source_language="en-US",
        target_languages=target_languages
    )
    
    # Define callbacks
    translation_count = 0
    
    def on_translation_complete(translations):
        nonlocal translation_count
        translation_count += 1
        print(f"\n✓ Translation #{translation_count} completed:")
        for lang, text in translations.items():
            print(f"   {lang}: {text}")
    
    def on_synthesis_complete(audio_outputs):
        print(f"   ♪ Audio synthesized for {len(audio_outputs)} languages")
    
    # Set callbacks
    pipeline.on_translation_complete = on_translation_complete
    pipeline.on_synthesis_complete = on_synthesis_complete
    
    # Start pipeline
    print("\n3. Starting real-time translation pipeline...")
    print("\n📢 Speak into your microphone (Press Ctrl+C to stop)...\n")
    
    pipeline.start_pipeline()
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n4. Stopping pipeline...")
        pipeline.stop_pipeline()
        print("✓ Pipeline stopped")
    
    print(f"\n📊 Statistics:")
    print(f"   Total translations: {translation_count}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
