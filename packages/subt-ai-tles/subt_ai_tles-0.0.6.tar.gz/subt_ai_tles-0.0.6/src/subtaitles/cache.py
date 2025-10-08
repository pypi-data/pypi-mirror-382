from typing import Protocol, TypeVar

from diskcache import Cache

from .environment import env
from .language import Lang

disk_cache = Cache(env.CACHE_DIR.value)


T = TypeVar("T")


def get_cache_key(text: str, lang_from: Lang, lang_to: Lang) -> str:
    return f"{text}-{lang_from}-{lang_to}"


class CacheProtocol(Protocol[T]):
    def get(self, key: str) -> T: ...

    def __setattr__(self, key: str, value: T) -> None: ...
