from maya_brew.maya_initializer import standalone_init


def test_standalone_can_use_cmds():
    standalone_init.initialize_maya()

    import maya.cmds as cmds

    (cube,) = cmds.polyCube(constructionHistory=False)
    assert isinstance(cube, str)


def test_standalone_not_interactive():
    from maya_brew.maya_initializer.shared import is_interactive_maya

    assert not is_interactive_maya()
