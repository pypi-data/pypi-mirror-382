import logging

import maya_brew.nodes.cast
import maya_brew.nodes.node_types
import pytest
from maya_brew.attributes.node_attribute import Attribute
from maya_brew.exceptions import MayaBrewAttributeError


def test_dag_node_string(test_cube, caplog):
    dag_node = maya_brew.nodes.node_types.DagNode(test_cube)
    full_node_path = maya_brew.nodes.cast.get_long_name_from_maya_string(test_cube)
    assert str(dag_node) == full_node_path
    # rename to see warning display correct node path when deleted
    new_name = "new_name"
    dag_node.rename(new_name)
    maya_brew.cmds.delete(str(dag_node))
    with caplog.at_level(logging.WARNING):
        str(dag_node)
        node_path = dag_node.node_path
        assert node_path in str(caplog.text)


def test_dag_node_rename(test_cube, caplog):
    dag_node = maya_brew.nodes.node_types.DagNode(test_cube)
    new_name = "new_name"
    new_resolved_name = dag_node.rename(new_name)
    assert new_resolved_name == new_name
    another_cube = maya_brew.cmds.polyCube(name="another_cube")[0]
    another_dag_node = maya_brew.nodes.node_types.DagNode(another_cube)
    another_cube_new_name = another_dag_node.rename(new_name)
    assert another_cube_new_name != new_name
    assert another_cube_new_name == "new_name1"
    another_dag_node_full_path = f"|{another_cube_new_name}"
    assert str(another_dag_node) == another_dag_node_full_path
    assert another_dag_node.dag_path.fullPathName() == another_dag_node_full_path


def test_Transform_repr():
    name = "hello"
    dag_node = maya_brew.nodes.node_types.Transform.create(name)
    repr = dag_node.__repr__()
    assert name in repr
    assert dag_node.get_full_path() in repr
    assert type(dag_node).__name__ in repr


def test_list_attributes(brew_transform):
    for a in brew_transform.list_attributes():
        assert isinstance(a, Attribute)


def test_node_at_returns_attribute(brew_transform):
    attr = brew_transform.at.visibility
    from maya_brew.attributes.node_attribute import Attribute

    assert isinstance(attr, Attribute)
    assert "visibility" in str(attr)
    assert brew_transform.node_path in str(attr)


def test_node_at_invalid_attribute_raises(brew_transform):
    with pytest.raises(MayaBrewAttributeError):
        _ = brew_transform.at.non_existent_attr


def test_node_at_on_dagnode(test_cube):
    from maya_brew.nodes.node_types import DagNode

    dag_node = DagNode(test_cube)
    attr = dag_node.at.visibility
    from maya_brew.attributes.node_attribute import Attribute

    assert isinstance(attr, Attribute)
    assert "visibility" in str(attr)
    assert dag_node.node_path in str(attr)


def test_node_at_on_transform():
    from maya_brew.nodes.node_types import Transform

    name = "test_transform"
    transform = Transform.create(name)
    attr = transform.at.visibility
    from maya_brew.attributes.node_attribute import Attribute

    assert isinstance(attr, Attribute)
    assert "visibility" in str(attr)
    assert transform.node_path in str(attr)
