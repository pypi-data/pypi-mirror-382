import maya_brew
import maya_brew.nodes.cast
import pytest


def test_string_to_dag_path(test_cube, test_namespace, test_cube_short_name):
    cube_full_path = maya_brew.cmds.ls(test_cube, long=True)[0]
    assert cube_full_path == f"|{test_namespace}:{test_cube_short_name}"
    dag_path = maya_brew.nodes.cast.get_dag_path_from_string(cube_full_path)
    assert isinstance(dag_path, maya_brew.OpenMaya2.MDagPath)


def test_invalid_string_to_dag_path(test_cube, test_cube_short_name):
    with pytest.raises(maya_brew.nodes.cast.NonExistingDagPath):
        maya_brew.nodes.cast.get_dag_path_from_string("invalid_name")
    with pytest.raises(maya_brew.nodes.cast.NonExistingDagPath):
        maya_brew.nodes.cast.get_dag_path_from_string(test_cube_short_name)
    with pytest.raises(maya_brew.nodes.cast.InvalidDagPath):
        maya_brew.nodes.cast.get_dag_path_from_string("lambert1")


def test_get_long_name_from_maya_string(
    test_cube, test_namespace, test_cube_short_name
):
    cube_full_name = f"{test_namespace}:{test_cube_short_name}"
    cube_full_path = maya_brew.nodes.cast.get_long_name_from_maya_string(cube_full_name)
    assert cube_full_path == f"|{cube_full_name}"
    grouped_cube = maya_brew.cmds.polyCube(name=test_cube_short_name)[0]
    group_name = "my_group"
    maya_brew.cmds.group(name=group_name, empty=True)
    maya_brew.cmds.parent(grouped_cube, group_name)
    grouped_cube_full_path = maya_brew.nodes.cast.get_long_name_from_maya_string(
        grouped_cube
    )
    assert group_name in grouped_cube_full_path
    new_cube_with_same_short_name = maya_brew.cmds.polyCube(name=test_cube_short_name)[
        0
    ]
    # we can cast it from maya's return value
    new_cube_full_path = maya_brew.nodes.cast.get_long_name_from_maya_string(
        new_cube_with_same_short_name
    )
    # if we try to cast it based on short name we should get two matches
    with pytest.raises(maya_brew.nodes.cast.MultipleMatchingNodes):
        maya_brew.nodes.cast.get_long_name_from_maya_string(test_cube_short_name)
    assert test_namespace not in new_cube_full_path
    with pytest.raises(maya_brew.nodes.cast.NoMatchingNodes):
        maya_brew.nodes.cast.get_long_name_from_maya_string("invalid_name")
