"""
Tests for document ingestors and registry.
"""

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from claude_rlm.document import (
    IngestorChain,
    TextIngestor,
    DocumentRegistry,
    DocumentMeta,
)


# =============================================================================
# TextIngestor
# =============================================================================


def test_text_ingestor_handles_txt():
    """TextIngestor handles .txt files."""
    ingestor = TextIngestor()
    assert ingestor.can_handle(Path("report.txt"))
    assert ingestor.can_handle(Path("data.csv"))
    assert not ingestor.can_handle(Path("report.pdf"))


def test_text_ingestor_extracts():
    """TextIngestor reads file content."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False
    ) as f:
        f.write("Revenue: $1.8M")
        f.flush()
        ingestor = TextIngestor()
        text = ingestor.extract(Path(f.name))
        assert "Revenue: $1.8M" in text
    Path(f.name).unlink()


# =============================================================================
# IngestorChain
# =============================================================================


def test_ingestor_chain_txt():
    """IngestorChain handles .txt files."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False
    ) as f:
        f.write("Test document content")
        f.flush()
        chain = IngestorChain()
        text = chain.ingest(Path(f.name))
        assert "Test document content" in text
    Path(f.name).unlink()


def test_ingestor_chain_missing_file():
    """IngestorChain raises FileNotFoundError for missing files."""
    chain = IngestorChain()
    with pytest.raises(FileNotFoundError):
        chain.ingest(Path("/nonexistent/file.txt"))


def test_ingestor_chain_unknown_ext_fallback():
    """IngestorChain falls back to plain text for unknown extensions."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".xyz", delete=False
    ) as f:
        f.write("plain text in weird extension")
        f.flush()
        chain = IngestorChain()
        text = chain.ingest(Path(f.name))
        assert "plain text in weird extension" in text
    Path(f.name).unlink()


# =============================================================================
# DocumentRegistry
# =============================================================================


def test_registry_load_and_get():
    """Load and retrieve a document."""
    registry = DocumentRegistry()
    meta = registry.load("doc1", "test.txt", "Hello World")
    assert meta.doc_id == "doc1"
    assert meta.char_count == 11
    assert registry.get("doc1") == "Hello World"


def test_registry_load_text():
    """load_text convenience method."""
    registry = DocumentRegistry()
    meta = registry.load_text("memo", "Internal memo content")
    assert meta.source == "text"
    assert "memo" in registry


def test_registry_missing_document():
    """Accessing a missing document raises KeyError."""
    registry = DocumentRegistry()
    with pytest.raises(KeyError):
        registry.get("nonexistent")


def test_registry_active_document():
    """Most recently loaded document is active."""
    registry = DocumentRegistry()
    registry.load_text("doc1", "first")
    registry.load_text("doc2", "second")
    assert registry.get_active() == "second"


def test_registry_combined_context():
    """Combined context merges documents with markers."""
    registry = DocumentRegistry()
    registry.load_text("apple", "Apple revenue: $1M")
    registry.load_text("google", "Google revenue: $2M")
    combined = registry.get_combined_context(["apple", "google"])
    assert "=== DOCUMENT: apple ===" in combined
    assert "=== DOCUMENT: google ===" in combined
    assert "Apple revenue: $1M" in combined
    assert "Google revenue: $2M" in combined


def test_registry_remove():
    """Remove a document from the registry."""
    registry = DocumentRegistry()
    registry.load_text("doc1", "text")
    assert len(registry) == 1
    registry.remove("doc1")
    assert len(registry) == 0
    assert "doc1" not in registry


def test_registry_list_documents():
    """list_documents returns metadata for all loaded docs."""
    registry = DocumentRegistry()
    registry.load_text("a", "aaa")
    registry.load_text("b", "bbb")
    docs = registry.list_documents()
    assert len(docs) == 2
    assert docs[0].doc_id == "a"
