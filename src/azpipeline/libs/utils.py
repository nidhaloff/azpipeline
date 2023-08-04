
import json
from pathlib import Path
from typing import Union

def write_json(f: Union[str, Path], obj: dict):
    with Path(f).open() as file:
        json.dump(obj)
        