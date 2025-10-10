# Corpus Tools

Batch-processing helpers for preparing and cleaning corpora that rely on AltMorph.
All scripts here are runnable modules, mirroring how they have historically been
used on the command line.

## Contents

- `process_jsonl.py` – adds AltMorph alternatives to every `text` field in a JSONL
  dataset. Supports batching, resume-on-interruption, and flags for niche filters
  such as lemma thresholds or gendered adjectives.
- `create_training_examples.py` – samples one variant from each AltMorph block and
  writes an `unnorm` field, useful when training models that need noisy inputs.
- `stream_ncc_text.py` – streams filtered Stortinget speeches from the NCC speech
  dataset on the Hugging Face Hub without downloading audio assets.
- `data/` – small sample corpora and placeholder directories for larger datasets.

## Quick Start

Run the scripts directly from the repository root:

```bash
python corpus_tools/process_jsonl.py --input_file corpus_tools/data/samples/sample_input.jsonl \
  --output_file tmp/output.jsonl --api_key "$ORDBANK_API_KEY"
```

Other handy variants:

Outputs from these scripts use the AltMetrics-style bracket format, e.g.
`[Katta|Katten] ligger på [matta|matten].`

```bash
# Verbose logging
python corpus_tools/process_jsonl.py --input_file ... --output_file ... --verbosity 2

# Sample one variant per block to make noisy training examples
python corpus_tools/create_training_examples.py --input_file tmp/output.jsonl --output_file tmp/unnorm.jsonl

# Stream Stortinget speeches from NCC and write to JSONL
python corpus_tools/stream_ncc_text.py --dataset NbAiLab/ncc_speech_v7 --config no --split train \
  --output corpus_tools/data/stortinget/train.jsonl --max-rows 100
```

Each script expects to import the `altmorph` package, so either run them from the
repository root (which is added to `PYTHONPATH`) or install AltMorph via `pip install altmorph`.

Temporary artefacts should live in an ignored directory such as `corpus_tools/tmp/`
(create it on demand). See the sub-directory READMEs for dataset-specific notes.
