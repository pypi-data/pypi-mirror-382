import maya_brew
import maya_brew.scene
import pytest


def test_new_scene():
    cube, history = maya_brew.cmds.polyCube()
    with pytest.raises(maya_brew.scene.UnsavedChanges):
        maya_brew.scene.new_file(force=False)
    maya_brew.scene.new_file(force=True)
    assert maya_brew.cmds.objExists(cube) is False


def test_UnsavedChanges_is_RuntimeError():
    try:
        raise maya_brew.scene.UnsavedChanges("some test error")
    except RuntimeError as e:
        assert isinstance(e, maya_brew.scene.UnsavedChanges)
