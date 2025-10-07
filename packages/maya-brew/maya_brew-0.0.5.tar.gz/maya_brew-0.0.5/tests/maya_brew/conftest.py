import maya_brew
import maya_brew.nodes.node_types
import maya_brew.scene
import pytest
from maya_brew import OpenMaya2


@pytest.fixture()
def test_namespace():
    return "my_namespace"


@pytest.fixture()
def test_cube_short_name():
    return "test_cube"


@pytest.fixture()
def test_cube(test_namespace, test_cube_short_name):
    cube, history = maya_brew.cmds.polyCube(
        name=f"{test_namespace}:{test_cube_short_name}"
    )
    yield cube


@pytest.fixture()
def brew_transform():
    """
    Fixture to return the node object of the test cube.
    """
    yield maya_brew.nodes.node_types.Transform.create("test_transform")


@pytest.fixture(autouse=True)
def new_scene():
    return maya_brew.scene.new_file()


@pytest.fixture()
def translatex_plug(brew_transform):
    """Provide the MPlug for translateX on the empty_transform."""
    fn = brew_transform.get_mfndependency_node()
    return fn.findPlug("translateX", False)


@pytest.fixture()
def non_dag_plug():
    """Provide the MPlug for a non-DAG dependency node (multiplyDivide.input1X)."""
    name = "test_multiplyDivide"
    maya_brew.cmds.createNode("multiplyDivide", name=name)
    sel = OpenMaya2.MSelectionList()
    sel.add(name)
    mobj = sel.getDependNode(0)
    fn = OpenMaya2.MFnDependencyNode(mobj)
    return fn.findPlug("input1X", False)
