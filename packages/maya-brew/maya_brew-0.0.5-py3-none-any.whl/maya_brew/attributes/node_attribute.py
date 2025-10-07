import typing

from .. import OpenMaya2, cmds
from ..exceptions import MayaBrewAttributeError
from ..nodes.node_types import DagNode, Node

PlugInput = typing.Union[OpenMaya2.MPlug, str]
A = typing.TypeVar("A", bound="Attribute")


class Attribute:
    _getter_type: str

    def __new__(cls: type[A], plug_or_path: PlugInput) -> A:
        if cls is not Attribute:
            return typing.cast(A, super().__new__(cls))

        if isinstance(plug_or_path, OpenMaya2.MPlug):
            plug = plug_or_path
        elif isinstance(plug_or_path, str):
            plug = cls._plug_from_path(plug_or_path)
        else:
            raise ValueError("plug_or_path must be an MPlug or attribute path string.")

        try:
            mobj_attr = plug.attribute()
        except (RuntimeError, ValueError) as e:
            raise RuntimeError(
                f"Failed to obtain MObject attribute for plug {plug}"
            ) from e

        api_type = getattr(mobj_attr, "apiTypeStr", None)
        if not api_type:
            raise RuntimeError(
                f"Attribute object for plug {plug} has no apiTypeStr; cannot dispatch."
            )

        try:
            subclass: type[Attribute] = _API_TYPE_SUBCLASS_MAP[api_type]
        except KeyError:
            raise NotImplementedError(
                f"Unsupported attribute apiTypeStr '{api_type}'. Could cast attribute for '{plug}'. "
                f"Known types: {sorted(_API_TYPE_SUBCLASS_MAP)}"
            )

        instance = super().__new__(subclass)
        setattr(instance, "_pre_init_plug", plug)
        return typing.cast(A, instance)

    @typing.overload
    def __init__(self, plug_or_path: str): ...

    @typing.overload
    def __init__(self, plug_or_path: OpenMaya2.MPlug): ...

    def __init__(self, plug_or_path: PlugInput):
        # _pre_init_plug is injected by Attribute.__new__ ONLY when the user called
        # Attribute(...) (base class factory dispatch). Direct subclass construction
        # (e.g. FloatAttribute(...)) bypasses that path, so pre will be None and we
        # must resolve plug_or_path here.
        pre = getattr(self, "_pre_init_plug", None)
        if pre is not None:
            self.plug = pre
            delattr(self, "_pre_init_plug")
            return

        if isinstance(plug_or_path, OpenMaya2.MPlug):
            self.plug = plug_or_path
        elif isinstance(plug_or_path, str):
            self.plug = self._plug_from_path(plug_or_path)
        else:
            raise ValueError("plug_or_path must be an MPlug or attribute path string.")

    @staticmethod
    def _plug_from_path(path: str) -> OpenMaya2.MPlug:
        """
        Resolve a string path to an MPlug using MSelectionList and MFnDependencyNode.
        Works for both DAG and dependency nodes without casting.
        :param path: The full path to the attribute, e.g. '|grp|node|nodeShape.visibility'
        :return: The MPlug for the attribute.
        """
        if "." not in path:
            raise ValueError(
                "Attribute path must include a '.' separating node and attribute."
            )
        node_path, attr_name = path.rsplit(".", 1)
        selection_list = OpenMaya2.MSelectionList()
        selection_list.add(node_path)
        mobj = selection_list.getDependNode(0)
        fn_dep = OpenMaya2.MFnDependencyNode(mobj)
        return fn_dep.findPlug(attr_name, False)

    def __str__(self):
        return self.name()

    def get(self):
        return self._get_plug_value(self.plug)

    def set(self, value):
        attr_name = self.plug.name()
        cmds.setAttr(attr_name, value)

    def node(self):
        return self._get_node_from_plug(self.plug)

    def name(self):
        return self.plug.name()

    def connect(self, dest: "Attribute", force: bool = False, next_available=False):
        """
        Connect this attribute to another attribute.
        :param dest: The destination attribute to connect to.
        :param force: Whether to force the connection if the destination is already connected.
        :param next_available: Whether to connect to the next available index if the destination is an array attribute.
        """
        cmds.connectAttr(
            self.plug.name(),
            dest.plug.name(),
            force=force,
            nextAvailable=next_available,
        )

    def disconnect(self, dest: "Attribute", next_available=False):
        """
        Disconnect this attribute from another attribute.
        :param dest: The destination attribute to disconnect from.
        :param next_available: Whether to disconnect from the next available index if the destination is an
        array attribute.
        """
        cmds.disconnectAttr(
            self.plug.name(), dest.plug.name(), nextAvailable=next_available
        )

    @classmethod
    def _get_value(cls, node: Node, attr_name: str):
        plug = cls._get_plug_from_node(node, attr_name)
        return cls._get_plug_value(plug)

    @staticmethod
    def _get_plug_from_node(node: Node, attr_name: str) -> OpenMaya2.MPlug:
        """
        Get the MPlug for the given attribute name from a Node or DagNode.
        """
        if hasattr(node, "get_mfndependency_node"):
            fn_dep = node.get_mfndependency_node()
        else:
            # For non-DAG nodes, resolve node.node_path to MObject
            selection_list = OpenMaya2.MSelectionList()
            selection_list.add(node.node_path)
            mobj = selection_list.getDependNode(0)
            fn_dep = OpenMaya2.MFnDependencyNode(mobj)
        return fn_dep.findPlug(attr_name, False)

    @staticmethod
    def _get_node_from_plug(plug: OpenMaya2.MPlug) -> Node:
        mobj = plug.node()
        if mobj.hasFn(OpenMaya2.MFn.kDagNode):
            return DagNode(OpenMaya2.MFnDagNode(mobj).fullPathName())
        else:
            name = OpenMaya2.MFnDependencyNode(mobj).name()
            return Node(name)

    @classmethod
    def _get_plug_value(cls, plug: OpenMaya2.MPlug):
        return getattr(plug, cls._getter_type)()


class FloatAttribute(Attribute):
    _getter_type = "asDouble"


class BoolAttribute(Attribute):
    _getter_type = "asBool"


class MessageAttribute(Attribute):
    _getter_type = "kMessage"

    @classmethod
    def _get_plug_value(cls, plug: OpenMaya2.MPlug):
        raise MayaBrewAttributeError("Message attributes do not hold data.")

    @classmethod
    def set(cls, value):
        raise MayaBrewAttributeError("Message attributes are not settable.")


class EnumAttribute(Attribute):
    _getter_type = "asShort"


class TypedAttribute(Attribute):
    """
    Handles Maya kTypedAttribute types. By default, returns the MObject stored in the plug.
    Extend this class if you need to handle specific typed data (e.g., strings, matrices).
    """

    _getter_type = "asMObject"


class CompoundAttribute(Attribute):
    """
    Handles Maya kCompoundAttribute types. Returns a list of child Attribute instances.
    """

    @classmethod
    def _get_plug_value(cls, plug: OpenMaya2.MPlug):
        children = []
        for i in range(plug.numChildren()):
            child_plug = plug.child(i)
            children.append(Attribute(child_plug))
        return children


class MultiFloatAttribute(Attribute):
    _num_children: int

    @classmethod
    def _get_plug_value(cls, plug: OpenMaya2.MPlug):
        if plug.numChildren() != cls._num_children:
            raise MayaBrewAttributeError(
                f"Expected {cls._num_children} children for kAttribute3Double, got {plug.numChildren()} on '{plug.name()}'"
            )
        return tuple(plug.child(i).asDouble() for i in range(cls._num_children))


class Float2Attribute(Attribute):
    """
    Handles Maya kAttribute2Double types (e.g., UV coordinates).
    Returns a tuple of two float values (u, v).
    """

    _num_children = 2


class Float3Attribute(Attribute):
    """
    Handles Maya kAttribute3Double types (e.g., translate, rotate, scale).
    Returns a tuple of three float values (x, y, z).
    """

    _num_children = 3


class Float4Attribute(Attribute):
    """
    Handles Maya kAttribute4Double types (e.g., quaternions).
    Returns a tuple of four float values (x, y, z, w).
    """

    _num_children = 4


class MatrixAttribute(Attribute):
    """
    Handles Maya kMatrixAttribute types. Returns an OpenMaya2.MMatrix instance.
    """

    @classmethod
    def _get_plug_value(cls, plug: OpenMaya2.MPlug):
        mobj = plug.asMObject()
        matrix_data = OpenMaya2.MFnMatrixData(mobj)
        return matrix_data.matrix()


class GenericAttribute(Attribute):
    """
    Handles Maya kGenericAttribute types. Returns the MObject stored in the plug, or raises an error if not supported.
    """

    @classmethod
    def _get_plug_value(cls, plug: OpenMaya2.MPlug):
        return plug.asMObject()


_API_TYPE_SUBCLASS_MAP = {
    "kDoubleLinearAttribute": FloatAttribute,
    "kMessageAttribute": MessageAttribute,
    "kNumericAttribute": BoolAttribute,
    "kEnumAttribute": EnumAttribute,
    "kTypedAttribute": TypedAttribute,
    "kCompoundAttribute": CompoundAttribute,
    "kAttribute3Double": Float3Attribute,
    "kAttribute4Double": Float4Attribute,
    "kAttribute2Float": Float2Attribute,
    "kAttribute3Float": Float3Attribute,
    "kDoubleAngleAttribute": FloatAttribute,
    "kMatrixAttribute": MatrixAttribute,
    "kGenericAttribute": GenericAttribute,
}


class AttributeAccessor:
    def __init__(self, node: "Node"):
        self._node = node

    def __getattr__(self, attr_name: str):
        try:
            return Attribute(f"{self._node}.{attr_name}")
        except (ValueError, RuntimeError, NotImplementedError, AttributeError) as e:
            raise MayaBrewAttributeError(
                f"Failed to access attribute '{attr_name}' on node '{self._node}'"
            ) from e
