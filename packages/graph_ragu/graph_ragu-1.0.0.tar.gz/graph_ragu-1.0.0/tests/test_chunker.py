import pytest
from ragu.chunker.types import Chunk
from ragu.utils.ragu_utils import compute_mdhash_id

from ragu.chunker.chunkers import SimpleChunker
from ragu.chunker.chunkers import SemanticTextChunker
from ragu.chunker.chunkers import SmartSemanticChunker


@pytest.fixture
def sample_docs():
    return [
        "Первый документ. Состоит из двух предложений.",
        "Второй документ. Он немного длиннее, чем первый, и содержит три предложения. Последнее завершает текст."
    ]


@pytest.mark.parametrize("chunker_class, init_kwargs", [
    (SimpleChunker, dict(max_chunk_size=50, overlap=5)),
    (SemanticTextChunker, dict(model_name="all-MiniLM-L6-v2", max_chunk_size=50, device="cpu")),
    (SmartSemanticChunker, dict(max_chunk_length=50, device="cpu")),
])
def test_chunker_interface(chunker_class, init_kwargs, sample_docs):
    """
    Tests that all chunkers return List[Chunk] with correct structure,
    per-document numbering, and valid doc_ids.
    """
    chunker = chunker_class(**init_kwargs)
    chunks = chunker.split(sample_docs)

    # 1. Check type and structure
    assert isinstance(chunks, list), "Chunker must return a list."
    assert all(isinstance(c, Chunk) for c in chunks), "Each element must be a Chunk."

    # 2. Group chunks by doc_id
    from collections import defaultdict
    groups = defaultdict(list)
    for c in chunks:
        groups[c.doc_id].append(c)

    # Ensure doc_ids correspond to input docs
    expected_doc_ids = [compute_mdhash_id(doc) for doc in sample_docs]
    assert set(groups.keys()) == set(expected_doc_ids), "Each doc_id must match document hash."

    # 3. Per-document ordering check
    for doc_id, doc_chunks in groups.items():
        indices = [c.chunk_order_idx for c in doc_chunks]
        assert indices == list(range(len(doc_chunks))), f"Indices must start at 0 for doc_id={doc_id}."

    # 4. Content sanity check
    for c in chunks:
        assert isinstance(c.content, str) and len(c.content.strip()) > 0, "Chunk content must be non-empty string."
