"""
Multi-document registry.

Manages multiple loaded documents and provides combined context
for cross-document queries.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class DocumentMeta:
    """Metadata for a loaded document."""

    doc_id: str
    source: str  # file path or "text"
    char_count: int
    token_estimate: int  # rough: chars // 4
    preview: str  # first 500 chars


class DocumentRegistry:
    """Registry for managing multiple loaded documents.

    Usage:
        registry = DocumentRegistry()
        registry.load("apple", Path("apple_10k.pdf"), extracted_text)
        registry.load_text("memo", "Internal memo content here...")

        # Single doc
        meta = registry.get("apple")

        # Cross-doc context
        combined = registry.get_combined_context(["apple", "memo"])
    """

    def __init__(self):
        self._documents: Dict[str, str] = {}  # doc_id -> text
        self._metadata: Dict[str, DocumentMeta] = {}
        self._active_id: Optional[str] = None

    def load(self, doc_id: str, source: str, text: str) -> DocumentMeta:
        """Register a document with its extracted text.

        Args:
            doc_id: Unique identifier for this document.
            source: Source path or description.
            text: The extracted document text.

        Returns:
            DocumentMeta for the loaded document.
        """
        self._documents[doc_id] = text
        meta = DocumentMeta(
            doc_id=doc_id,
            source=source,
            char_count=len(text),
            token_estimate=len(text) // 4,
            preview=text[:500],
        )
        self._metadata[doc_id] = meta
        self._active_id = doc_id
        return meta

    def load_text(self, doc_id: str, text: str) -> DocumentMeta:
        """Load text directly (convenience wrapper)."""
        return self.load(doc_id, "text", text)

    def get(self, doc_id: str) -> str:
        """Get the full text of a document by ID."""
        if doc_id not in self._documents:
            raise KeyError(f"Document '{doc_id}' not found. "
                           f"Available: {list(self._documents.keys())}")
        return self._documents[doc_id]

    def get_meta(self, doc_id: str) -> DocumentMeta:
        """Get metadata for a document."""
        if doc_id not in self._metadata:
            raise KeyError(f"Document '{doc_id}' not found.")
        return self._metadata[doc_id]

    def get_active(self) -> Optional[str]:
        """Get the text of the most recently loaded document."""
        if self._active_id and self._active_id in self._documents:
            return self._documents[self._active_id]
        return None

    def get_combined_context(self, doc_ids: List[str]) -> str:
        """Merge multiple documents with section markers.

        Produces a combined context string with clear boundaries:

            === DOCUMENT: apple ===
            [apple text]

            === DOCUMENT: google ===
            [google text]
        """
        parts = []
        for doc_id in doc_ids:
            text = self.get(doc_id)
            parts.append(f"=== DOCUMENT: {doc_id} ===\n{text}")
        return "\n\n".join(parts)

    def list_documents(self) -> List[DocumentMeta]:
        """List all loaded documents."""
        return list(self._metadata.values())

    def remove(self, doc_id: str) -> None:
        """Remove a document from the registry."""
        self._documents.pop(doc_id, None)
        self._metadata.pop(doc_id, None)
        if self._active_id == doc_id:
            self._active_id = None

    def __len__(self) -> int:
        return len(self._documents)

    def __contains__(self, doc_id: str) -> bool:
        return doc_id in self._documents
