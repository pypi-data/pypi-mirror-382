from pathlib import Path
from textwrap import dedent

import black
from black.mode import Mode


def write_code(path: str | Path, *lines: str):
    raw_code = "\n".join(dedent(line) for line in lines)
    formatted_code = black.format_str(raw_code, mode=Mode())
    Path(path).write_text(formatted_code, "utf-8")
