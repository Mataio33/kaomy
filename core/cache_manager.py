import json
from pathlib import Path
from typing import Optional

from kaomy.core.constants import CACHE_DIR
from kaomy.core.exceptions import CacheError
from kaomy.models.resource_state import ResourceState


class CacheManager:
    """
    Manage persistent cache files for Kaomy collectors.

    The cache stores the last valid ResourceState so collectors can restore
    Home Assistant sensors after a restart without contacting providers.
    """

    def __init__(self, cache_name: str):
        self.cache_name = cache_name
        self.cache_path = self._build_cache_path(cache_name)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

    def exists(self) -> bool:
        return self.cache_path.exists()

    def load(self) -> Optional[ResourceState]:
        if not self.exists():
            return None

        try:
            with self.cache_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            return ResourceState.from_dict(data)

        except Exception as exc:
            raise CacheError(f"Unable to load cache file {self.cache_path}: {exc}") from exc

    def save(self, state: ResourceState) -> None:
        try:
            with self.cache_path.open("w", encoding="utf-8") as file:
                json.dump(
                    state.to_dict(),
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as exc:
            raise CacheError(f"Unable to save cache file {self.cache_path}: {exc}") from exc

    def delete(self) -> None:
        try:
            if self.exists():
                self.cache_path.unlink()

        except Exception as exc:
            raise CacheError(f"Unable to delete cache file {self.cache_path}: {exc}") from exc

    @staticmethod
    def _build_cache_path(cache_name: str) -> Path:
        if cache_name.endswith(".json"):
            filename = cache_name
        else:
            filename = f"{cache_name}.json"

        return CACHE_DIR / filename
