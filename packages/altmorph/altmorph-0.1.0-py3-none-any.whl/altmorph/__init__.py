#!/usr/bin/env python3
"""
AltMorph: Context-aware Norwegian morphological alternative generator.

Expands Norwegian text by finding morphological alternatives for each word using
the Ordbank API. Combines POS tagging, comprehensive lemma analysis, and BERT-based
acceptability scoring to provide contextually appropriate alternatives.

Features:
- Context-sensitive filtering (handles ambiguous cases intelligently)
- Comprehensive lemma coverage (finds all valid morphological forms)
- Position-specific analysis (same word, different contexts)
- Intelligent caching (dramatic performance improvements)
- Multiple verbosity levels (quiet to very verbose)
- Batched BERT processing for improved performance

Usage:
    python -m altmorph --sentence "Jenta kasta ballen." --lang nob
    # Output: "[Jenta|Jenten] [kasta|kastet] [ballen|balla] til gutten."
    
    # As a package:
    pip install altmorph
    altmorph --sentence "Jenta kasta ballen." --lang nob
"""

import argparse
import csv
import concurrent.futures as cf
import difflib
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import sys
import time
from functools import lru_cache
from typing import Dict, List, Optional, Set, Tuple

import requests
import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer, pipeline

# Constants
API_BASE = "https://clarino.uib.no/ordbank-api-prod"
LEMMA_MULTI_DIR = Path(__file__).parent / "data" / "lemma-multi"
SESSION = requests.Session()

logger = logging.getLogger(__name__)

# Global cache configuration
_cache_enabled = True
_cache_dir = Path.home() / ".ordbank_cache"
_cache_stats = {"hits": 0, "misses": 0}


# ========================= Cache Management =========================

def set_cache_enabled(enabled: bool):
    """Enable or disable caching globally."""
    global _cache_enabled
    _cache_enabled = enabled


def get_cache_stats():
    """Get cache hit/miss statistics."""
    return _cache_stats.copy()


def reset_cache_stats():
    """Reset cache statistics."""
    global _cache_stats
    _cache_stats = {"hits": 0, "misses": 0}


def ensure_cache_dir():
    """Ensure cache directory exists."""
    if _cache_enabled:
        _cache_dir.mkdir(exist_ok=True)


def delete_cache():
    """Delete all cache files."""
    if _cache_dir.exists():
        cache_files = list(_cache_dir.glob("*.json"))
        file_count = len(cache_files)
        for cache_file in cache_files:
            cache_file.unlink()
        logger.info("Cache cleared: deleted %d files", file_count)
    else:
        logger.info("Cache cleared: no cache directory found")


def make_cache_key(prefix: str, *args) -> str:
    """Generate a cache key from prefix and arguments."""
    # Create a stable hash from the arguments
    content = ":".join(str(arg) for arg in args)
    hash_obj = hashlib.md5(content.encode('utf-8'))
    return f"{prefix}_{hash_obj.hexdigest()}"


def load_from_cache(cache_key: str) -> Optional[any]:
    """Load data from cache file."""
    if not _cache_enabled:
        return None
    
    cache_file = _cache_dir / f"{cache_key}.json"
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                _cache_stats["hits"] += 1
                
                # Fix inflection data: convert tags from lists back to tuples
                if isinstance(data, list) and data and isinstance(data[0], dict) and "tags" in data[0]:
                    for item in data:
                        if "tags" in item and isinstance(item["tags"], list):
                            item["tags"] = tuple(item["tags"])
                
                return data
        except (json.JSONDecodeError, IOError) as e:
            logger.warning("Failed to load cache file %s: %s", cache_file, e)
            # Delete corrupted cache file
            cache_file.unlink(missing_ok=True)
    
    _cache_stats["misses"] += 1
    return None


def save_to_cache(cache_key: str, data: any):
    """Save data to cache file."""
    if not _cache_enabled:
        return
    
    ensure_cache_dir()
    cache_file = _cache_dir / f"{cache_key}.json"
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    except IOError as e:
        logger.warning("Failed to save cache file %s: %s", cache_file, e)


# ========================= Multi-lemma Handling =========================

@lru_cache(maxsize=4)
def _load_multi_lemma_map(lang: str) -> Dict[int, Set[int]]:
    """Return mapping from lemma id to related lemma ids for the given language."""
    path = LEMMA_MULTI_DIR / f"{lang}.csv"
    if not path.exists():
        return {}

    mapping: Dict[int, Set[int]] = {}

    try:
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                raw_ids = (row or {}).get("lemma_id")
                if not raw_ids:
                    continue
                ids = _parse_braced_ints(raw_ids)
                if not ids:
                    continue
                for lemma_id in ids:
                    bucket = mapping.setdefault(lemma_id, set())
                    bucket.update(ids)
    except Exception as exc:
        logger.warning("Failed to load multi-lemma map for %s: %s", lang, exc)
        return {}

    # Freeze values to avoid accidental mutation downstream
    return {lemma_id: frozenset(values) for lemma_id, values in mapping.items()}


def _parse_braced_ints(raw: str) -> Set[int]:
    """Parse a string like '{1,2}' into a set of ints."""
    text = raw.strip()
    if text.startswith("{") and text.endswith("}"):
        text = text[1:-1]
    result: Set[int] = set()
    for part in text.split(","):
        piece = part.strip()
        if not piece:
            continue
        try:
            result.add(int(piece))
        except ValueError:
            continue
    return result


def _expand_multi_lemma_ids(lang: str, lemma_ids: Set[int]) -> Set[int]:
    """Return additional lemma ids linked via the multi-lemma map."""
    if not lemma_ids:
        return set()
    mapping = _load_multi_lemma_map(lang)
    if not mapping:
        return set()

    expanded: Set[int] = set()
    for lemma_id in lemma_ids:
        related = mapping.get(lemma_id)
        if related:
            expanded.update(related)
    return expanded


# ========================= Model Loading =========================

@lru_cache(maxsize=1)
def get_pos_tagger():
    """Load POS tagger model (lazy initialization)."""
    logger.info("Loading POS tagger...")
    tagger = pipeline(
        "token-classification",
        model="NbAiLab/nb-bert-base-pos",
        aggregation_strategy="none"
    )
    logger.info("POS tagger loaded")
    return tagger


@lru_cache(maxsize=1)
def get_masked_lm() -> Tuple[AutoTokenizer, AutoModelForMaskedLM]:
    """Load masked language model (lazy initialization)."""
    logger.info("Loading masked language model...")
    tokenizer = AutoTokenizer.from_pretrained("NbAiLab/nb-bert-base")
    model = AutoModelForMaskedLM.from_pretrained("NbAiLab/nb-bert-base")
    logger.info("Masked language model loaded")
    return tokenizer, model


# ========================= POS Tagging =========================

def extract_pos_tags(sentence: str) -> Dict[str, str]:
    """Extract POS tags for all words in sentence."""
    try:
        tagger = get_pos_tagger()
        pos_results = tagger(sentence)
        
        # Parse sub-token output and map to original words
        word_pos_map = {}
        current_word = ""
        current_pos = None
        
        for token_info in pos_results:
            token = token_info['word']
            pos_tag = token_info['entity']
            
            if token.startswith('##'):
                current_word += token[2:]  # Remove ## prefix
            else:
                # Save previous word
                if current_word and current_pos:
                    word_pos_map[current_word.lower()] = current_pos
                # Start new word
                current_word = token
                current_pos = pos_tag
        
        # Don't forget last word
        if current_word and current_pos:
            word_pos_map[current_word.lower()] = current_pos
            
        return word_pos_map
        
    except Exception as e:
        logger.warning("POS tagging failed: %r", e)
        return {}


# ========================= Acceptability Scoring =========================

def score_word_in_context(sentence: str, target_word: str, target_position: Optional[int] = None) -> Dict:
    """Score a word's acceptability in its sentence context."""
    tokenizer, model = get_masked_lm()

    words = sentence.split()
    
    if target_position is not None:
        # Convert from tokenize_preserve position to split position
        # Count only word tokens up to target_position
        tokens = tokenize_preserve(sentence)
        word_count = 0
        for i in range(min(target_position, len(tokens))):
            if is_word(tokens[i]):
                word_count += 1
        target_idx = word_count
    else:
        # Find first occurrence (fallback)
        target_norm = normalize_token(target_word)
        try:
            target_idx = next(
                idx for idx, word in enumerate(words)
                if normalize_token(word) == target_norm
            )
        except StopIteration:
            return {'logit': float('-inf'), 'probability': 0.0, 'rank': -1}

    if target_idx >= len(words):
        return {'logit': float('-inf'), 'probability': 0.0, 'rank': -1}

    masked_words = words.copy()
    masked_words[target_idx] = tokenizer.mask_token
    masked_sentence = " ".join(masked_words)

    inputs = tokenizer(masked_sentence, return_tensors="pt")
    mask_positions = (inputs.input_ids == tokenizer.mask_token_id).nonzero(as_tuple=True)[1]
    if len(mask_positions) == 0:
        return {'logit': float('-inf'), 'probability': 0.0, 'rank': -1}

    mask_pos = mask_positions[0]

    with torch.no_grad():
        logits = model(**inputs).logits[0, mask_pos]
        probabilities = torch.softmax(logits, dim=0)

    target_tokens = tokenizer(target_word, add_special_tokens=False)['input_ids']

    if len(target_tokens) == 1:
        token_id = target_tokens[0]
        target_prob = probabilities[token_id]
        return {
            'logit': logits[token_id].item(),
            'probability': target_prob.item(),
            'rank': (probabilities > target_prob).sum().item() + 1,
        }

    # Multi-token words: average scores to stay comparable with single tokens.
    token_probs = [probabilities[tid].item() for tid in target_tokens]
    token_logits = [logits[tid].item() for tid in target_tokens]
    return {
        'logit': sum(token_logits) / len(token_logits),
        'probability': sum(token_probs) / len(token_probs),
        'rank': -1,
    }


def filter_by_acceptability(tokens: List[str], position: int, alternatives: Set[str],
                          threshold: float = 2.0, debug: bool = False) -> Set[str]:
    """Filter alternatives by linguistic acceptability at specific position."""
    if len(alternatives) <= 1:
        return alternatives
    
    original_word = tokens[position]
    original_sentence = "".join(tokens)
    
    # Score original word at its specific position
    original_score = score_word_in_context(original_sentence, original_word, position)
    scores = {original_word: original_score}
    
    if debug:
        logger.debug(
            "     %-12s: Logit %6.3f, Prob %.2e, Rank %4d (ORIGINAL)",
            original_word,
            original_score['logit'],
            original_score['probability'],
            original_score['rank'],
        )
    
    # Score each alternative
    for alt in alternatives:
        if alt.lower() == original_word.lower():
            continue
            
        # Replace word at specific position
        test_tokens = tokens.copy()
        test_tokens[position] = alt
        test_sentence = "".join(test_tokens)
        
        score = score_word_in_context(test_sentence, alt, position)
        scores[alt] = score
        
        if debug:
            logger.debug(
                "     %-12s: Logit %6.3f, Prob %.2e, Rank %4d",
                alt,
                score['logit'],
                score['probability'],
                score['rank'],
            )
    
    # Filter based on logit threshold
    original_logit = original_score['logit']
    filtered = {original_word}  # Always include original
    
    for word, score in scores.items():
        if word == original_word:
            continue
            
        logit_diff = original_logit - score['logit']
        
        if logit_diff <= threshold:
            filtered.add(word)
            if debug:
                logger.debug(
                    "     ✅ KEEPING %s: logit diff %+0.3f <= %.2f",
                    word,
                    logit_diff,
                    threshold,
                )
        else:
            if debug:
                logger.debug(
                    "     ❌ REJECTING %s: logit diff %+0.3f > %.2f",
                    word,
                    logit_diff,
                    threshold,
                )

    if debug:
        rejected = len(alternatives) - len(filtered)
        logger.debug(
            "     📊 Result: kept %d, rejected %d",
            len(filtered),
            rejected,
        )
    
    return filtered


# ========================= Batched BERT Processing =========================

def batch_score_alternatives(scoring_tasks: List[Dict]) -> Dict[str, Dict[str, Dict]]:
    """Score multiple alternatives for multiple sentences in one BERT batch.
    
    Args:
        scoring_tasks: List of dicts with keys:
            - 'sentence_id': unique identifier for the sentence
            - 'tokens': list of tokens
            - 'position': position of word to score
            - 'alternatives': set of alternatives to score
            - 'original_word': the original word at position
    
    Returns:
        Dict mapping sentence_id -> word -> {alternative: score_dict}
    """
    if not scoring_tasks:
        return {}
    
    tokenizer, model = get_masked_lm()
    
    # Collect all masked sentences and track their metadata
    masked_sentences = []
    task_metadata = []
    
    for task in scoring_tasks:
        sentence_id = task['sentence_id']
        tokens = task['tokens']
        position = task['position']
        alternatives = task['alternatives']
        original_word = task['original_word']
        
        # Create original sentence
        original_sentence = "".join(tokens)
        
        # Score original word
        words = original_sentence.split()
        word_count = 0
        for i in range(min(position, len(tokens))):
            if is_word(tokens[i]):
                word_count += 1
        target_idx = word_count
        
        if target_idx < len(words):
            # Add original word scoring
            masked_words = words.copy()
            masked_words[target_idx] = tokenizer.mask_token
            masked_sentence = " ".join(masked_words)
            
            masked_sentences.append(masked_sentence)
            task_metadata.append({
                'sentence_id': sentence_id,
                'word': original_word,
                'is_original': True,
                'target_idx': target_idx
            })
            
            # Add alternative word scoring
            for alt in alternatives:
                if alt.lower() != original_word.lower():
                    masked_sentences.append(masked_sentence)
                    task_metadata.append({
                        'sentence_id': sentence_id,
                        'word': alt,
                        'is_original': False,
                        'target_idx': target_idx
                    })
    
    if not masked_sentences:
        return {}
    
    # Batch process all masked sentences
    results = {}
    batch_size = 32  # Process in smaller batches to avoid memory issues
    
    for i in range(0, len(masked_sentences), batch_size):
        batch_sentences = masked_sentences[i:i+batch_size]
        batch_metadata = task_metadata[i:i+batch_size]
        
        # Tokenize batch
        inputs = tokenizer(batch_sentences, return_tensors="pt", padding=True, truncation=True)
        
        with torch.no_grad():
            logits = model(**inputs).logits
            
            # Process each result in the batch
            for j, (sentence, metadata) in enumerate(zip(batch_sentences, batch_metadata)):
                sentence_id = metadata['sentence_id']
                word = metadata['word']
                target_idx = metadata['target_idx']
                
                # Find mask position in this sentence
                sentence_inputs = tokenizer(sentence, return_tensors="pt")
                mask_positions = (sentence_inputs.input_ids == tokenizer.mask_token_id).nonzero(as_tuple=True)[1]
                
                if len(mask_positions) == 0:
                    score = {'logit': float('-inf'), 'probability': 0.0, 'rank': -1}
                else:
                    mask_pos = mask_positions[0]
                    word_logits = logits[j, mask_pos]
                    probabilities = torch.softmax(word_logits, dim=0)
                    
                    # Score the target word
                    target_tokens = tokenizer(word, add_special_tokens=False)['input_ids']
                    
                    if len(target_tokens) == 1:
                        token_id = target_tokens[0]
                        target_prob = probabilities[token_id]
                        score = {
                            'logit': word_logits[token_id].item(),
                            'probability': target_prob.item(),
                            'rank': (probabilities > target_prob).sum().item() + 1,
                        }
                    else:
                        # Multi-token words: average scores
                        token_probs = [probabilities[tid].item() for tid in target_tokens]
                        token_logits = [word_logits[tid].item() for tid in target_tokens]
                        score = {
                            'logit': sum(token_logits) / len(token_logits),
                            'probability': sum(token_probs) / len(token_probs),
                            'rank': -1,
                        }
                
                # Store result
                if sentence_id not in results:
                    results[sentence_id] = {}
                results[sentence_id][word] = score
    
    return results


def batch_filter_by_acceptability(sentences_data: List[Dict], threshold: float = 2.0, debug: bool = False) -> Dict[str, Dict[int, Set[str]]]:
    """Filter alternatives for multiple sentences using batched BERT processing.
    
    Args:
        sentences_data: List of dicts with keys:
            - 'sentence_id': unique identifier
            - 'tokens': list of tokens
            - 'word_alternatives': dict mapping position -> set of alternatives
    
    Returns:
        Dict mapping sentence_id -> position -> filtered_alternatives
    """
    if not sentences_data:
        return {}
    
    # Prepare scoring tasks
    scoring_tasks = []
    for sentence_data in sentences_data:
        sentence_id = sentence_data['sentence_id']
        tokens = sentence_data['tokens']
        word_alternatives = sentence_data['word_alternatives']
        
        for position, alternatives in word_alternatives.items():
            if len(alternatives) > 1:
                original_word = tokens[position]
                scoring_tasks.append({
                    'sentence_id': sentence_id,
                    'tokens': tokens,
                    'position': position,
                    'alternatives': alternatives,
                    'original_word': original_word
                })
    
    # Batch score all alternatives
    batch_scores = batch_score_alternatives(scoring_tasks)
    
    # Filter based on threshold
    filtered_results = {}
    
    for sentence_data in sentences_data:
        sentence_id = sentence_data['sentence_id']
        tokens = sentence_data['tokens']
        word_alternatives = sentence_data['word_alternatives']
        
        filtered_results[sentence_id] = {}
        
        for position, alternatives in word_alternatives.items():
            if len(alternatives) <= 1:
                filtered_results[sentence_id][position] = alternatives
                continue
            
            original_word = tokens[position]
            scores = batch_scores.get(sentence_id, {})
            
            if original_word not in scores:
                # Fallback to original alternatives if scoring failed
                filtered_results[sentence_id][position] = alternatives
                continue
            
            original_score = scores[original_word]
            original_logit = original_score['logit']
            filtered = {original_word}  # Always include original
            
            if debug:
                logger.debug(
                    "     %-12s: Logit %6.3f, Prob %.2e, Rank %4d (ORIGINAL)",
                    original_word,
                    original_score['logit'],
                    original_score['probability'],
                    original_score['rank'],
                )
            
            for alt in alternatives:
                if alt.lower() == original_word.lower():
                    continue
                
                if alt in scores:
                    alt_score = scores[alt]
                    logit_diff = original_logit - alt_score['logit']
                    
                    if debug:
                        logger.debug(
                            "     %-12s: Logit %6.3f, Prob %.2e, Rank %4d",
                            alt,
                            alt_score['logit'],
                            alt_score['probability'],
                            alt_score['rank'],
                        )
                    
                    if logit_diff <= threshold:
                        filtered.add(alt)
                        if debug:
                            logger.debug(
                                "     ✅ KEEPING %s: logit diff %+0.3f <= %.2f",
                                alt,
                                logit_diff,
                                threshold,
                            )
                    else:
                        if debug:
                            logger.debug(
                                "     ❌ REJECTING %s: logit diff %+0.3f > %.2f",
                                alt,
                                logit_diff,
                                threshold,
                            )
            
            filtered_results[sentence_id][position] = filtered
            
            if debug:
                rejected = len(alternatives) - len(filtered)
                logger.debug(
                    "     📊 Result: kept %d, rejected %d",
                    len(filtered),
                    rejected,
                )
    
    return filtered_results


def process_sentences_batch(
    sentences: List[str],
    lang: str,
    api_key: str,
    timeout: float,
    max_workers: int,
    verbosity: int = 0,
    logit_threshold: float = 2.0,
    include_imperatives: bool = False,
    include_determinatives: bool = False,
    include_gender_adj: bool = False,
    lemma_threshold: int = 1,
    exclude_number_ambigious: bool = False,
    exclude_lamma_multi: bool = False,
) -> List[str]:
    """Process multiple sentences with batched BERT processing for improved performance."""
    
    if not sentences:
        return []
    
    headers = {"x-api-key": api_key.strip()}
    
    # Step 1: Process each sentence individually for API calls and POS tagging
    sentences_data = []
    
    for i, sentence in enumerate(sentences):
        # Preprocess and tokenize
        preprocessed = preprocess_punctuation(sentence)
        tokens = tokenize_preserve(preprocessed)
        
        # POS tagging
        unique_words = get_unique_words(tokens)
        pos_tags = extract_pos_tags(preprocessed)
        
        # Filter determiners
        if not include_determinatives:
            filtered_words = []
            for word in unique_words:
                pos_tag = pos_tags.get(word)
                if pos_tag != 'DET':
                    filtered_words.append(word)
            unique_words = filtered_words
        
        # Fetch alternatives from API
        cache = {}
        with cf.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            
            for word in unique_words:
                pos_tag = pos_tags.get(word)
                future = executor.submit(
                    get_alternatives,
                    word,
                    lang,
                    headers,
                    timeout,
                    pos_tag,
                    False,
                    include_imperatives,
                    include_gender_adj,
                    lemma_threshold,
                    exclude_number_ambigious,
                    exclude_lamma_multi,
                )
                futures[future] = word
            
            for future in cf.as_completed(futures):
                word = futures[future]
                try:
                    alternatives = future.result()
                    if alternatives:
                        cache[word.casefold()] = alternatives
                except Exception as e:
                    if verbosity >= 1:
                        logger.warning("Error processing word '%s': %s", word, e)
        
        # Collect word alternatives by position
        word_alternatives = {}
        for j, token in enumerate(tokens):
            if is_word(token):
                alternatives = cache.get(token.casefold())
                if alternatives and len(alternatives) > 1:
                    word_alternatives[j] = alternatives
        
        sentences_data.append({
            'sentence_id': f"sent_{i}",
            'original_sentence': sentence,
            'tokens': tokens,
            'word_alternatives': word_alternatives,
            'has_alternatives': bool(word_alternatives)
        })
    
    # Step 2: Batch BERT processing for all sentences with alternatives
    sentences_with_alternatives = [s for s in sentences_data if s['has_alternatives']]
    
    if sentences_with_alternatives:
        if verbosity >= 3:
            logger.debug("\n🧠 BATCH ACCEPTABILITY FILTERING (threshold: %.2f)", logit_threshold)
        
        filtered_alternatives = batch_filter_by_acceptability(
            sentences_with_alternatives, logit_threshold, verbosity >= 3
        )
    else:
        filtered_alternatives = {}
    
    # Step 3: Build output for each sentence
    results = []
    
    for sentence_data in sentences_data:
        sentence_id = sentence_data['sentence_id']
        tokens = sentence_data['tokens']
        
        # Get filtered alternatives for this sentence
        position_alternatives = filtered_alternatives.get(sentence_id, {})
        
        # Build output with alternatives
        output_parts = []
        for i, token in enumerate(tokens):
            if not is_word(token):
                output_parts.append(token)
            else:
                alternatives = position_alternatives.get(i)
                if alternatives and len(alternatives) > 1:
                    sorted_alts = sorted(alternatives, key=str.casefold)
                    output_parts.append("[" + "|".join(sorted_alts) + "]")
                else:
                    output_parts.append(token)
        
        raw_result = "".join(output_parts)
        clean_result = postprocess_punctuation(raw_result)
        results.append(clean_result)
    
    return results


# ========================= Ordbank API =========================

def http_get(url: str, headers: Dict[str, str], timeout: float) -> Optional[List]:
    """HTTP GET with retries."""
    for attempt in range(3):
        try:
            response = SESSION.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            logger.debug(
                "HTTP %s for %s (attempt %d/3)",
                response.status_code,
                url,
                attempt + 1,
            )
        except requests.RequestException as e:
            logger.debug("Request failed (attempt %d/3): %r", attempt + 1, e)
            if attempt < 2:
                time.sleep(0.75)
    return None


def search_lemmas(word: str, lang: str, headers: Dict[str, str], timeout: float,
                 pos_filter: Optional[str] = None, debug: bool = False) -> List[Dict]:
    """Search for lemmas matching the word."""
    # Check cache first
    cache_key = make_cache_key("lemmas", word.casefold(), lang, pos_filter or "None")
    cached_result = load_from_cache(cache_key)
    if cached_result is not None:
        if debug:
            logger.debug("💾 CACHE HIT: lemmas for '%s' (POS: %s)", word, pos_filter or 'None')
        return cached_result
    
    if debug:
        logger.debug("🌐 CACHE MISS: fetching lemmas for '%s' from API", word)
    
    query = requests.utils.quote(word.casefold())
    url = (f"{API_BASE}/lemmas?query={query}&stubs=false&include_dict_links=true"
           f"&extended_vocabulary=true&language={lang}&search_inflection=true")
    
    result = http_get(url, headers, timeout) or []
    
    # Filter by POS if specified
    if pos_filter and result:
        result = [lemma for lemma in result 
                 if lemma.get('word_class') == pos_filter]
        if debug:
            logger.debug(
                "POS filtering: %d lemmas remain after filtering for %s",
                len(result),
                pos_filter,
            )
    
    # Save to cache
    save_to_cache(cache_key, result)
    
    return result


def collect_inflections(lemma_ids: List[int], lang: str, headers: Dict[str, str], 
                       timeout: float, debug: bool = False) -> List[Dict]:
    """Collect all inflections for given lemma IDs."""
    inflections = []

    for lemma_id in lemma_ids:
        # Check cache first for this specific lemma
        cache_key = make_cache_key("inflections", lemma_id, lang)
        cached_entries = load_from_cache(cache_key)
        
        if cached_entries is not None:
            if debug:
                logger.debug("💾 CACHE HIT: inflections for lemma %d", lemma_id)
            inflections.extend(cached_entries)
            continue
        
        if debug:
            logger.debug("🌐 CACHE MISS: fetching inflections for lemma %d from API", lemma_id)
        
        # Use the correct API endpoint - query by ID, not direct access
        url = (f"{API_BASE}/lemmas?query={lemma_id}&stubs=false&include_dict_links=true"
               f"&extended_vocabulary=true&language={lang}&search_inflection=false")

        data = http_get(url, headers, timeout)
        if not isinstance(data, list) or not data:
            # Cache empty result to avoid repeated API calls for non-existent lemmas
            save_to_cache(cache_key, [])
            continue

        lemma_data = data[0]  # Take first result

        entries = [
            {
                "lemma_id": lemma_id,
                "word_form": entry.get("word_form"),
                "tags": tuple(entry.get("tags", [])),
            }
            for paradigm in lemma_data.get("paradigm_info", [])
            for entry in paradigm.get("inflection", [])
            if isinstance(entry.get("word_form"), str)
               and isinstance(entry.get("tags", []), list)
        ]
        
        # Save to cache
        save_to_cache(cache_key, entries)
        inflections.extend(entries)

    return inflections


def find_matching_tags(target_word: str, inflections: List[Dict], pos_tag: Optional[str] = None,
                      debug: bool = False, include_imperatives: bool = False, 
                      include_gender_adj: bool = False, exclude_number_ambigious: bool = False) -> Set[Tuple[str, ...]]:
    """Find grammatical tags that match the target word."""
    target_lower = target_word.casefold()
    matching_tags = set()
    
    if debug:
        logger.debug("🏷️ FINDING TAGS FOR: %s", target_word)
    
    for inflection in inflections:
        if inflection["word_form"].casefold() == target_lower:
            matching_tags.add(inflection["tags"])
            if debug:
                logger.debug("   Found match: %s -> %s", inflection["word_form"], inflection["tags"])
    
    # Filter out imperatives unless explicitly requested
    if not include_imperatives:
        has_imperative = any(len(tags) == 1 and tags[0] == 'Imp' 
                            for tags in matching_tags)
        if has_imperative:
            if debug:
                logger.debug("   Word could be imperative - skipping alternatives (use --include_imperatives to override)")
            return set()
    
    # Filter out gender-dependent adjectives unless explicitly requested
    if pos_tag == 'ADJ' and not include_gender_adj:
        has_gender_variants = any(
            any(gender_marker in str(tags) for gender_marker in ['Masc/Fem', 'Neuter'])
            for tags in matching_tags
        )
        if has_gender_variants:
            if debug:
                logger.debug("   ADJ has gender-dependent forms - skipping alternatives (use --include_gender_adj for agreement forms)")
            return set()
    
    # Optionally filter out number-ambiguous nouns
    if pos_tag == 'NOUN' and exclude_number_ambigious:
        has_singular = any('Sing' in str(tags) for tags in matching_tags)
        has_plural = any('Plur' in str(tags) for tags in matching_tags)
        if has_singular and has_plural:
            if debug:
                logger.debug("   NOUN has both singular and plural forms - skipping alternatives (--exclude_number_ambigious active)")
            return set()
    
    # Prioritize simple verb tags over complex ones
    if len(matching_tags) > 1:
        simple_verb_tags = {'Past', 'Pres', 'Inf', 'Imp'}
        simple_tags = {tags for tags in matching_tags 
                      if len(tags) == 1 and tags[0] in simple_verb_tags}
        if simple_tags:
            if debug:
                logger.debug("   Prioritized simple verb tags: %s", simple_tags)
            matching_tags = simple_tags
    
    if debug:
        logger.debug("   Final matching tags: %s", matching_tags)
    
    return matching_tags


def get_alternatives(
    word: str,
    lang: str,
    headers: Dict[str, str],
    timeout: float,
    pos_filter: Optional[str] = None,
    debug: bool = False,
    include_imperatives: bool = False,
    include_gender_adj: bool = False,
    lemma_threshold: int = 1,
    exclude_number_ambigious: bool = False,
    exclude_lamma_multi: bool = False,
) -> Optional[Set[str]]:
    """Get alternative forms for a word."""
    # Search for lemmas
    lemmas = search_lemmas(word, lang, headers, timeout, pos_filter, debug)
    if not lemmas:
        return None

    if debug:
        logger.debug("📝 FOUND %d LEMMAS for %s", len(lemmas), word)
        for i, lemma in enumerate(lemmas):
            logger.debug("   [%d] ID: %s, lemma: %s, class: %s", 
                        i+1, lemma.get("id"), lemma.get("lemma"), lemma.get("word_class"))
    
    # Find all lemmas that contain the target word
    matching_lemmas = []
    seen_lemma_ids: Set[int] = set()
    target_word_lower = word.casefold()
    
    for lemma in lemmas:
        if "id" not in lemma:
            continue
            
        lemma_id = int(lemma["id"])
        inflections = collect_inflections([lemma_id], lang, headers, timeout, debug)
        
        # Check if this lemma contains our target word
        contains_word = any(inf["word_form"].casefold() == target_word_lower 
                           for inf in inflections)
        
        if contains_word:
            matching_lemmas.append({
                "id": lemma_id,
                "inflections": inflections,
                "lemma_info": lemma,
            })
            seen_lemma_ids.add(lemma_id)
            if debug:
                logger.debug("   ✅ LEMMA %d: Contains '%s' (%d inflections)", 
                            lemma_id, word, len(inflections))
        elif debug:
            logger.debug("   ❌ LEMMA %d: Does NOT contain '%s'", lemma_id, word)
    
    if not matching_lemmas:
        if debug:
            logger.debug("   💥 NO LEMMAS contain the target word '%s'", word)
        return None

    # Filter by lemma threshold to avoid semantic confusion
    base_lemma_ids = set(seen_lemma_ids)
    if len(base_lemma_ids) > lemma_threshold:
        if debug:
            logger.debug("   🚫 LEMMA THRESHOLD: Word spans %d lemmas (threshold: %d) - avoiding semantic confusion", 
                        len(base_lemma_ids), lemma_threshold)
        return None

    # Expand with multi-lemma relations unless explicitly disabled
    if not exclude_lamma_multi:
        extra_ids = _expand_multi_lemma_ids(lang, base_lemma_ids) - base_lemma_ids
        if extra_ids and debug:
            logger.debug("   🔁 MULTI-LEMMA EXPANSION: %s -> %s", sorted(base_lemma_ids), sorted(extra_ids))

        for extra_id in sorted(extra_ids):
            if extra_id in seen_lemma_ids:
                continue
            extra_inflections = collect_inflections([extra_id], lang, headers, timeout, debug)
            if not extra_inflections:
                continue
            matching_lemmas.append({
                "id": extra_id,
                "inflections": extra_inflections,
                "lemma_info": {"id": extra_id},
            })
            seen_lemma_ids.add(extra_id)

    # Combine all alternatives from matching lemmas
    all_inflections = []
    for lemma_data in matching_lemmas:
        all_inflections.extend(lemma_data["inflections"])
    
    if debug:
        logger.debug("📋 COMBINED INFLECTIONS from %d matching lemmas:", len(matching_lemmas))
        for i, inf in enumerate(all_inflections):
            logger.debug("   [%d] word_form='%s', tags=%s", i+1, inf["word_form"], inf["tags"])
        logger.debug("   Total: %d inflections", len(all_inflections))
    
    # Find matching grammatical tags
    matching_tags = find_matching_tags(
        word,
        all_inflections,
        pos_filter,
        debug,
        include_imperatives,
        include_gender_adj,
        exclude_number_ambigious,
    )
    if not matching_tags:
        return None

    # Collect alternatives with matching tags
    alternatives = set()
    if debug:
        logger.debug("🔍 COLLECTING ALTERNATIVES WITH MATCHING TAGS:")
    for inflection in all_inflections:
        if inflection["tags"] in matching_tags:
            alternatives.add(inflection["word_form"])
            if debug:
                logger.debug("   ✅ %s (tags: %s)", inflection["word_form"], inflection["tags"])
        elif debug:
            logger.debug("   ❌ %s (tags: %s) - doesn't match", inflection["word_form"], inflection["tags"])
    
    if debug:
        logger.debug("   Final alternatives: %s", sorted(alternatives))
    
    # Only return if we have real alternatives
    if len({alt.casefold() for alt in alternatives}) <= 1:
        return None

    return alternatives


# ========================= Text Processing =========================

def preprocess_punctuation(text: str) -> str:
    """Insert spaces before punctuation to ensure proper tokenization."""
    # Insert space before common punctuation marks if not already there
    # This ensures "matten." becomes "matten ." for proper tokenization
    return re.sub(r'(?<!\s)([,.;:?!])', r' \1', text)


def postprocess_punctuation(text: str) -> str:
    """Remove extra spaces before punctuation from final output."""
    # Remove the spaces we added during preprocessing
    return re.sub(r'\s+([,.;:?!])', r'\1', text)


def tokenize_preserve(text: str) -> List[str]:
    """Tokenize text while preserving exact spacing and punctuation."""
    return re.findall(r'\S+|\s+', text)


def is_word(token: str) -> bool:
    """Check if token is a word (contains letters)."""
    return bool(re.search(r'[a-zA-ZæøåÆØÅ]', token))


def normalize_token(token: str) -> str:
    """Lowercase token with punctuation stripped for matching."""
    return re.sub(r'[^\w]', '', token.casefold())


def case_match(original: str, target: str) -> str:
    """Match the casing pattern of original string to target."""
    if original.islower():
        return target.lower()
    elif original.isupper():
        return target.upper()
    elif original.istitle():
        return target.capitalize()
    return target


def get_unique_words(tokens: List[str]) -> List[str]:
    """Extract unique word forms from tokens."""
    unique_words = []
    seen = set()
    
    for token in tokens:
        if is_word(token):
            word_lower = token.casefold()
            if word_lower not in seen:
                seen.add(word_lower)
                unique_words.append(word_lower)
    
    return unique_words


# ========================= Main Processing =========================

def process_sentence(sentence: str, lang: str, api_key: str, timeout: float,
                    max_workers: int, verbosity: int = 0, logit_threshold: float = 2.0, 
                    include_imperatives: bool = False, include_determinatives: bool = False,
                    include_gender_adj: bool = False, lemma_threshold: int = 1, 
                    exclude_number_ambigious: bool = False,
                    exclude_lamma_multi: bool = False) -> str:
    """Process sentence and return alternatives."""
    
    headers = {"x-api-key": api_key.strip()}
    
    # Preprocess: add spaces before punctuation for proper tokenization
    preprocessed = preprocess_punctuation(sentence)
    tokens = tokenize_preserve(preprocessed)

    if verbosity >= 2:
        logger.debug("\n🎯 PROCESSING: %s", sentence)
        logger.debug("   Language: %s, Threshold: %.2f, Lemma threshold: %d", lang, logit_threshold, lemma_threshold)
    
    # Extract unique words and get POS tags (using preprocessed text for consistency)
    unique_words = get_unique_words(tokens)
    pos_tags = extract_pos_tags(preprocessed)
    
    if verbosity >= 2:
        logger.debug("\n📝 WORDS: %s", unique_words)
        logger.debug("\n🏷️ POS TAGS:")
        for word, pos in pos_tags.items():
            logger.debug("   %s: %s", word, pos)
    
    # Filter out determiners unless explicitly requested
    if not include_determinatives:
        filtered_words = []
        for word in unique_words:
            pos_tag = pos_tags.get(word)
            if pos_tag == 'DET':
                if verbosity >= 2:
                    logger.debug("   🚫 SKIPPING %s: POS=DET (use --include_determinatives to override)", word)
            else:
                filtered_words.append(word)
        unique_words = filtered_words
        
        if verbosity >= 2 and len(filtered_words) < len(get_unique_words(tokens)):
            logger.debug("   📋 FILTERED WORDS: %s", unique_words)
    
    # Fetch alternatives from API
    cache = {}
    with cf.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        
        for word in unique_words:
            pos_tag = pos_tags.get(word)
            if verbosity >= 2:
                logger.debug("\n📡 API LOOKUP: %s (POS: %s)", word, pos_tag or 'None')
            
            future = executor.submit(
                get_alternatives,
                word,
                lang,
                headers,
                timeout,
                pos_tag,
                verbosity >= 2,
                include_imperatives,
                include_gender_adj,
                lemma_threshold,
                exclude_number_ambigious,
                exclude_lamma_multi,
            )
            futures[future] = word
        
        for future in cf.as_completed(futures):
            word = futures[future]
            try:
                result = future.result()
                cache[word] = result
                if verbosity >= 2:
                    if result:
                        logger.debug(
                            "   ✅ %s: %d alternatives: %s",
                            word,
                            len(result),
                            sorted(result),
                        )
                    else:
                        logger.debug("   ❌ %s: No alternatives found", word)
            except Exception as e:
                cache[word] = None
                if verbosity >= 2:
                    logger.debug("   💥 %s: Failed: %s", word, e)
    
    # Apply acceptability filtering
    position_alternatives = {}
    has_alternatives = any(
        (alts := cache.get(token.casefold())) and len(alts) > 1
        for token in tokens
        if is_word(token)
    )
    
    if has_alternatives:
        if verbosity >= 3:
            logger.debug("\n🧠 ACCEPTABILITY FILTERING (threshold: %.2f)", logit_threshold)
        
        for i, token in enumerate(tokens):
            if is_word(token):
                alternatives = cache.get(token.casefold())
                if alternatives and len(alternatives) > 1:
                    
                    if verbosity >= 3:
                        context = "".join(
                            f"[{t}]" if j == i else t
                            for j, t in enumerate(tokens)
                        )
                        logger.debug("\n🔍 ANALYZING: %s (position %d)", token, i)
                        logger.debug("   Context: %s", context)
                        logger.debug("   Alternatives: %s", sorted(alternatives))
                    
                    filtered = filter_by_acceptability(
                        tokens, i, alternatives, logit_threshold, verbosity >= 3
                    )
                    position_alternatives[i] = filtered
    
    # Build output with alternatives
    output_parts = []
    for i, token in enumerate(tokens):
        if not is_word(token):
            output_parts.append(token)
            continue

        # Use position-specific alternatives if available
        alternatives = position_alternatives.get(i) or cache.get(token.casefold())
        
        if not alternatives or len(alternatives) <= 1:
            output_parts.append(token)
            continue

        # Format alternatives with proper casing
        cased_alts = [case_match(token, alt) for alt in alternatives]
        normalized = {alt.casefold(): alt for alt in cased_alts}
        normalized.setdefault(token.casefold(), token)
        
        # Order: original first, then others sorted
        original = case_match(token, normalized[token.casefold()])
        others = sorted([
            case_match(token, alt) for key, alt in normalized.items()
            if key != token.casefold()
        ], key=str.casefold)
        
        ordered = [original] + others
        output_parts.append("[" + "|".join(ordered) + "]")
    
    # Join output parts and remove extra spaces from preprocessing
    raw_result = "".join(output_parts)
    clean_result = postprocess_punctuation(raw_result)
    result = clean_result
    
    if verbosity >= 2:
        logger.debug("\n✨ RESULT: %s", result)
    
    return result


# ========================= CLI =========================

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AltMorph: Context-aware Norwegian morphological alternative generator"
    )
    parser.add_argument("--sentence", 
                       help="Input sentence to process")
    parser.add_argument("--lang", default="nob", choices=["nob", "nno"],
                       help="Language code (default: nob)")
    parser.add_argument("--api_key", default=os.getenv("ORDBANK_API_KEY", ""),
                       help="Ordbank API key (or set ORDBANK_API_KEY)")
    parser.add_argument("--timeout", type=float, default=6.0,
                       help="HTTP timeout per request (default: 6.0)")
    parser.add_argument("--max_workers", type=int, default=4,
                       help="Parallel API requests (default: 4)")
    parser.add_argument("--verbosity", type=int, default=0, choices=[0, 1, 2, 3],
                       help="Verbosity level: 0=quiet, 1=normal, 2=verbose, 3=very verbose (default: 0)")
    parser.add_argument("--logit-threshold", type=float, default=99.0,
                       help="Acceptability threshold (default: 99.0)")
    parser.add_argument("--lemma_threshold", type=int, default=99,
                       help="Maximum lemmas before filtering to avoid semantic confusion (default: 99)")
    parser.add_argument("--include_imperatives", action="store_true",
                       help="Include imperative alternatives (default: False)")
    parser.add_argument("--include_determinatives", action="store_true",
                       help="Include determiner alternatives like en/ei (default: False)")
    parser.add_argument("--include_gender_adj", action="store_true",
                       help="Include gender-dependent adjective alternatives (default: False)")
    parser.add_argument("--exclude_number_ambigious", action="store_true",
                       help="Exclude alternatives for nouns that have both singular and plural forms")
    parser.add_argument("--exclude_lamma_multi", action="store_true",
                       help="Disable merging of linked lemma ids defined in data/lemma-multi")
    parser.add_argument("--batch_size", type=int, default=50,
                       help="Batch size for processing multiple sentences (default: 50)")
    parser.add_argument("--no-cache", action="store_true",
                       help="Disable caching (always fetch from API)")
    parser.add_argument("--delete-cache", action="store_true",
                       help="Delete all cache files and exit")
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Map verbosity to logging levels
    log_levels = {
        0: logging.ERROR,    # quiet - only errors
        1: logging.INFO,     # normal - basic progress
        2: logging.DEBUG,    # verbose - processing details  
        3: logging.DEBUG     # very verbose - everything including cache
    }

    # Configure clean logging for verbosity levels
    if args.verbosity >= 2:
        # Clean format for verbosity output - no timestamps or level names
        logging.basicConfig(
            level=log_levels.get(args.verbosity, logging.ERROR),
            format="%(message)s"
        )
    else:
        # Standard format for errors and basic info
        logging.basicConfig(
            level=log_levels.get(args.verbosity, logging.ERROR),
            format="%(asctime)s %(levelname)s %(message)s"
        )

    # Handle cache management
    if hasattr(args, 'delete_cache') and args.delete_cache:
        delete_cache()
        print("Cache cleared successfully.")
        sys.exit(0)
    
    # Validate required arguments for normal processing
    if not args.sentence:
        logger.error("Missing required argument: --sentence")
        sys.exit(2)
    
    if hasattr(args, 'no_cache') and args.no_cache:
        set_cache_enabled(False)
        if args.verbosity >= 2:
            logger.info("🚫 Cache disabled")

    if not args.api_key:
        logger.error("Missing API key. Use --api_key or set ORDBANK_API_KEY.")
        sys.exit(2)

    try:
        result = process_sentence(
            sentence=args.sentence,
            lang=args.lang,
            api_key=args.api_key,
            timeout=args.timeout,
            max_workers=max(1, args.max_workers),
            verbosity=args.verbosity,
            logit_threshold=args.logit_threshold,
            include_imperatives=args.include_imperatives,
            include_determinatives=args.include_determinatives,
            include_gender_adj=args.include_gender_adj,
            lemma_threshold=args.lemma_threshold,
            exclude_number_ambigious=args.exclude_number_ambigious,
            exclude_lamma_multi=args.exclude_lamma_multi,
        )
        print(result)
        
        # Report cache statistics in verbose mode
        if args.verbosity >= 3 and _cache_enabled:
            stats = get_cache_stats()
            total = stats["hits"] + stats["misses"]
            if total > 0:
                hit_rate = stats["hits"] / total * 100
                logger.debug("📊 CACHE STATS: %d hits, %d misses (%.1f%% hit rate)", 
                           stats["hits"], stats["misses"], hit_rate)
            else:
                logger.debug("📊 CACHE STATS: No cache operations performed")
    except KeyboardInterrupt:
        logger.warning("Interrupted.")
        sys.exit(130)
    except Exception as e:
        logger.exception("Failed to process sentence: %r", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
