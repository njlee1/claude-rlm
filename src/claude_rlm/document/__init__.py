"""
Document processing — ingestors and multi-document registry.
"""

from .ingestors import IngestorChain, TextIngestor, PDFIngestor, DocxIngestor
from .registry import DocumentRegistry, DocumentMeta

__all__ = [
    "IngestorChain",
    "TextIngestor",
    "PDFIngestor",
    "DocxIngestor",
    "DocumentRegistry",
    "DocumentMeta",
]
