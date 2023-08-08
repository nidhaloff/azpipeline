__copyright__ = """
@copyright (c) 2023 by Nidhal Baccouri. All rights reserved.
"""

from pathlib import Path


class Config:
    cwd = Path.cwd()
    ADO_LOGS_DIR = cwd / "logs"
