def is_interactive_maya():
    """
    Checks if maya is running in interactive mode
    """
    import maya.cmds as cmds

    try:
        return not cmds.about(batch=True)  # noqa
    except (AttributeError, ImportError):
        return False
