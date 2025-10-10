# AltMorph: Context-Aware Norwegian Morphological Alternative Generator

**AltMorph** is a tool for expanding Norwegian text by finding morphological alternatives for each word. It combines the Ordbank API with NLP techniques to provide alternatives that fit the surrounding context.

Outputs follow the AltMetrics bracket format, listing options as `[original|alt1|alt2]`.

## ✨ Features

- **🎯 Context-sensitive filtering**: Uses BERT-based acceptability scoring for ambiguous cases
- **📚 Lemma coverage**: Finds morphological forms across multiple lemmas
- **🔍 Position-specific analysis**: Looks at each word in its syntactic context  
- **⚡ Caching**: Persistent file-based caching to improve performance
- **🗣️ Multiple verbosity levels**: From silent operation to detailed pipeline insights
- **🌐 Language support**: Norwegian Bokmål (`nob`) and Nynorsk (`nno`)
- **🧠 POS-aware**: Uses NbAiLab BERT models for part-of-speech tagging
- **🚀 Parallel processing**: Runs concurrent API calls

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Ordbank API key (free registration at [Ordbank](https://www.ordbank.no/))

### Install from PyPI
```bash
pip install altmorph
```

### Install from Source (development)
```bash
pip install -e .
```

### Optional: Sync Development Requirements
```bash
pip install -r requirements.txt
```

### Get API Key
1. Register at [https://www.ordbank.no/](https://www.ordbank.no/)
2. Obtain your API key from your account dashboard
3. Set the environment variable:
   ```bash
   export ORDBANK_API_KEY="your_api_key_here"
   ```
   Or pass it directly with `--api_key` flag

## 🚀 Quick Start

After installation you can invoke the CLI either with the `altmorph` command or via `python -m altmorph`.

### Basic Usage
```bash
python -m altmorph --sentence "Katta ligger på matta." --lang nob
```
**Output:**
```
[Katta|Katten] ligger på [matta|matten].
```

### With API Key
```bash
python -m altmorph \
  --sentence "Katta ligger på matta." \
  --lang nob \
  --api_key "your_api_key_here"
```

## 📖 Usage Examples

### Context-Sensitive Behaviour
The tool takes sentence context into account:

**Simple example:**
```bash
python -m altmorph --sentence "Katta ligger på matta." --lang nob
# Output: [Katta|Katten] ligger på [matta|matten].
# Shows different morphological forms for the same words
```

**Complex context:**
```bash
python -m altmorph --sentence "Katta ligger på matta i stua." --lang nob  
# Output: [Katta|Katten] ligger på [matta|matten] i stua.
# BERT-based filtering keeps alternatives that work in the sentence
```

### Position-Specific Analysis
```bash
python -m altmorph --sentence "Katta ligger på matta." --lang nob
# Each word occurrence is analyzed in its specific syntactic context
```

## 🎛️ Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--sentence` | *required* | Input sentence to process |
| `--lang` | `nob` | Language code (`nob` or `nno`) |
| `--api_key` | `$ORDBANK_API_KEY` | Ordbank API key |
| `--verbosity` | `0` | Verbosity level (0-3) |
| `--logit-threshold` | `3.0` | BERT acceptability threshold |
| `--timeout` | `6.0` | HTTP timeout per request |
| `--max_workers` | `4` | Parallel API requests |
| `--no-cache` | `False` | Disable caching |
| `--delete-cache` | `False` | Clear cache and exit |

## 🔊 Verbosity Levels

### Level 0: Quiet (Default)
```bash
python -m altmorph --sentence "Katta ligger på matta." --verbosity 0
```
**Output:** Just the final result
```
[Katta|Katten] ligger på [matta|matten].
```

### Level 1: Normal  
```bash
python -m altmorph --sentence "Katta ligger på matta." --verbosity 1
```
**Output:** Basic progress information
```
2025-XX-XX 12:00:00 INFO Loading POS tagger...
2025-XX-XX 12:00:02 INFO POS tagger loaded
[Katta|Katten] ligger på [matta|matten].
```

### Level 2: Verbose
```bash
python -m altmorph --sentence "Katta ligger på matta." --verbosity 2
```
**Output:** Processing details (POS tags, API lookups, alternatives found)
```
🎯 PROCESSING: Katta ligger på matta.
📝 WORDS: ['katta', 'ligger', 'på', 'matta']
🏷️ POS TAGS:
   katta: NOUN
   ligger: VERB
   på: ADP
   matta: NOUN
📡 API LOOKUP: katta (POS: NOUN)
   ✅ katta: 2 alternatives: ['katta', 'katten']
...
✨ RESULT: [Katta|Katten] ligger på [matta|matten].
```

### Level 3: Very Verbose
```bash
python -m altmorph --sentence "Katta ligger på matta." --verbosity 3
```
**Output:** Everything including cache operations, lemma analysis, BERT filtering
```
🎯 PROCESSING: Katta ligger på matta.
📝 FOUND 2 LEMMAS for katta
💾 CACHE HIT: lemmas for 'katta' (POS: NOUN)
🧠 ACCEPTABILITY FILTERING (threshold: 3.00)
🔍 ANALYZING: katta (position 0)
   Context: [Katta] ligger på matta.
   Alternatives: ['katta', 'katten']
📊 CACHE STATS: 8 hits, 0 misses (100.0% hit rate)
...
```

## 🗂️ Caching System

AltMorph includes caching to improve performance:

- **Cache location:** `~/.ordbank_cache/`
- **Cache types:** Lemma searches and inflection data
- **Performance:** ~95%+ hit rate for repeated usage
- **Management:** 
  - `--no-cache`: Disable caching
  - `--delete-cache`: Clear all cache files

**Performance impact:**
- First run: ~3-4 seconds (API calls)
- Cached runs: ~0.5 seconds

## 🧠 Technical Details

### Code Architecture Deep-Dive
📖 **[Complete Code Walkthrough](docs/code_explanation.md)** - Detailed technical explanation of how AltMorph works for developers who need implementation details.

### Architecture
1. **Input Processing**: Tokenization preserving whitespace and punctuation
2. **POS Tagging**: NbAiLab/nb-bert-base-pos for accurate grammatical analysis
3. **Lemma Discovery**: Comprehensive search across all relevant Ordbank lemmas
4. **Inflection Analysis**: Full morphological paradigm extraction
5. **Acceptability Scoring**: NbAiLab/nb-bert-base for context-sensitive filtering
6. **Output Generation**: Case-preserving alternative presentation

### Models Used
- **POS Tagging**: `NbAiLab/nb-bert-base-pos`
- **Acceptability**: `NbAiLab/nb-bert-base` 
- **API**: [Ordbank](https://www.ordbank.no/) - Norwegian morphological database

### Key Algorithms
- **Comprehensive lemma matching**: Finds all lemmas containing target word
- **Position-specific analysis**: Each word occurrence analyzed in context
- **Logit-based filtering**: Acceptability thresholding (default: 3.0)
- **Prioritization**: Balances morphological coverage with contextual fit

## 📊 Performance

### Typical Performance
- **Single sentence**: 0.5-4 seconds (depending on cache state)
- **Cache hit rate**: Typically 95%+ for repeated usage
- **API efficiency**: Parallel requests with batching
- **Memory usage**: ~500MB (loaded BERT models)

### Scaling Considerations
- **Concurrent requests**: Configurable via `--max_workers`
- **Timeout handling**: Robust error recovery with retries
- **Rate limiting**: Respectful API usage patterns

## 🛠️ Tools

AltMorph includes additional helpers for batch processing and debugging:

- **[`corpus_tools/process_jsonl.py`](corpus_tools/process_jsonl.py)**: Batch-process JSONL files by adding morphological alternatives to text fields (resume-aware, batched).
- **[`corpus_tools/create_training_examples.py`](corpus_tools/create_training_examples.py)**: Sample one variant per alternative block to generate `unnorm` training strings.
- **[`corpus_tools/stream_ncc_text.py`](corpus_tools/stream_ncc_text.py)**: Stream Stortinget speeches from the NCC dataset on Hugging Face.
- **[`scripts/pos_tester.py`](scripts/pos_tester.py)**: Compare POS tagging across Norwegian NLP models.
- **[`scripts/hf_probe_fields.py`](scripts/hf_probe_fields.py)**: Inspect Hugging Face dataset metadata and stream example rows.

Browse [`corpus_tools/README.md`](corpus_tools/README.md) and [`scripts/README.md`](scripts/README.md) for more details.

## 🔧 Development

### Project Structure
```
altmorph/
├── __init__.py                  # Main application / CLI
├── data/                        # Packaged lemma resources
├── corpus_tools/                # Corpus cleaning scripts and sample data
│   ├── process_jsonl.py         # JSONL batch processor
│   ├── create_training_examples.py
│   ├── stream_ncc_text.py
│   └── data/                    # Sample + placeholder corpora
├── docs/                        # Developer documentation
│   └── code_explanation.md
├── legacy/                      # Archived scripts kept for reference
├── scripts/                     # Standalone utilities (POS tester, HF helper)
├── README.md                    # Main documentation
├── pyproject.toml               # Packaging metadata
├── requirements.txt             # Dependencies
├── setup.py                     # Legacy packaging shim
└── ~/.ordbank_cache/            # Cache directory (auto-created)
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure code follows existing style
5. Submit a pull request

### Testing
```bash
# Run the automated test suite
pytest

# Test basic functionality
python -m altmorph --sentence "Katta ligger på matta." --lang nob

# Test cache functionality  
python -m altmorph --delete-cache
python -m altmorph --sentence "Katta ligger på matta." --lang nob --verbosity 3

# Test without cache
python -m altmorph --sentence "Katta ligger på matta." --lang nob --no-cache

# Test POS comparison tool
python scripts/pos_tester.py --text "Katta ligger på matta."

# Test batch processing with sample data
python corpus_tools/process_jsonl.py \
  --input_file corpus_tools/data/samples/sample_input.jsonl \
  --output_file tmp/test_output.jsonl \
  --verbosity 2
```

## 🚢 Release Guide

Ready to publish? Follow the step-by-step instructions in [`docs/RELEASING.md`](docs/RELEASING.md) to build,
test, and upload the package (v0.1.0) to PyPI.

## 🤝 Related Projects

- **[altmetrics](https://github.com/peregilk/altmetrics)**: Depends on AltMorph's output format for Norwegian text evaluation. Allows you to calculate wer, cer, BLEU and chrF based on valid morphological alternatives.

## 📄 License

[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)


## 🙏 Acknowledgments

- **Ordbank Team**: For providing the comprehensive Norwegian morphological API
- **Clarino/UiB**: For hosting the API infrastructure
- **NbAiLab**: For the Norwegian BERT models
- **AltMorph**: Idea and coding by Magnus Breder Birkenes and Per Egil Kummervold
