#!/usr/bin/env python3
"""
Book content ingestion script for RAG chatbot.

Reads markdown files from the book directory, chunks them,
generates embeddings, and stores them in Qdrant with metadata in Postgres.

Usage:
    python -m src.scripts.ingest_book
    python -m src.scripts.ingest_book --book-path ../book --force
"""

import argparse
import asyncio
import hashlib
import logging
import re
from pathlib import Path
from typing import Optional
from uuid import uuid4

from openai import AsyncOpenAI
from qdrant_client import models as qdrant_models

from src.config import get_settings
from src.db.postgres import init_db, close_db, get_db
from src.db.qdrant import init_qdrant, close_qdrant, upsert_vectors, get_qdrant
from src.models.document import DocumentChunk

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class BookIngestor:
    """Ingests book markdown content into vector database."""

    def __init__(
        self,
        book_path: Path,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ):
        self.book_path = book_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.settings = get_settings()
        self.openai = AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.stats = {"files": 0, "chunks": 0, "skipped": 0}

    async def run(self, force: bool = False) -> dict:
        """
        Run the ingestion process.

        Args:
            force: If True, re-ingest all content even if unchanged.

        Returns:
            Statistics dictionary.
        """
        logger.info(f"Starting book ingestion from: {self.book_path}")

        # Find all markdown files
        md_files = list(self.book_path.rglob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files")

        for md_file in md_files:
            await self._process_file(md_file, force)

        logger.info(
            f"Ingestion complete: {self.stats['files']} files, "
            f"{self.stats['chunks']} chunks, {self.stats['skipped']} skipped"
        )
        return self.stats

    async def _process_file(self, file_path: Path, force: bool) -> None:
        """Process a single markdown file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            # Build source URL from file path
            relative_path = file_path.relative_to(self.book_path)
            source_url = self._path_to_url(relative_path)

            # Check if content changed
            if not force:
                existing = await self._get_existing_hash(source_url)
                if existing == content_hash:
                    logger.debug(f"Skipping unchanged: {file_path.name}")
                    self.stats["skipped"] += 1
                    return

            # Extract metadata
            title, metadata = self._extract_metadata(content, file_path)

            # Chunk the content
            chunks = self._chunk_content(content, title)

            if not chunks:
                logger.warning(f"No chunks generated for: {file_path.name}")
                return

            # Generate embeddings and store
            await self._store_chunks(
                chunks=chunks,
                source_url=source_url,
                content_hash=content_hash,
                metadata=metadata,
            )

            self.stats["files"] += 1
            self.stats["chunks"] += len(chunks)
            logger.info(f"Processed: {file_path.name} ({len(chunks)} chunks)")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

    def _path_to_url(self, relative_path: Path) -> str:
        """Convert file path to documentation URL."""
        # Remove .md extension and convert to URL path
        url_path = str(relative_path).replace("\\", "/")
        url_path = re.sub(r"\.md$", "", url_path)
        url_path = re.sub(r"/README$", "", url_path)  # README -> directory index
        url_path = re.sub(r"^README$", "", url_path)
        return f"/{url_path}" if url_path else "/"

    def _extract_metadata(self, content: str, file_path: Path) -> tuple[str, dict]:
        """Extract title and metadata from markdown content."""
        # Extract title from first H1
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem

        # Extract YAML frontmatter if present
        metadata = {}
        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if frontmatter_match:
            # Simple YAML parsing
            for line in frontmatter_match.group(1).split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip().strip('"\'')

        # Add file path info
        metadata["file_path"] = str(file_path.relative_to(self.book_path))
        metadata["module"] = self._extract_module(file_path)

        return title, metadata

    def _extract_module(self, file_path: Path) -> Optional[str]:
        """Extract module name from file path."""
        parts = file_path.relative_to(self.book_path).parts
        for part in parts:
            if part.startswith("module-"):
                return part
        return None

    def _chunk_content(self, content: str, title: str) -> list[dict]:
        """
        Split content into chunks with section awareness.

        Returns list of dicts with 'text' and 'section_title' keys.
        """
        chunks = []

        # Remove YAML frontmatter
        content = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL)

        # Split by headers while preserving them
        sections = re.split(r"(^#{1,3}\s+.+$)", content, flags=re.MULTILINE)

        current_section = title
        current_text = ""

        for i, part in enumerate(sections):
            # Check if this is a header
            header_match = re.match(r"^(#{1,3})\s+(.+)$", part)
            if header_match:
                # Save accumulated text
                if current_text.strip():
                    chunks.extend(
                        self._split_text(current_text.strip(), current_section)
                    )
                current_section = header_match.group(2)
                current_text = ""
            else:
                current_text += part

        # Don't forget the last section
        if current_text.strip():
            chunks.extend(self._split_text(current_text.strip(), current_section))

        return chunks

    def _split_text(self, text: str, section_title: str) -> list[dict]:
        """Split text into chunks of appropriate size."""
        chunks = []

        # Clean the text
        text = re.sub(r"\n{3,}", "\n\n", text)  # Collapse multiple newlines
        text = re.sub(r"```[\s\S]*?```", "[CODE BLOCK]", text)  # Placeholder for code

        # Split into sentences/paragraphs
        paragraphs = text.split("\n\n")

        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check if adding this paragraph exceeds chunk size
            if len(current_chunk) + len(para) + 2 > self.chunk_size:
                if current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "section_title": section_title,
                    })
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        # Add remaining text
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "section_title": section_title,
            })

        return chunks

    async def _get_existing_hash(self, source_url: str) -> Optional[str]:
        """Get existing content hash from database."""
        async with get_db() as db:
            from sqlalchemy import select
            result = await db.execute(
                select(DocumentChunk.content_hash)
                .where(DocumentChunk.source_url == source_url)
                .limit(1)
            )
            row = result.scalar_one_or_none()
            return row

    async def _store_chunks(
        self,
        chunks: list[dict],
        source_url: str,
        content_hash: str,
        metadata: dict,
    ) -> None:
        """Store chunks in both Postgres and Qdrant."""
        # Delete existing chunks for this URL
        async with get_db() as db:
            from sqlalchemy import delete
            await db.execute(
                delete(DocumentChunk).where(DocumentChunk.source_url == source_url)
            )
            await db.commit()

        # Delete from Qdrant
        client = get_qdrant()
        try:
            client.delete(
                collection_name=self.settings.qdrant_collection,
                points_selector=qdrant_models.FilterSelector(
                    filter=qdrant_models.Filter(
                        must=[
                            qdrant_models.FieldCondition(
                                key="source_url",
                                match=qdrant_models.MatchValue(value=source_url),
                            )
                        ]
                    )
                ),
            )
        except Exception:
            pass  # Collection might not have these points

        # Generate embeddings for all chunks
        texts = [c["text"] for c in chunks]
        embeddings = await self._generate_embeddings(texts)

        # Prepare points for Qdrant
        points = []
        db_chunks = []

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = uuid4()

            points.append(
                qdrant_models.PointStruct(
                    id=str(chunk_id),
                    vector=embedding,
                    payload={
                        "source_url": source_url,
                        "section_title": chunk["section_title"],
                        "content": chunk["text"],
                        "chunk_index": i,
                        **metadata,
                    },
                )
            )

            db_chunks.append(
                DocumentChunk(
                    id=chunk_id,
                    source_url=source_url,
                    section_title=chunk["section_title"],
                    content=chunk["text"],
                    content_hash=content_hash,
                    chunk_index=i,
                    metadata=metadata,
                )
            )

        # Store in Qdrant
        await upsert_vectors(points)

        # Store in Postgres
        async with get_db() as db:
            db.add_all(db_chunks)
            await db.commit()

    async def _generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        # Batch in groups of 100
        all_embeddings = []
        batch_size = 100

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = await self.openai.embeddings.create(
                model=self.settings.openai_embedding_model,
                input=batch,
            )
            all_embeddings.extend([e.embedding for e in response.data])

        return all_embeddings


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Ingest book content into vector database")
    parser.add_argument(
        "--book-path",
        type=Path,
        default=Path(__file__).parent.parent.parent.parent / "book",
        help="Path to book directory",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-ingestion of all content",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=512,
        help="Target chunk size in characters",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=50,
        help="Overlap between chunks",
    )
    args = parser.parse_args()

    # Initialize connections
    await init_db()
    await init_qdrant()

    try:
        ingestor = BookIngestor(
            book_path=args.book_path,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )
        stats = await ingestor.run(force=args.force)
        print(f"\nIngestion complete!")
        print(f"  Files processed: {stats['files']}")
        print(f"  Chunks created: {stats['chunks']}")
        print(f"  Files skipped: {stats['skipped']}")
    finally:
        await close_db()
        await close_qdrant()


if __name__ == "__main__":
    asyncio.run(main())
