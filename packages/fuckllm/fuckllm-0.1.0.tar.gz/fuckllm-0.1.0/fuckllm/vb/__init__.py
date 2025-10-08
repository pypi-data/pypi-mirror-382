"""Vector database implementations for fuckllm package."""

from ._vb_json import JsonVectorDB

# ChromaVectorDB requires chromadb
try:
    from ._vb_chroma import ChromaVectorDB
    _has_chromadb = True
except ImportError as e:
    import warnings
    warnings.warn(
        f"ChromaVectorDB not available: {e}. "
        "Install 'chromadb' for ChromaDB support: pip install chromadb",
        ImportWarning
    )
    ChromaVectorDB = None
    _has_chromadb = False

__all__ = [
    "JsonVectorDB",
]

# Add ChromaVectorDB to exports if available
if _has_chromadb:
    __all__.append("ChromaVectorDB")