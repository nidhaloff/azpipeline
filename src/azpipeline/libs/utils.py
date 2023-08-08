__copyright__ = """
@copyright (c) 2023 by Nidhal Baccouri. All rights reserved.
"""
import json
from pathlib import Path
from typing import Union


def write_json(output_path: Union[str, Path], obj: dict) -> None:
    with Path(output_path).open() as file:
        json.dump(obj, file)
