from .. import log
from .interactive_utils import SuppressScriptEditorOutput

# note this logger is defined before SilenceMayaContextManager is added so will not
# silence script editor output
logger = log.get_logger(__name__)
# logger.setLevel("DEBUG")


class SilenceMayaContextManager(
    SuppressScriptEditorOutput, log.LogAllLevelsContextManager
):
    pass


def initialize_maya():
    log.SilenceContextManager = SilenceMayaContextManager
    logger.debug("Initializing interactive maya...")
