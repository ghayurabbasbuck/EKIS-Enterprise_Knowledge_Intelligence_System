import asyncio
import os

from langchain_huggingface import HuggingFaceEmbeddings

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

HF_TOKEN = os.getenv("HF_TOKEN")

model_kwargs = {
    "device": "cpu",
}

if HF_TOKEN:
    model_kwargs["token"] = HF_TOKEN

embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs=model_kwargs,
    encode_kwargs={
        "normalize_embeddings": True,
    },
)


async def generate_embedding(text: str) -> list[float]:
    """Generate an embedding for a single text."""

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    return await asyncio.to_thread(
        embedding_model.embed_query,
        text,
    )


async def generate_embeddings(
    texts: list[str],
) -> list[list[float]]:
    """Generate embeddings for multiple texts."""

    cleaned_texts = [
        text.strip()
        for text in texts
        if text and text.strip()
    ]

    if not cleaned_texts:
        return []

    return await asyncio.to_thread(
        embedding_model.embed_documents,
        cleaned_texts,
    )