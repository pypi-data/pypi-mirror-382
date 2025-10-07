from .. import OpenMaya2, cmds, exceptions


class NodeCastingException(exceptions.MayaBrewException):
    """Base class for node casting exceptions."""

    pass


class InvalidDagPath(NodeCastingException, RuntimeError, ValueError, TypeError):
    """Exception raised when a DAG path is invalid."""

    pass


class NonExistingDagPath(NodeCastingException, RuntimeError, ValueError, TypeError):
    """Exception raised when a DAG path is invalid."""

    pass


class MultipleMatchingNodes(NodeCastingException):
    """Exception raised when multiple nodes match a given name."""

    pass


class NoMatchingNodes(NodeCastingException):
    """Exception raised when no nodes match a given name."""

    pass


def get_dag_path_from_string(node_path: str) -> OpenMaya2.MDagPath:
    """
    Convert a string representation of a node path to an OpenMaya2.MDagPath object.
    """
    selection_list = OpenMaya2.MSelectionList()
    try:
        selection_list.add(node_path)
        dag_path = selection_list.getDagPath(0)
    except RuntimeError as e:
        if "Object does not exist" in str(e):
            raise NonExistingDagPath(f"Dag Path does not exist: {node_path}") from e
        raise
    except TypeError as e:
        if "item is not a DAG path" in str(e):
            raise InvalidDagPath(f"{node_path} exists but is not a dag object") from e
        raise
    return dag_path


def get_long_name_from_maya_string(name: str) -> str:
    """
    Convert a unique maya.cmds node string to a long name.
    """
    matching_nodes = cmds.ls(name, long=True)
    if not matching_nodes:
        raise NoMatchingNodes(f"No objects matching '{name}' in scene")
    num_nodes = len(matching_nodes)
    if num_nodes > 1:
        raise MultipleMatchingNodes(
            f"Multiple objects matching '{name}' in scene. Found {num_nodes} nodes: {matching_nodes}"
        )
    return matching_nodes[0]
