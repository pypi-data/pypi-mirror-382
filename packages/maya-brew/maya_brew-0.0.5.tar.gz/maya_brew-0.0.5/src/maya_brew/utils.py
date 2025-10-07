import importlib
import sys
from pathlib import Path

from .log import get_logger

logger = get_logger(__name__)
logger.setLevel("DEBUG")


def reload_mb():
    """
    Workaround to reload entire maya-brew library.
    Removes all maya-brew modules from 'sys.modules' and imports it again
    """

    import maya_brew

    mb_path = Path(maya_brew.__file__)
    mb_modules = list()
    for m in [p for p in sys.modules if p.startswith(mb_path.parent.name)]:
        mb_modules.append(m)
        sys.modules.pop(m)
    for m in mb_modules:
        logger.debug(f"re-importing {m}")
        importlib.import_module(m)
