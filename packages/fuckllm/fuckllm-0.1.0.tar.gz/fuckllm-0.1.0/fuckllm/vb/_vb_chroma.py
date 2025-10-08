import chromadb
from typing import List, Dict, Any, Optional, Union
from model import Embedder


class ChromaVectorDB:
    def __init__(
        self,
        dimension: int = None,
        embedder: Embedder = None,
        collection_name: str = "memory_collection",
        persist_directory: str = "./chroma_db",
    ):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"dimension": dimension} if dimension else None,
        )
        self.dimension = dimension
        self.embedder = embedder

    async def add_data(
        self, data: Union[str, list[str]], metadata: Dict[str, Any], record_id: str
    ) -> None:
        if isinstance(data, str):
            data = [data]
        embed_response = await self.embedder.embed(data)
        self.collection.add(
            documents=data,
            metadatas=[metadata],
            ids=[record_id],
            embeddings=embed_response.embedding,
        )

    async def query(
        self,
        query: str,
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ):
        embed_response = await self.embedder.embed(query)
        results = self.collection.query(
            query_embeddings=embed_response.embedding, n_results=top_k, where=where
        )
        similarities = []
        for i in range(len(results["ids"][0])):
            similarities.append(
                {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": (
                        results["distances"][0][i] if "distances" in results else None
                    ),
                }
            )
        return similarities

    def get_data_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        try:
            results = self.collection.get(
                ids=[id], include=["documents", "metadatas", "embeddings"]
            )

            if results["ids"]:
                return {
                    "id": results["ids"][0],
                    "document": results["documents"][0],
                    "metadata": results["metadatas"][0],
                    "embedding": results["embeddings"][0],
                }
        except Exception as e:
            return None
        return None

    def delete_data(self, id: str) -> bool:
        try:
            self.collection.delete(ids=[id])
            return True
        except Exception as e:
            return False

    def update_data_metadata(self, id: str, metadata: Dict[str, Any]) -> bool:
        try:
            existing = self.collection.get(
                ids=[id], include=["embeddings", "documents"]
            )

            if existing["ids"]:
                self.collection.update(
                    ids=[id],
                    metadatas=[metadata],
                    embeddings=[existing["embeddings"][0]],
                    documents=[existing["documents"][0]],
                )
                return True
        except Exception as e:
            return False
        return False

    def count_data(self) -> int:
        return self.collection.count()

    def clear_all_data(self) -> bool:
        try:
            self.collection.delete(where={})
            return True
        except Exception as e:
            return False


if __name__ == "__main__":
    import asyncio
    import os

    api_key = os.getenv("siliconflow_api_key")
    base_url = "https://api.siliconflow.cn/v1"
    # "Qwen/Qwen3-Coder-480B-A35B-Instruct"
    model = "ByteDance-Seed/Seed-OSS-36B-Instruct"
    embed_model = "Qwen/Qwen3-Embedding-8B"
    chater_cfg = {
        "client_cfg": {
            "api_key": api_key,
            "base_url": base_url,
        },
        "chat_cfg": {
            "stream": True,
            "model": model,
            "max_tokens": 1024,
        },
        "embed_cfg": {
            "model": embed_model,
        },
    }

    async def run():
        db = ChromaVectorDB(dimension=1536, embedder=Embedder(chater_cfg))
        await db.add_data("Hello, how are you?", {"name": "John"}, "1")
        print(await db.query("Hello, how are you?"))

    asyncio.run(run())
