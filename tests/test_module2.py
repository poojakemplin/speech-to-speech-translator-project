"""
Unit tests for Module 2: Translation
"""
import pytest
from module2_translation import TranslationEvaluator


class TestTranslationEvaluator:
    """Test translation evaluation metrics"""
    
    def test_bleu_score_perfect_match(self):
        """Test BLEU score with perfect match"""
        reference = "Hello world"
        candidate = "Hello world"
        
        score = TranslationEvaluator.calculate_bleu_score(reference, candidate)
        assert score > 0.9
    
    def test_bleu_score_no_match(self):
        """Test BLEU score with no match"""
        reference = "Hello world"
        candidate = "Goodbye universe"
        
        score = TranslationEvaluator.calculate_bleu_score(reference, candidate)
        assert score < 0.5
    
    def test_wer_calculation(self):
        """Test Word Error Rate"""
        reference = "the quick brown fox"
        candidate = "the quick brown dog"
        
        wer = TranslationEvaluator.calculate_word_error_rate(reference, candidate)
        assert 0 < wer < 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
