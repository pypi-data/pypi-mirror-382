from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable


class BaseLoader(ABC):
    @abstractmethod
    def load(
        self,
        path: Path,
        *,
        project_root_callback: Callable[[], Path | str] | None = None,
    ) -> Any:
        raise NotImplementedError
