"""
Textbook ingestion script.

Reads DSA textbook markdown files, chunks them, generates embeddings,
and indexes into the pgvector knowledge_documents table.
"""

import os
import re
import asyncio
from pathlib import Path

from app.services.rag_service import get_rag_service

TEXTBOOK_DIR = Path(__file__).parent.parent / "knowledge_graph" / "textbook"

# Map of filename prefix to topic_id(s)
FILE_TOPIC_MAP = {
    "01": "complexity_analysis",
    "02": "arrays",           # also linked_lists
    "03": "stacks",           # also queues
    "04": "strings",
    "05": "trees_basic",
    "06": "bst",              # also avl_trees, red_black_trees
    "07": "heap",             # also trie
    "08": "graphs_basic",     # also graph_traversal
    "09": "shortest_path",    # also mst
    "10": "advanced_sorting", # also basic_sorting, non_comparison_sorting, searching
    "11": "hashing",
    "12": "dynamic_programming",  # also recursion, divide_conquer, greedy, backtracking
}

# Expanded topic mapping for files covering multiple topics
MULTI_TOPIC_FILES = {
    "02": ["arrays", "linked_lists"],
    "03": ["stacks", "queues"],
    "06": ["bst", "avl_trees", "red_black_trees"],
    "07": ["heap", "trie"],
    "08": ["graphs_basic", "graph_traversal"],
    "09": ["shortest_path", "mst"],
    "10": ["basic_sorting", "advanced_sorting", "non_comparison_sorting", "searching"],
    "12": ["recursion", "divide_conquer", "dynamic_programming", "greedy", "backtracking"],
}


def chunk_markdown(text: str, chunk_size: int = 800, overlap: int = 100) -> list:
    """
    Split markdown text into overlapping chunks.

    Strategy: Split by ## section headers first, then sub-split
    sections that are too long.
    """
    # Split by ## headers
    sections = re.split(r'\n(?=## )', text)

    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract section title for metadata
        title_match = re.match(r'^## (.*)', section)
        section_title = title_match.group(1) if title_match else ""

        # Detect content type
        if re.search(r'```(python|java|cpp)', section):
            content_type = "code"
        elif re.search(r'\$\$.*\$\$|\$.*\$', section):
            content_type = "formula"
        elif section_title and any(kw in section_title for kw in ["定义", "概念", "性质"]):
            content_type = "definition"
        else:
            content_type = "text"

        # If section is short enough, keep as one chunk
        if len(section) <= chunk_size:
            chunks.append({
                "content": section,
                "section": section_title,
                "content_type": content_type,
            })
        else:
            # Sub-split long sections with overlap
            paragraphs = section.split("\n\n")
            current = ""
            for para in paragraphs:
                if len(current) + len(para) <= chunk_size:
                    current += ("\n\n" + para) if current else para
                else:
                    if current:
                        chunks.append({
                            "content": current,
                            "section": section_title,
                            "content_type": content_type,
                        })
                    current = para
            if current:
                chunks.append({
                    "content": current,
                    "section": section_title,
                    "content_type": content_type,
                })

    return chunks


async def ingest_file(filepath: Path) -> int:
    """Ingest a single textbook markdown file."""
    rag = await get_rag_service()

    with open(filepath, "r") as f:
        text = f.read()

    # Determine primary topic from filename
    filename = filepath.stem
    prefix = filename[:2]
    primary_topic = FILE_TOPIC_MAP.get(prefix, "dsa_intro")
    multi_topics = MULTI_TOPIC_FILES.get(prefix, [primary_topic])

    chunks = chunk_markdown(text)

    documents = []
    for i, chunk in enumerate(chunks):
        # Assign topic — first chunk gets primary, distribute rest
        topic_idx = i % len(multi_topics)
        topic_id = multi_topics[topic_idx]

        documents.append({
            "content": chunk["content"],
            "topic_id": topic_id,
            "chunk_index": i,
            "source_file": filepath.name,
            "content_type": chunk["content_type"],
            "metadata": {
                "section": chunk["section"],
                "source_file": filepath.name,
                "content_type": chunk["content_type"],
            },
        })

    # Batch index
    await rag.index_batch(documents)
    return len(documents)


async def ingest_all():
    """Ingest all textbook files."""
    rag = await get_rag_service()

    # Clear existing documents
    from app.models.base import async_session
    from sqlalchemy import text
    async with async_session() as session:
        await session.execute(text("DELETE FROM knowledge_documents"))
        await session.commit()
    print("[ingest] Cleared existing documents.")

    total_chunks = 0
    md_files = sorted(TEXTBOOK_DIR.glob("*.md"))

    for filepath in md_files:
        count = await ingest_file(filepath)
        total_chunks += count
        print(f"[ingest] {filepath.name}: {count} chunks indexed.")

    # Verify
    doc_count = await rag.get_document_count()
    print(f"[ingest] Total documents indexed: {doc_count}")
    print(f"[ingest] Ingestion complete.")


if __name__ == "__main__":
    asyncio.run(ingest_all())
