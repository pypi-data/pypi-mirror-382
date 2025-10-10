import importlib

import altmorph


def test_module_importable():
    """Ensure the package exposes a main entry point."""
    assert callable(altmorph.main)


def test_multi_lemma_resources_available():
    """The packaged lemma multi CSVs should load without network access."""
    mapping = altmorph._load_multi_lemma_map("nob")
    assert mapping, "Expected multi-lemma map for 'nob' to be non-empty"

    # Spot-check that the helper expands linked IDs
    some_ids = next(iter(mapping.values()))
    assert any(isinstance(val, int) for val in some_ids)


def test_cli_entry_point_loadable():
    """Importing the console script target should succeed."""
    module = importlib.import_module("altmorph")
    assert hasattr(module, "main")
