try:
    from itertools import batched
except ImportError:
    from collections.abc import Generator, Iterable
    from itertools import islice
    from typing import Any

    def batched(iterable: Iterable, n: int) -> Generator[tuple[Any, ...], Any]:
        # batched('ABCDEFG', 3) --> ABC DEF G
        if n < 1:
            msg = "n must be at least one"
            raise ValueError(msg)
        it = iter(iterable)
        while batch := tuple(islice(it, n)):
            yield batch
