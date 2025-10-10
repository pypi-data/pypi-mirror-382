# Utility Scripts

Standalone helpers that can be run directly from the repository root.

- `pos_tester.py` – lightweight harness that compares POS-tagging output from
  Hugging Face, spaCy, and Flair models on the same sentence.
- `hf_probe_fields.py` – quick inspector for Hugging Face datasets, printing
  schema information and streamed sample rows.

Invoke the scripts with `python scripts/<name>.py ...`. They do not form part of
the PyPI package; they exist purely for local experimentation and debugging.
