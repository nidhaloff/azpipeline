__copyright__ = """
@copyright (c) 2023 by Nidhal Baccouri. All rights reserved.
"""
import json
from pathlib import Path
from typing import Union


def write_json(f: Union[str, Path], obj: dict) -> None:
    with Path(f).open() as file:
        json.dump(obj, file)
