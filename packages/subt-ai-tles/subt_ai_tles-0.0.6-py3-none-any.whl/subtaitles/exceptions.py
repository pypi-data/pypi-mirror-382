from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class FailedToTranslateError(Exception):
    def __init__(self, input_path: str | Path, output_path: str | Path, *args: any) -> None:
        self.input_path = input_path
        self.output_path = output_path
        super().__init__(*args)
