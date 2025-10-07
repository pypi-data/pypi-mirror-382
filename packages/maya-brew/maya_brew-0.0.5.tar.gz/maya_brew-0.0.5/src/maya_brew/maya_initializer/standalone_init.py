from ..log import get_logger

logger = get_logger(__name__)
# logger.setLevel("DEBUG")


def initialize_maya():
    if cmds_about_exists():
        return
    with logger.silence(["This plugin does not support createPlatformOpenGLContext!"]):
        import maya.standalone

        maya.standalone.initialize(name="initialized_by_maya_brew")
    logger.debug("initialized maya standalone")


def cmds_about_exists():
    try:
        from maya.cmds import about  # noqa: F401

        return True
    except ImportError:
        return False


if __name__ == "__main__":
    initialize_maya()
