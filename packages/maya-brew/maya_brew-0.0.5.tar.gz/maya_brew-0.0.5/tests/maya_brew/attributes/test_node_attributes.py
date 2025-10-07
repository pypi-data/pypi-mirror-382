import pytest
from maya_brew import OpenMaya2, cmds
from maya_brew.attributes.node_attribute import (
    Attribute,
    FloatAttribute,
    MessageAttribute,
)
from maya_brew.log import get_logger
from maya_brew.nodes.node_types import DagNode, Node

logger = get_logger(__name__)


def test_cast_attributes(brew_transform):
    tx = Attribute(f"{brew_transform.node_path}.translateX")
    assert isinstance(tx, FloatAttribute)
    message = Attribute(f"{brew_transform}.message")
    assert isinstance(message, MessageAttribute)


def test_message_attribute_get_value_error(brew_transform):
    with pytest.raises(AttributeError):
        Attribute._get_value(brew_transform, "message")


def test_attribute_get_value(brew_transform):
    tx = Attribute(f"{brew_transform.node_path}.translateX")
    value = tx.get()
    assert value == 0
    cmds.setAttr(f"{brew_transform.node_path}.translateX", 5)
    value = FloatAttribute._get_value(brew_transform, "translateX")
    assert value == 5


def test_factory_with_mplug(translatex_plug):
    a = Attribute(translatex_plug)
    assert isinstance(a, FloatAttribute)
    assert a.get() == 0


def test_subclass_with_mplug(translatex_plug):
    fa = FloatAttribute(translatex_plug)
    assert fa.get() == 0


def test_invalid_path_missing_dot():
    with pytest.raises(ValueError):
        Attribute("bad_path_without_dot")


def test_invalid_plug_type():
    with pytest.raises(ValueError):
        Attribute(123)  # type: ignore


def test_get_node_from_plug_dag_and_non_dag(translatex_plug, non_dag_plug):
    dag = Attribute._get_node_from_plug(translatex_plug)
    assert isinstance(dag, DagNode)
    expected_dag_path = OpenMaya2.MFnDagNode(translatex_plug.node()).fullPathName()
    assert str(dag) == expected_dag_path

    non_dag = Attribute._get_node_from_plug(non_dag_plug)
    assert isinstance(non_dag, Node)
    assert not isinstance(non_dag, DagNode)
    expected_non_dag_name = OpenMaya2.MFnDependencyNode(non_dag_plug.node()).name()
    non_dag_name = str(non_dag)
    assert non_dag_name == expected_non_dag_name


def test_attribute_set_instance(brew_transform):
    tx = Attribute(f"{brew_transform.node_path}.translateX")
    tx.set(3.14)
    assert cmds.getAttr(f"{brew_transform.node_path}.translateX") == 3.14


def test_attribute_set_redo(brew_transform):
    tx = Attribute(f"{brew_transform.node_path}.translateX")
    initial = cmds.getAttr(f"{brew_transform.node_path}.translateX")
    tx.set(8.88)
    with logger.silence():
        cmds.undo()
    assert cmds.getAttr(f"{brew_transform.node_path}.translateX") == initial
    with logger.silence():
        cmds.redo()
    assert cmds.getAttr(f"{brew_transform.node_path}.translateX") == 8.88


def test_message_attribute_set_value_error(brew_transform):
    message_attr = Attribute(f"{brew_transform}.message")
    with pytest.raises(AttributeError):
        message_attr.set(1)


def test_connect_and_force_overwrite_and_disconnect(brew_transform, test_cube):
    tx_attr = Attribute(f"{brew_transform.node_path}.translateX")
    ty_attr = Attribute(f"{brew_transform.node_path}.translateY")
    cube_ty = Attribute(f"{test_cube}.translateY")

    def get_ty_connections():
        return cmds.listConnections(cube_ty.plug.name(), source=True, plugs=True)

    tx_attr.connect(cube_ty)
    connections = get_ty_connections()
    expected_connection = tx_attr.plug.name()
    assert connections == [expected_connection]

    cmds.undo()
    assert not get_ty_connections()
    cmds.redo()
    assert get_ty_connections() == [expected_connection]

    ty_attr.connect(cube_ty, force=True)
    connections = get_ty_connections()
    expected_connection = ty_attr.plug.name()
    assert connections == [expected_connection]

    cmds.undo()
    assert get_ty_connections() == [tx_attr.plug.name()]
    cmds.redo()
    assert get_ty_connections() == [expected_connection]

    ty_attr.disconnect(cube_ty)
    assert not get_ty_connections()

    cmds.undo()
    assert get_ty_connections() == [ty_attr.plug.name()]
    cmds.redo()
    assert not get_ty_connections()
