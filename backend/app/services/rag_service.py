"""
RAG (Retrieval-Augmented Generation) Service for DSA Learning System.

Uses sentence-transformers for embedding + pgvector for vector
similarity search to retrieve relevant DSA textbook content.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from sqlalchemy import text

from app.config import get_settings
from app.models.base import _get_async_session

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class RetrievedDocument:
    """A document retrieved from the knowledge base."""
    id: str
    content: str
    metadata: Dict[str, Any]
    similarity_score: float


class RAGService:
    """
    RAG pipeline for retrieving DSA knowledge base content.

    Workflow:
    1. Embed query using sentence-transformers (MiniLM)
    2. Vector similarity search via pgvector <=> operator
    3. Filter by similarity threshold
    4. Return top-k relevant documents
    5. Format for LLM context injection
    """

    _model = None
    _model_lock = asyncio.Lock()

    def __init__(
        self,
        similarity_threshold: Optional[float] = None,
        top_k: int = 5,
    ):
        self.similarity_threshold = similarity_threshold or settings.RAG_SIMILARITY_THRESHOLD
        self.top_k = top_k
        self.vector_dimension = settings.VECTOR_DIMENSION

    async def _get_model(self):
        """Lazy-load the sentence-transformers model with thread safety."""
        if self._model is None:
            async with self._model_lock:
                if self._model is None:
                    from sentence_transformers import SentenceTransformer
                    logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
                    loop = asyncio.get_event_loop()
                    self._model = await loop.run_in_executor(
                        None,
                        lambda: SentenceTransformer(settings.EMBEDDING_MODEL)
                    )
                    logger.info("Embedding model loaded successfully.")
        return self._model

    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding vector for a query string.

        Uses sentence-transformers MiniLM model (384-dim).
        Wraps CPU-bound encode() in executor to avoid blocking.
        """
        model = await self._get_model()
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None,
            lambda: model.encode(query, normalize_embeddings=True)
        )
        return embedding.tolist()

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        model = await self._get_model()
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: model.encode(texts, normalize_embeddings=True)
        )
        return embeddings.tolist()

    async def retrieve(
        self,
        query: str,
        topic_id: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> List[RetrievedDocument]:
        """
        Retrieve relevant documents from the knowledge base.

        Uses pgvector cosine distance operator <=> for similarity search.
        Similarity = 1 - cosine_distance
        """
        k = top_k or self.top_k
        query_embedding = await self.embed_query(query)

        conditions = ["1 - (embedding <=> CAST(:embedding AS vector)) > :threshold"]
        params = {
            "embedding": query_embedding,
            "threshold": self.similarity_threshold,
            "top_k": k,
        }

        if topic_id:
            conditions.append("topic_id = :topic_id")
            params["topic_id"] = topic_id

        where_clause = " AND ".join(conditions)
        stmt = text(f"""
            SELECT id, content, metadata, topic_id, source_file,
                   1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
            FROM knowledge_documents
            WHERE {where_clause}
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :top_k
        """)

        async with _get_async_session()() as session:
            result = await session.execute(stmt, params)
            rows = result.fetchall()

        docs = []
        for row in rows:
            docs.append(RetrievedDocument(
                id=str(row.id),
                content=row.content,
                metadata=dict(row.meta) if row.meta else {},
                similarity_score=round(float(row.similarity), 4),
            ))

        logger.info(f"Retrieved {len(docs)} documents for query (threshold: {self.similarity_threshold})")
        return docs

    async def retrieve_context(
        self,
        query: str,
        topic_id: Optional[str] = None,
        max_tokens: int = 3000,
    ) -> str:
        """
        Retrieve and format context for LLM prompt injection.

        Returns concatenated document contents formatted as context.
        """
        docs = await self.retrieve(query, topic_id)

        if not docs:
            return ""

        context_parts = []
        for i, doc in enumerate(docs):
            context_parts.append(
                f"[参考材料 {i+1}] (相关度: {doc.similarity_score:.2f})\n"
                f"来源: {doc.metadata.get('source_file', 'Unknown')}\n"
                f"{doc.content}"
            )

        context = "\n---\n".join(context_parts)

        # Truncate to approximate token limit (4 chars ≈ 1 token for Chinese)
        if len(context) > max_tokens * 4:
            context = context[:max_tokens * 4] + "\n\n[上下文已截断，超出长度限制...]"

        return context

    async def index_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        doc_id: Optional[str] = None,
    ):
        """Index a single document into the knowledge base."""
        import uuid
        embedding = await self.embed_query(content)

        stmt = text("""
            INSERT INTO knowledge_documents (id, topic_id, content, chunk_index, source_file, content_type, metadata, embedding)
            VALUES (:id, :topic_id, :content, :chunk_index, :source_file, :content_type, :metadata, :embedding)
        """)

        async with _get_async_session()() as session:
            await session.execute(stmt, {
                "id": doc_id or str(uuid.uuid4()),
                "topic_id": metadata.get("topic_id"),
                "content": content,
                "chunk_index": metadata.get("chunk_index", 0),
                "source_file": metadata.get("source_file", "unknown"),
                "content_type": metadata.get("content_type", "text"),
                "metadata": metadata,
                "embedding": embedding,
            })
            await session.commit()

        logger.info(f"Indexed document: {metadata.get('topic_id', 'unknown')} [{metadata.get('source_file', '?')}]")

    async def index_batch(self, documents: List[Dict[str, Any]]):
        """Batch-index documents with shared embeddings."""
        import uuid

        texts = [doc["content"] for doc in documents]
        embeddings = await self.embed_batch(texts)

        stmt = text("""
            INSERT INTO knowledge_documents (id, topic_id, content, chunk_index, source_file, content_type, metadata, embedding)
            VALUES (:id, :topic_id, :content, :chunk_index, :source_file, :content_type, :metadata, :embedding)
        """)

        async with _get_async_session()() as session:
            for doc, emb in zip(documents, embeddings):
                await session.execute(stmt, {
                    "id": str(uuid.uuid4()),
                    "topic_id": doc.get("topic_id"),
                    "content": doc["content"],
                    "chunk_index": doc.get("chunk_index", 0),
                    "source_file": doc.get("source_file", "unknown"),
                    "content_type": doc.get("content_type", "text"),
                    "metadata": doc.get("metadata", {}),
                    "embedding": emb,
                })
            await session.commit()

        logger.info(f"Batch-indexed {len(documents)} documents")

    async def delete_document(self, doc_id: str):
        """Remove a document from the knowledge base."""
        async with _get_async_session()() as session:
            await session.execute(
                text("DELETE FROM knowledge_documents WHERE id = :id"),
                {"id": doc_id}
            )
            await session.commit()
        logger.info(f"Deleted document: {doc_id}")

    async def get_document_count(self) -> int:
        """Get total number of indexed documents."""
        async with _get_async_session()() as session:
            result = await session.execute(
                text("SELECT COUNT(*) FROM knowledge_documents")
            )
            return result.scalar() or 0


# Singleton
_rag_service: Optional[RAGService] = None
_lock = asyncio.Lock()


async def get_rag_service() -> RAGService:
    """Get or create the RAG service singleton (async-safe)."""
    global _rag_service
    if _rag_service is None:
        async with _lock:
            if _rag_service is None:
                _rag_service = RAGService()
    return _rag_service
