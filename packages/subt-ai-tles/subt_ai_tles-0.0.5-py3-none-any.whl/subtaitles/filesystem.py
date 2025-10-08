from __future__ import annotations

import asyncio
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING

from .translate import translate_srt_file

if TYPE_CHECKING:
    from . import Engine
    from .language import Lang
    from .providers import TranslateProtocol


@dataclass
class TranslateTask:
    path: Path
    source: Lang
    target: Lang
    new_path: Path


def find_srt_files(path: str | Path) -> list[Path]:
    path = Path(path)
    result = []
    if path.is_dir():
        result.extend(chain(*[find_srt_files(sub_path) for sub_path in path.iterdir()]))

    if path.is_file() and path.suffix == ".srt":
        result.append(path)

    return result


def is_already_translated(path: str | Path, lang: Lang) -> bool:
    path = Path(path)
    without_suffix = str(path).removesuffix(path.suffix)
    split = without_suffix.rsplit(".", 1)
    if len(split) == 2:  # noqa: PLR2004
        maybe_lang_identifier = split[1]
        if maybe_lang_identifier in [*lang.language.aliases, lang.language.iso]:
            return True

    return False


def get_new_language_file_path(path: str | Path, lang_from: Lang, lang_to: Lang) -> Path:
    path = Path(path)
    without_suffix = str(path.name).removesuffix(path.suffix)
    split = without_suffix.rsplit(".", 1)
    if len(split) == 2:  # noqa: PLR2004
        maybe_lang_identifier = split[1]
        if maybe_lang_identifier in [*lang_from.language.aliases, lang_from.language.iso]:
            return path.parent / f"{split[0]}.{lang_to.language.iso}{path.suffix}"

    return path.parent / f"{without_suffix}.{lang_to.language.iso}{path.suffix}"


def get_translate_tasks(
    path: Path | str,
    source: Lang,
    target: Lang,
) -> list[TranslateTask]:
    path_to_dir = Path(path)
    if not path_to_dir.is_dir():
        msg = "Supplied path is NOT a directory"
        raise FileNotFoundError(msg)

    tasks = [
        TranslateTask(
            path=srt_file,
            source=source,
            target=target,
            new_path=get_new_language_file_path(srt_file, lang_from=source, lang_to=target),
        )
        for srt_file in find_srt_files(path_to_dir)
        if not is_already_translated(srt_file, lang=target)
    ]
    return [task for task in tasks if not task.new_path.is_file()]


async def run_translate_tasks(
    *tasks: TranslateTask, translator: Engine | TranslateProtocol
) -> list[Path]:
    translate_tasks = [
        translate_srt_file(
            **task.__dict__,
            translator=translator,
        )
        for task in tasks
    ]

    return await asyncio.gather(*translate_tasks, return_exceptions=True)


async def translate_directory(
    path: Path | str,
    source: Lang,
    target: Lang,
    translator: Engine | TranslateProtocol,
) -> list[Path]:
    path_to_dir = Path(path)
    if not path_to_dir.is_dir():
        msg = "Supplied path is NOT a directory"
        raise FileNotFoundError(msg)

    return await run_translate_tasks(
        *get_translate_tasks(path, source, target), translator=translator
    )
