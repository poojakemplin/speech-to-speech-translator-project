"""
Example: Test Speech Recognition
Demonstrates speech recognition capabilities
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module1_speech_recognition import SpeechRecognizer
from config import settings
import time


def main():
    """Test speech recognition"""
    print("=" * 60)
    print("Speech Recognition Test")
    print("=" * 60)
    
    # Initialize recognizer
    print("\n1. Initializing speech recognizer...")
    recognizer = SpeechRecognizer(
        speech_key=settings.azure_speech_key,
        speech_region=settings.azure_speech_region,
        source_language="en-US"
    )
    
    # Setup microphone input
    print("2. Setting up microphone input...")
    recognizer.setup_microphone_input()
    
    # Define callbacks
    def on_recognized(result):
        print(f"\n✓ Recognized: {result['text']}")
        print(f"  Language: {result['language']}")
        print(f"  Timestamp: {result['timestamp']}")
    
    def on_recognizing(result):
        print(f"  Recognizing: {result['text']}", end='\r')
    
    def on_error(error):
        print(f"\n✗ Error: {error['error_details']}")
    
    # Set callbacks
    recognizer.set_callbacks(
        on_recognized=on_recognized,
        on_recognizing=on_recognizing,
        on_error=on_error
    )
    
    # Start recognition
    print("3. Starting continuous recognition...")
    print("\n📢 Speak into your microphone (Press Ctrl+C to stop)...\n")
    
    recognizer.start_continuous_recognition()
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n4. Stopping recognition...")
        recognizer.stop_continuous_recognition()
        print("✓ Recognition stopped")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
