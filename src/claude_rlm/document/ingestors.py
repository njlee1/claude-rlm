"""
Document ingestors — extract text from various file formats.

Each ingestor handles a set of file extensions and returns plain text.
The IngestorChain tries ingestors in order until one succeeds.
"""

import subprocess
from pathlib import Path
from typing import List, Optional


class TextIngestor:
    """Plain text file ingestor (.txt, .md, .csv, .tsv, .log, etc.)."""

    extensions = {".txt", ".md", ".csv", ".tsv", ".log", ".text", ".rst"}

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensions

    def extract(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")


class PDFIngestor:
    """PDF ingestor with fallback chain: docling -> pdftotext."""

    extensions = {".pdf"}

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensions

    def extract(self, path: Path) -> str:
        # Try docling first (best quality)
        try:
            result = subprocess.run(
                [
                    "python3", "-c",
                    "from docling.document_converter import DocumentConverter; "
                    "converter = DocumentConverter(); "
                    f"result = converter.convert('{path}'); "
                    "print(result.document.export_to_markdown())",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
        except Exception:
            pass

        # Fallback to pdftotext
        try:
            result = subprocess.run(
                ["pdftotext", "-layout", str(path), "-"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass

        raise RuntimeError(f"Could not extract text from PDF: {path}")


class DocxIngestor:
    """DOCX ingestor using pandoc."""

    extensions = {".docx", ".doc"}

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensions

    def extract(self, path: Path) -> str:
        try:
            result = subprocess.run(
                ["pandoc", str(path), "-t", "plain"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass

        raise RuntimeError(f"Could not extract text from DOCX: {path}")


class IngestorChain:
    """Chain of ingestors — tries each until one succeeds.

    Falls back to reading as plain text if no ingestor matches.

    Usage:
        chain = IngestorChain()
        text = chain.ingest(Path("report.pdf"))
    """

    def __init__(self, ingestors: Optional[List] = None):
        self._ingestors = ingestors or [
            PDFIngestor(),
            DocxIngestor(),
            TextIngestor(),
        ]

    def ingest(self, path: Path) -> str:
        """Extract text from a file using the first matching ingestor.

        Args:
            path: Path to the document file.

        Returns:
            Extracted text content.

        Raises:
            RuntimeError: If no ingestor can handle the file.
        """
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")

        for ingestor in self._ingestors:
            if ingestor.can_handle(path):
                return ingestor.extract(path)

        # Ultimate fallback: try reading as plain text
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            raise RuntimeError(
                f"No ingestor can handle '{path.suffix}' files: {path}"
            )
