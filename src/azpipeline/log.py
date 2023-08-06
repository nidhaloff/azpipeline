__copyright__ = """
@copyright (c) 2023 by Nidhal Baccouri. All rights reserved.
"""

import logging


def logger(name: str) -> logging.Logger:
    logger = logging.Logger(name=name)
    return logger
