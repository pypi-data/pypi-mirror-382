import asyncio
import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

from subtaitles import Engine, Lang
from subtaitles.filesystem import translate_directory
from subtaitles.translate import translate_srt_file


def main() -> None:
    logging.basicConfig()
    logging.getLogger(__package__).setLevel(level=logging.INFO)

    parser = ArgumentParser()
    parser.add_argument(
        "input",
        metavar="INPUT_PATH",
        type=Path,
        help="Path to a .srt file to be translated",
    )
    parser.add_argument(
        "output",
        metavar="OUTPUT_PATH",
        type=Path,
        default=None,
        help="Path to where the resulting file will be stored",
    )
    parser.add_argument(
        "lang_from",
        metavar="LANGUAGE_FROM",
        type=Lang,
        help="Language to be translated from",
    )
    parser.add_argument(
        "lang_to", metavar="LANGUAGE_TO", type=Lang, help="Language to be translated to"
    )
    parser.add_argument("--dir", action="store_true")
    parser.add_argument(
        "--engine",
        type=Engine,
        help="Translation engine to be used",
        default=Engine.OPEN_AI,
    )

    args = parser.parse_args()
    if args.dir:
        asyncio.run(translate_directory(args.input, args.lang_from, args.lang_to, args.engine))
        sys.exit(0)

    try:
        asyncio.run(
            translate_srt_file(
                path=args.input,
                source=args.lang_from,
                target=args.lang_to,
                translator=args.engine,
                new_path=args.output,
            )
        )
    except Exception as exc:  # noqa: BLE001
        print(f"\033[31mFailed to translate subtitles: {exc}\033[0m")  # noqa: T201
        sys.exit(1)


if __name__ == "__main__":
    main()
