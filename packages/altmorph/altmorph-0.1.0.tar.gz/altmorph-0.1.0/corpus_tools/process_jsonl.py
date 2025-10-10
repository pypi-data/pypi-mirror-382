#!/usr/bin/env python3
"""
Process JSONL files with AltMorph: Add morphological alternatives to text fields.

This script reads a JSONL (JSON Lines) file where each line contains a JSON object
with a "text" field. It processes each text through AltMorph to generate morphological
alternatives and adds the result as an "alt" field.

Features:
- Batched BERT processing for improved performance
- Automatic resume functionality
- Progress reporting with regular flushing
- Configurable batch sizes for optimal performance

Usage Examples:
    python corpus_tools/process_jsonl.py --input_file data.jsonl --output_file enhanced.jsonl
    python corpus_tools/process_jsonl.py --input_file texts.jsonl --api_key your_key --lang nno
    python corpus_tools/process_jsonl.py --input_file large.jsonl --verbosity 2 --max_workers 8 --batch_size 100

Requirements:
    - Input JSONL file with "text" field in each JSON object
    - Ordbank API key (via --api_key or ORDBANK_API_KEY environment variable)
    - altmorph package available on the PYTHONPATH (run from repo root or install via pip)

Output:
    - JSONL file with original fields plus "alt" field containing alternatives
    - Progress information based on verbosity level
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Import altmorph functions from parent directory
try:
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))
    
    # Debug info
    altmorph_pkg = parent_dir / "altmorph" / "__init__.py"
    if not altmorph_pkg.exists():
        print(f"Error: altmorph package not found at {altmorph_pkg.parent}")
        sys.exit(1)
    
    from altmorph import process_sentences_batch
except ImportError as e:
    print(f"Error importing altmorph: {e}")
    print(f"Python path: {sys.path[:3]}...")  # Show first few paths
    parent_dir = Path(__file__).parent.parent
    print(f"Parent directory: {parent_dir}")
    print(f"Contents in parent: {list(parent_dir.iterdir())[:5]}")
    sys.exit(1)


def count_output_lines(output_file: str) -> int:
    """Count existing lines in output file for resume functionality."""
    if not Path(output_file).exists():
        return 0
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            return sum(1 for line in f if line.strip())
    except Exception:
        return 0


def process_jsonl_file(
    input_file: str,
    output_file: str,
    lang: str,
    api_key: str,
    timeout: float,
    max_workers: int,
    verbosity: int,
    logit_threshold: float,
    include_imperatives: bool = False,
    include_determinatives: bool = False,
    include_gender_adj: bool = False,
    lemma_threshold: int = 1,
    exclude_number_ambigious: bool = False,
    exclude_lamma_multi: bool = False,
    batch_size: int = 50,
) -> None:
    """
    Process JSONL file by adding morphological alternatives to each text field.
    Uses batched BERT processing for improved performance.
    Supports automatic resume by skipping already processed lines.
    """
    if not Path(input_file).exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    if not api_key.strip():
        raise ValueError("API key required. Set ORDBANK_API_KEY environment variable or use --api_key")
    
    # Check for resume
    existing_lines = count_output_lines(output_file)
    file_mode = 'a' if existing_lines > 0 else 'w'
    
    if existing_lines > 0 and verbosity >= 1:
        print(f"📋 RESUMING: Found {existing_lines} existing lines, starting from line {existing_lines + 1}")
    
    processed_count = 0
    error_count = 0
    total_processed = existing_lines
    start_time = time.time()
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, file_mode, encoding='utf-8') as outfile:
        
        sentence_batch = []
        line_data_batch = []
        line_num = 0
        
        for line in infile:
            line_num += 1
            line = line.strip()
            if not line:
                continue
            
            # Skip already processed lines for resume
            if line_num <= existing_lines:
                continue
            
            try:
                # Parse JSON line
                data = json.loads(line)
                
                # Check if "text" field exists
                if "text" not in data:
                    if verbosity >= 1:
                        print(f"Warning: Line {line_num} missing 'text' field, skipping")
                    continue
                
                text = data["text"]
                if not isinstance(text, str) or not text.strip():
                    if verbosity >= 1:
                        print(f"Warning: Line {line_num} has empty/invalid text, skipping")
                    continue
                
                # Add to batch
                sentence_batch.append(text)
                line_data_batch.append((line_num, data))
                
                # Process batch when full
                if len(sentence_batch) >= batch_size:
                    # Process batch with AltMorph
                    try:
                        if verbosity >= 2:
                            print(f"Processing batch of {len(sentence_batch)} sentences (lines {line_data_batch[0][0]}-{line_data_batch[-1][0]})")
                        
                        alt_texts = process_sentences_batch(
                            sentences=sentence_batch,
                            lang=lang,
                            api_key=api_key,
                            timeout=timeout,
                            max_workers=max_workers,
                            verbosity=max(0, verbosity - 2),
                            logit_threshold=logit_threshold,
                            include_imperatives=include_imperatives,
                            include_determinatives=include_determinatives,
                            include_gender_adj=include_gender_adj,
                            lemma_threshold=lemma_threshold,
                            exclude_number_ambigious=exclude_number_ambigious,
                            exclude_lamma_multi=exclude_lamma_multi,
                        )
                        
                        # Write results
                        for (batch_line_num, batch_data), alt_text in zip(line_data_batch, alt_texts):
                            batch_data["alt"] = alt_text
                            outfile.write(json.dumps(batch_data, ensure_ascii=False) + '\n')
                            processed_count += 1
                            total_processed += 1
                        
                        # Progress reporting and flushing
                        outfile.flush()  # Ensure data is written to disk
                        elapsed = time.time() - start_time
                        lines_per_sec = processed_count / elapsed if elapsed > 0 else 0
                        if verbosity >= 1 and processed_count % 100 == 0:
                            print(f"✅ Progress: {total_processed} lines processed ({processed_count} new) | "
                                  f"{lines_per_sec:.1f} lines/sec | {error_count} errors")
                        
                    except Exception as e:
                        error_count += len(sentence_batch)
                        if verbosity >= 1:
                            print(f"Error processing batch ending at line {line_num}: {e}")
                    
                    # Reset batch
                    sentence_batch = []
                    line_data_batch = []
                    
            except json.JSONDecodeError as e:
                error_count += 1
                if verbosity >= 1:
                    print(f"Error: Line {line_num} invalid JSON: {e}")
                continue
                
            except Exception as e:
                error_count += 1
                if verbosity >= 1:
                    print(f"Error processing line {line_num}: {e}")
                continue
        
        # Process remaining sentences in final batch
        if sentence_batch:
            try:
                if verbosity >= 2:
                    print(f"Processing final batch of {len(sentence_batch)} sentences")
                
                alt_texts = process_sentences_batch(
                    sentences=sentence_batch,
                    lang=lang,
                    api_key=api_key,
                    timeout=timeout,
                    max_workers=max_workers,
                    verbosity=max(0, verbosity - 2),
                    logit_threshold=logit_threshold,
                    include_imperatives=include_imperatives,
                    include_determinatives=include_determinatives,
                    include_gender_adj=include_gender_adj,
                    lemma_threshold=lemma_threshold,
                    exclude_number_ambigious=exclude_number_ambigious,
                    exclude_lamma_multi=exclude_lamma_multi,
                )
                
                # Write results
                for (batch_line_num, batch_data), alt_text in zip(line_data_batch, alt_texts):
                    batch_data["alt"] = alt_text
                    outfile.write(json.dumps(batch_data, ensure_ascii=False) + '\n')
                    processed_count += 1
                    total_processed += 1
                
            except Exception as e:
                error_count += len(sentence_batch)
                if verbosity >= 1:
                    print(f"Error processing final batch: {e}")
        
        # Final flush (inside the with block)
        try:
            outfile.flush()
        except Exception:
            pass  # File might already be closed
    
    # Final summary
    elapsed = time.time() - start_time
    if verbosity >= 1:
        print(f"\n🎯 Processing complete!")
        print(f"   📊 New lines processed: {processed_count}")
        print(f"   📁 Total lines in output: {total_processed}")
        print(f"   ⚠️  Errors encountered: {error_count}")
        print(f"   ⏱️  Processing time: {elapsed:.1f}s")
        if processed_count > 0:
            print(f"   🚀 Average speed: {processed_count / elapsed:.1f} lines/sec")


def main() -> None:
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Process JSONL files with AltMorph morphological alternatives (batched processing)"
    )
    
    parser.add_argument("--input_file", required=True,
                       help="Input JSONL file with 'text' fields")
    parser.add_argument("--output_file", required=True, 
                       help="Output JSONL file with added 'alt' fields")
    parser.add_argument("--lang", default="nob", choices=["nob", "nno"],
                       help="Language code (default: nob)")
    parser.add_argument("--api_key", default=os.getenv("ORDBANK_API_KEY", ""),
                       help="Ordbank API key (or set ORDBANK_API_KEY)")
    parser.add_argument("--timeout", type=float, default=6.0,
                       help="HTTP timeout per request (default: 6.0)")
    parser.add_argument("--max_workers", type=int, default=4,
                       help="Parallel API requests (default: 4)")
    parser.add_argument("--verbosity", type=int, default=1, choices=[0, 1, 2, 3],
                       help="Verbosity level: 0=quiet, 1=normal, 2=verbose, 3=very verbose (default: 1)")
    parser.add_argument("--logit_threshold", type=float, default=3.0,
                       help="BERT acceptability threshold (default: 3.0)")
    parser.add_argument("--lemma_threshold", type=int, default=1,
                       help="Maximum lemmas before filtering to avoid semantic confusion (default: 1)")
    parser.add_argument("--include_imperatives", action="store_true",
                       help="Include imperative alternatives (default: False)")
    parser.add_argument("--include_determinatives", action="store_true",
                       help="Include determiner alternatives like en/ei (default: False)")
    parser.add_argument("--include_gender_adj", action="store_true",
                       help="Include gender-dependent adjective alternatives (default: False)")
    parser.add_argument("--exclude_number_ambigious", action="store_true",
                       help="Exclude alternatives for nouns that are ambiguous between singular and plural")
    parser.add_argument("--exclude_lamma_multi", action="store_true",
                       help="Disable merging of linked lemma ids from data/lemma-multi")
    parser.add_argument("--batch_size", type=int, default=100,
                       help="Batch size for processing sentences (default: 50)")
    
    args = parser.parse_args()
    
    # Configure logging
    log_levels = {
        0: logging.ERROR,
        1: logging.INFO,
        2: logging.DEBUG,
        3: logging.DEBUG
    }
    
    logging.basicConfig(
        level=log_levels.get(args.verbosity, logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s"
    )
    
    try:
        process_jsonl_file(
            input_file=args.input_file,
            output_file=args.output_file,
            lang=args.lang,
            api_key=args.api_key,
            timeout=args.timeout,
            max_workers=args.max_workers,
            verbosity=args.verbosity,
            logit_threshold=args.logit_threshold,
            include_imperatives=args.include_imperatives,
            include_determinatives=args.include_determinatives,
            include_gender_adj=args.include_gender_adj,
            lemma_threshold=args.lemma_threshold,
            exclude_number_ambigious=args.exclude_number_ambigious,
            exclude_lamma_multi=args.exclude_lamma_multi,
            batch_size=args.batch_size
        )
        
    except KeyboardInterrupt:
        print("\n⚠️ Processing interrupted by user")
        print("💾 Progress has been saved. You can resume by running the same command.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
