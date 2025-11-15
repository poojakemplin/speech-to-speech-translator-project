"""
Example: Test Translation
Demonstrates translation capabilities and evaluation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module2_translation import AzureOpenAITranslator, MultiLanguageTranslator, TranslationEvaluator
from config import settings


def main():
    """Test translation"""
    print("=" * 60)
    print("Translation Test")
    print("=" * 60)
    
    # Initialize translator
    print("\n1. Initializing translator...")
    translator = AzureOpenAITranslator(
        api_key=settings.azure_openai_key,
        endpoint=settings.azure_openai_endpoint,
        deployment_name=settings.azure_openai_deployment_name
    )
    
    # Test single translation
    print("\n2. Testing single translation...")
    test_text = "Welcome to the live cricket match! The players are entering the field."
    print(f"   Original (en-US): {test_text}")
    
    result = translator.translate_text(
        text=test_text,
        source_language="en-US",
        target_language="hi-IN"
    )
    
    if result["success"]:
        print(f"   Translated (hi-IN): {result['translated_text']}")
        print(f"   Latency: {result['latency']:.2f}s")
    else:
        print(f"   Error: {result['error']}")
    
    # Test multi-language translation
    print("\n3. Testing multi-language translation...")
    multi_translator = MultiLanguageTranslator(translator)
    multi_translator.set_target_languages(["es-ES", "fr-FR", "de-DE", "ja-JP"])
    
    test_text2 = "The score is 150 for 3 wickets!"
    print(f"   Original (en-US): {test_text2}")
    
    results = multi_translator.translate_to_all_languages(
        text=test_text2,
        source_language="en-US"
    )
    
    for lang, result in results.items():
        if result["success"]:
            print(f"   {lang}: {result['translated_text']}")
    
    # Test batch translation
    print("\n4. Testing batch translation...")
    batch_texts = [
        "What an amazing shot!",
        "The crowd is going wild!",
        "This is incredible!"
    ]
    
    print("   Translating to Spanish...")
    batch_results = translator.translate_batch(
        texts=batch_texts,
        source_language="en-US",
        target_language="es-ES"
    )
    
    for i, result in enumerate(batch_results):
        if result["success"]:
            print(f"   {i+1}. {batch_texts[i]} -> {result['translated_text']}")
    
    # Test evaluation
    print("\n5. Testing translation evaluation...")
    evaluator = TranslationEvaluator()
    
    reference = "¡Qué tiro increíble!"
    candidate = batch_results[0]["translated_text"]
    
    metrics = evaluator.evaluate_translation(reference, candidate)
    
    print(f"   Reference: {reference}")
    print(f"   Candidate: {candidate}")
    print(f"   BLEU Score: {metrics['bleu_score']:.4f}")
    print(f"   WER: {metrics['wer']:.4f}")
    print(f"   CER: {metrics['cer']:.4f}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
