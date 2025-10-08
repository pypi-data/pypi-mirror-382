import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import os


class JsonVectorDB:
    def __init__(self, dimension: int = None):
        self.dimension = dimension
        self.vectors = []
        self.metadata = []
        self.ids = []
        self.vector_index = 0

    def add_vector(
        self,
        vector: List[float],
        metadata: Dict[str, Any] = None,
        vector_id: str = None,
    ) -> str:
        vector_array = np.array(vector, dtype=np.float32)

        if self.dimension is None:
            self.dimension = len(vector)
        elif len(vector) != self.dimension:
            raise ValueError(
                f"Vector dimension mismatch, expected {self.dimension}, got {len(vector)}"
            )

        if vector_id is None:
            vector_id = f"vec_{self.vector_index}"
        self.vector_index += 1

        self.vectors.append(vector_array)
        self.metadata.append(metadata or {})
        self.ids.append(vector_id)

        return vector_id

    def search(
        self, query_vector: List[float], k: int = 5, metric: str = "cosine"
    ) -> List[Tuple[str, float, Dict]]:
        if not self.vectors:
            return []

        query_array = np.array(query_vector, dtype=np.float32)

        if len(query_array) != self.dimension:
            raise ValueError(
                f"Vector dimension mismatch, expected {self.dimension}, got {len(query_array)}"
            )

        similarities = []

        for i, vector in enumerate(self.vectors):
            if metric == "cosine":
                dot_product = np.dot(query_array, vector)
                norm_query = np.linalg.norm(query_array)
                norm_vector = np.linalg.norm(vector)
                if norm_query == 0 or norm_vector == 0:
                    similarity = 0.0
                else:
                    similarity = dot_product / (norm_query * norm_vector)
            elif metric == "euclidean":
                distance = np.linalg.norm(query_array - vector)
                similarity = 1.0 / (1.0 + distance)
            else:
                raise ValueError(f"Unsupported metric: {metric}")

            similarities.append((self.ids[i], similarity, self.metadata[i]))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

    def get_vector(self, vector_id: str) -> Optional[Tuple[List[float], Dict]]:

        try:
            index = self.ids.index(vector_id)
            vector = self.vectors[index].tolist()
            metadata = self.metadata[index]
            return vector, metadata
        except ValueError:
            return None

    def delete_vector(self, vector_id: str) -> bool:

        try:
            index = self.ids.index(vector_id)
            del self.vectors[index]
            del self.metadata[index]
            del self.ids[index]
            return True
        except ValueError:
            return False

    def save(self, filepath: str) -> None:

        data = {
            "dimension": self.dimension,
            "vector_index": self.vector_index,
            "vectors": [vector.tolist() for vector in self.vectors],
            "metadata": self.metadata,
            "ids": self.ids,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "JsonVectorDB":

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        db = cls(dimension=data["dimension"])
        db.vector_index = data["vector_index"]

        db.vectors = [np.array(vector, dtype=np.float32) for vector in data["vectors"]]
        db.metadata = data["metadata"]
        db.ids = data["ids"]

        return db

    def __len__(self) -> int:
        return len(self.vectors)

    def __str__(self) -> str:
        return f"VectorDB(dimension={self.dimension}, size={len(self)})"
