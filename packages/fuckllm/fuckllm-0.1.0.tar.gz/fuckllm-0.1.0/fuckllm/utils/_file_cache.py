import hashlib
from itertools import accumulate
import json
import os
import numpy as np


class FileCache:
    def __init__(
        self,
        cache_dir: str = "./cache",
        max_size: int | None = None,
        max_num: int | None = None,
    ) -> None:
        self.cache_dir = cache_dir
        self.max_size = max_size
        self.max_num = max_num
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_file_name(self, identifier: dict | object) -> str:
        json_str = json.dumps(identifier, ensure_ascii=False, indent=2)
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest() + ".npy"

    def _get_file_path(self, file_name: str) -> str:
        return os.path.join(self.cache_dir, file_name)

    async def store(
        self,
        embeddings: list[list[float]],
        identifier: dict | object,
        overwrite: bool = False,
    ) -> str:
        file_path = self._get_file_path(self._get_file_name(identifier))
        if os.path.exists(file_path):
            if not os.path.isfile(file_path):
                raise ValueError(f"Cache path {file_path} exists but is not a file")
            if overwrite:
                np.save(file_path, embeddings)
                await self._rebuild()
        else:
            np.save(file_path, embeddings)
            await self._rebuild()

    async def retrieve(
        self,
        identifier: dict | object,
    ) -> np.ndarray | None:
        file_path = self._get_file_path(self._get_file_name(identifier))
        if os.path.exists(file_path):
            try:
                data = np.load(file_path, allow_pickle=True)
                return data
            except Exception as e:
                print(f"Warning: Could not load cache file {file_path}: {e}")
                return None
        return None

    async def delete(
        self,
        identifier: dict | object,
    ) -> None:
        file_path = self._get_file_path(self._get_file_name(identifier))
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise ValueError(f"Cache file {file_path} does not exist")

    async def clear(self) -> bool:
        for _, _, files in os.walk(self.cache_dir):
            for file in files:
                file_path = os.path.join(self.cache_dir, file)
                if file_path.endswith(".npy") and os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except (PermissionError, OSError) as e:
                        print(f"Warning: Could not delete cache file {file_path}: {e}")
                        continue

    async def _rebuild(self):
        try:
            files = [
                (_.name, _.stat().st_size, _.stat().st_mtime)
                for _ in os.scandir(self.cache_dir)
                if _.is_file() and _.name.endswith(".npy")
            ]
        except (PermissionError, OSError) as e:
            print(f"Warning: Could not scan cache directory {self.cache_dir}: {e}")
            return False

        files.sort(key=lambda x: x[2])
        if self.max_num and len(files) > self.max_num:
            for file in files[: -self.max_num]:
                try:
                    os.remove(os.path.join(self.cache_dir, file[0]))
                except (PermissionError, OSError) as e:
                    print(f"Warning: Could not delete cache file {file[0]}: {e}")
                    continue
            files = files[-self.max_num :]
        file_size_sum = accumulate([_[1] for _ in files], initial=0)
        if self.max_size and file_size_sum[-1] > self.max_size:
            for file in files:
                if file_size_sum[-1] - file[1] < self.max_size:
                    break
                try:
                    os.remove(os.path.join(self.cache_dir, file[0]))
                except (PermissionError, OSError) as e:
                    print(f"Warning: Could not delete cache file {file[0]}: {e}")
                    continue
            files = files[files.index(file) :]
        return True
