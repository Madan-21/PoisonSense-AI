# Vector embeddings model — stored in Postgres via pgvector
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Index
from pgvector.sqlalchemy import Vector
from datetime import datetime, timezone
from app.db.base import Base
from app.core.config import settings


class DocumentChunk(Base):
    """Stores document chunks with their vector embeddings for RAG retrieval."""
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String(100), unique=True, nullable=False, index=True)
    doc_id = Column(String(100), nullable=False, index=True)
    doc_title = Column(String(500), nullable=False)
    collection_name = Column(String(100), nullable=False, index=True, default="general")

    # The actual text content
    text = Column(Text, nullable=False)

    # Vector embedding (dimension matches HF all-MiniLM-L6-v2 = 384)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSIONS), nullable=False)

    # Metadata
    source_path = Column(String(500))
    page = Column(Integer, default=0)
    section = Column(String(500), default="")
    content_hash = Column(String(64), index=True)  # for dedup

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Indexes for fast retrieval
    __table_args__ = (
        Index("idx_chunks_collection", "collection_name"),
        Index("idx_chunks_doc_id", "doc_id"),
    )

    def __repr__(self):
        return f"<DocumentChunk {self.chunk_id} collection={self.collection_name}>"
