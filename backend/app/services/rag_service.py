"""
RAG (Retrieval-Augmented Generation) Service for DSA Learning System.

Uses pgvector for vector similarity search to retrieve relevant
DSA textbook content for grounding LLM generation.
"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from app.config import get_settings

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
    1. Embed query using embedding model
    2. Vector similarity search in pgvector
    3. Filter by similarity threshold
    4. Return top-k relevant documents
    5. Format for LLM context injection
    """

    def __init__(
        self,
        similarity_threshold: Optional[float] = None,
        top_k: int = 5,
    ):
        self.similarity_threshold = similarity_threshold or settings.RAG_SIMILARITY_THRESHOLD
        self.top_k = top_k
        self.vector_dimension = settings.VECTOR_DIMENSION

    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding vector for a query string.

        Uses text2vec-large-chinese or Spark Embedding API.
        Returns a vector of VECTOR_DIMENSION dimensions.
        """
        # TODO: Implement actual embedding generation
        # Option 1: text2vec-large-chinese (local, free)
        #   from text2vec import SentenceModel
        #   model = SentenceModel("shibing624/text2vec-base-chinese")
        #   return model.encode(query).tolist()
        #
        # Option 2: iFlytek Spark Embedding API
        #   Use SparkClient to call embedding endpoint
        logger.info(f"Embedding query: {query[:100]}...")
        # Placeholder: return zero vector
        return [0.0] * self.vector_dimension

    async def retrieve(
        self,
        query: str,
        topic_id: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> List[RetrievedDocument]:
        """
        Retrieve relevant documents from the knowledge base.

        Args:
            query: Search query text
            topic_id: Optional filter by DSA topic
            top_k: Number of documents to retrieve
        """
        k = top_k or self.top_k
        query_embedding = await self.embed_query(query)

        # TODO: Implement pgvector similarity search
        # SELECT id, content, metadata,
        #        1 - (embedding <=> query_embedding) AS similarity
        # FROM knowledge_documents
        # WHERE 1 - (embedding <=> query_embedding) > :threshold
        #   AND (:topic_id IS NULL OR metadata->>'topic_id' = :topic_id)
        # ORDER BY embedding <=> query_embedding
        # LIMIT :top_k

        logger.info(f"Retrieving top {k} documents for query (threshold: {self.similarity_threshold})")

        # Placeholder: return empty results
        return []

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
                f"[Document {i+1}] (relevance: {doc.similarity_score:.2f})\n"
                f"Source: {doc.metadata.get('source', 'Unknown')}\n"
                f"{doc.content}\n"
            )

        context = "\n---\n".join(context_parts)

        # Truncate to approximate token limit
        if len(context) > max_tokens * 4:  # rough char/token ratio
            context = context[:max_tokens * 4] + "\n[Context truncated...]"

        return context

    async def index_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        doc_id: Optional[str] = None,
    ):
        """
        Index a new document into the knowledge base.

        Args:
            content: Document text content
            metadata: Additional metadata (topic_id, source, type, etc.)
            doc_id: Optional document ID (generated if not provided)
        """
        embedding = await self.embed_query(content)

        # TODO: Insert into pgvector
        # INSERT INTO knowledge_documents (id, content, metadata, embedding)
        # VALUES (:id, :content, :metadata, :embedding)

        logger.info(f"Indexed document: {metadata.get('topic_id', 'unknown')}")

    async def delete_document(self, doc_id: str):
        """Remove a document from the knowledge base."""
        # TODO: DELETE FROM knowledge_documents WHERE id = :doc_id
        logger.info(f"Deleted document: {doc_id}")

    async def get_document_count(self) -> int:
        """Get total number of indexed documents."""
        # TODO: SELECT COUNT(*) FROM knowledge_documents
        return 0


# Singleton
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create the RAG service singleton."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
