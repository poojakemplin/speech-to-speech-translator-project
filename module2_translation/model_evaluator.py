"""
Translation Model Evaluation
Evaluates translation quality using various metrics
"""
from typing import List, Dict, Tuple
import numpy as np
from collections import Counter
import math
from loguru import logger


class TranslationEvaluator:
    """Evaluates translation quality using multiple metrics"""
    
    @staticmethod
    def calculate_bleu_score(
        reference: str,
        candidate: str,
        max_n: int = 4
    ) -> float:
        """
        Calculate BLEU score for translation quality
        
        Args:
            reference: Reference (ground truth) translation
            candidate: Candidate (model) translation
            max_n: Maximum n-gram size (default: 4)
        
        Returns:
            BLEU score (0-1)
        """
        ref_tokens = reference.lower().split()
        cand_tokens = candidate.lower().split()
        
        if len(cand_tokens) == 0:
            return 0.0
        
        # Brevity penalty
        bp = TranslationEvaluator._brevity_penalty(len(ref_tokens), len(cand_tokens))
        
        # Calculate precision for each n-gram
        precisions = []
        for n in range(1, max_n + 1):
            precision = TranslationEvaluator._ngram_precision(
                ref_tokens,
                cand_tokens,
                n
            )
            precisions.append(precision)
        
        # Geometric mean of precisions
        if all(p > 0 for p in precisions):
            geo_mean = math.exp(sum(math.log(p) for p in precisions) / len(precisions))
            bleu = bp * geo_mean
        else:
            bleu = 0.0
        
        return bleu
    
    @staticmethod
    def _brevity_penalty(ref_len: int, cand_len: int) -> float:
        """Calculate brevity penalty"""
        if cand_len >= ref_len:
            return 1.0
        return math.exp(1 - ref_len / cand_len) if cand_len > 0 else 0.0
    
    @staticmethod
    def _ngram_precision(ref_tokens: List[str], cand_tokens: List[str], n: int) -> float:
        """Calculate n-gram precision"""
        if len(cand_tokens) < n:
            return 0.0
        
        # Generate n-grams
        ref_ngrams = Counter(
            tuple(ref_tokens[i:i+n]) for i in range(len(ref_tokens) - n + 1)
        )
        cand_ngrams = Counter(
            tuple(cand_tokens[i:i+n]) for i in range(len(cand_tokens) - n + 1)
        )
        
        # Count matches
        matches = sum(
            min(cand_ngrams[ngram], ref_ngrams[ngram])
            for ngram in cand_ngrams
        )
        
        total = sum(cand_ngrams.values())
        
        return matches / total if total > 0 else 0.0
    
    @staticmethod
    def calculate_word_error_rate(reference: str, candidate: str) -> float:
        """
        Calculate Word Error Rate (WER)
        
        Args:
            reference: Reference text
            candidate: Candidate text
        
        Returns:
            WER score (lower is better)
        """
        ref_words = reference.lower().split()
        cand_words = candidate.lower().split()
        
        # Levenshtein distance at word level
        distance = TranslationEvaluator._levenshtein_distance(ref_words, cand_words)
        
        wer = distance / len(ref_words) if len(ref_words) > 0 else 0.0
        return wer
    
    @staticmethod
    def _levenshtein_distance(seq1: List[str], seq2: List[str]) -> int:
        """Calculate Levenshtein distance between two sequences"""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],    # deletion
                        dp[i][j-1],    # insertion
                        dp[i-1][j-1]   # substitution
                    )
        
        return dp[m][n]
    
    @staticmethod
    def calculate_character_error_rate(reference: str, candidate: str) -> float:
        """
        Calculate Character Error Rate (CER)
        
        Args:
            reference: Reference text
            candidate: Candidate text
        
        Returns:
            CER score (lower is better)
        """
        ref_chars = list(reference.lower().replace(" ", ""))
        cand_chars = list(candidate.lower().replace(" ", ""))
        
        distance = TranslationEvaluator._levenshtein_distance(ref_chars, cand_chars)
        
        cer = distance / len(ref_chars) if len(ref_chars) > 0 else 0.0
        return cer
    
    @staticmethod
    def evaluate_translation(
        reference: str,
        candidate: str
    ) -> Dict[str, float]:
        """
        Comprehensive translation evaluation
        
        Args:
            reference: Reference translation
            candidate: Candidate translation
        
        Returns:
            Dictionary with evaluation metrics
        """
        metrics = {
            "bleu_score": TranslationEvaluator.calculate_bleu_score(reference, candidate),
            "wer": TranslationEvaluator.calculate_word_error_rate(reference, candidate),
            "cer": TranslationEvaluator.calculate_character_error_rate(reference, candidate),
            "length_ratio": len(candidate.split()) / len(reference.split()) if len(reference.split()) > 0 else 0
        }
        
        return metrics
    
    @staticmethod
    def evaluate_batch(
        references: List[str],
        candidates: List[str]
    ) -> Dict[str, float]:
        """
        Evaluate a batch of translations
        
        Args:
            references: List of reference translations
            candidates: List of candidate translations
        
        Returns:
            Dictionary with average metrics
        """
        if len(references) != len(candidates):
            raise ValueError("References and candidates must have the same length")
        
        all_metrics = [
            TranslationEvaluator.evaluate_translation(ref, cand)
            for ref, cand in zip(references, candidates)
        ]
        
        # Calculate averages
        avg_metrics = {
            "avg_bleu_score": np.mean([m["bleu_score"] for m in all_metrics]),
            "avg_wer": np.mean([m["wer"] for m in all_metrics]),
            "avg_cer": np.mean([m["cer"] for m in all_metrics]),
            "avg_length_ratio": np.mean([m["length_ratio"] for m in all_metrics])
        }
        
        return avg_metrics


class LatencyEvaluator:
    """Evaluates translation latency and performance"""
    
    def __init__(self):
        """Initialize latency evaluator"""
        self.latency_records = []
        logger.info("Latency evaluator initialized")
    
    def record_latency(
        self,
        latency: float,
        text_length: int,
        source_lang: str,
        target_lang: str
    ):
        """
        Record translation latency
        
        Args:
            latency: Translation time in seconds
            text_length: Length of input text
            source_lang: Source language
            target_lang: Target language
        """
        self.latency_records.append({
            "latency": latency,
            "text_length": text_length,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "chars_per_second": text_length / latency if latency > 0 else 0
        })
    
    def get_statistics(self) -> Dict:
        """
        Get latency statistics
        
        Returns:
            Dictionary with latency statistics
        """
        if not self.latency_records:
            return {"error": "No latency records available"}
        
        latencies = [r["latency"] for r in self.latency_records]
        
        stats = {
            "total_translations": len(self.latency_records),
            "avg_latency": np.mean(latencies),
            "median_latency": np.median(latencies),
            "min_latency": np.min(latencies),
            "max_latency": np.max(latencies),
            "std_latency": np.std(latencies),
            "p95_latency": np.percentile(latencies, 95),
            "p99_latency": np.percentile(latencies, 99)
        }
        
        return stats
    
    def is_real_time_capable(self, threshold: float = 2.0) -> bool:
        """
        Check if translation is real-time capable
        
        Args:
            threshold: Maximum acceptable latency in seconds
        
        Returns:
            True if capable of real-time translation
        """
        if not self.latency_records:
            return False
        
        stats = self.get_statistics()
        return stats["p95_latency"] < threshold
    
    def clear_records(self):
        """Clear latency records"""
        self.latency_records.clear()
        logger.info("Latency records cleared")
