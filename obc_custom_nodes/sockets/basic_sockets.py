import bpy
from bpy.types import NodeSocket, NodeTreeInterfaceSocket

from ...config import (COLOR_OBJECT_SOCKET, COLOR_BLACK, COLOR_STRING_SOCKET, COLOR_INT_SOCKET, COLOR_FLOAT_SOCKET,
                       COLOR_FLOAT_VECTOR_SOCKET, COLOR_EMPTY_SOCKET, COLOR_BOOL_SOCKET,
                       CntSocketTypes, cnt_sockets_list)
from ..base.helper import get_socket_index
from ...config import IS_DEBUG

def get_all_group_nodes(selected_node_group, node_group):
    group_nodes = []
    for node_ in selected_node_group.nodes:
        if node_.bl_idname == "GroupNodeCnt":
            if node_.target_tree == node_group:
                group_nodes.append(node_)
    return group_nodes

class NodeSocketCnt(NodeSocket):
    is_constant: bpy.props.BoolProperty()
    selected_node_group_name: bpy.props.StringProperty()
    node_group_name: bpy.props.StringProperty()
    disable_socket_update: bpy.props.BoolProperty(default=False)

    silent_updates = False

    def draw(self, context, layout, node, text):
        if self.is_constant:
            layout.alignment = 'EXPAND'
            layout.prop(self, "input_value", text="")
        else:
            if self.is_output or self.is_linked:
                layout.label(text=text)
            else:
                layout.prop(self, "input_value", text=text)

    def update_prop(self):
        if NodeSocketCnt.silent_updates:
            return
        if getattr(self, "_updating", False):
            return
        self._updating = True
        try:
            if hasattr(self.node, "socket_update"):
                if getattr(self.node, "_updating", False):
                    return
                # node.socket_update itself decides whether to recompute
                self.node._updating = True
                try:
                    self.node.socket_update(self)
                finally:
                    self.node._updating = False

            if isinstance(self.node, bpy.types.NodeGroupOutput):
                self.__group_node_link_function()
        finally:
            self._updating = False

    def __group_node_link_function(self):
        # A NodeGroupOutput socket changed -> the shared tree's result changed.
        # Re-evaluate every instance with its own inputs.
        tree = self.node.id_data
        if tree is not None and hasattr(tree, 'evaluate_all'):
            tree.evaluate_all()


    @classmethod
    def draw_color_simple(cls):
        return cls.sock_col


class NodeTreeInterfaceSocketCnt(bpy.types.NodeTreeInterfaceSocket):
    cnt_socket_type: bpy.props.EnumProperty(  # type: ignore
        name="Socket Type CNT"
        , items=cnt_sockets_list
        , default=CntSocketTypes.Float,
        update=lambda self, context: self.cnt_socket_type_update()
    )
    default_value: bpy.props.StringProperty()
    selected_node_group_name: bpy.props.StringProperty()
    node_group_name: bpy.props.StringProperty()

    def cnt_socket_type_update(self):
        self.socket_type = self.cnt_socket_type

    def draw(self, context, layout):
        layout.prop(self, "default_value")

    def init_socket(self, node, socket, data_path):
        socket.input_value = self.default_value

    def draw_color(self, context, node):
        return COLOR_BLACK


class NodeSocketObjectCnt(NodeSocketCnt):
    bl_label = "Object"
    sock_col = COLOR_OBJECT_SOCKET
    input_value: bpy.props.PointerProperty(update=lambda self, context: self.update_prop(), name="Object",
                                           type=bpy.types.Object)

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "input_value", text="", placeholder=self.name)


class NodeTreeInterfaceSocketObjectCnt(NodeTreeInterfaceSocketCnt):
    bl_socket_idname = 'NodeSocketObjectCnt'

    def draw_color(self, context, node):
        # cls.display_shape = "SQUARE"
        return COLOR_OBJECT_SOCKET


class NodeSocketFloatCnt(NodeSocketCnt):
    bl_label = "Float"
    sock_col = COLOR_FLOAT_SOCKET
    input_value: bpy.props.FloatProperty(update=lambda self, context: self.update_prop(), name="Float")


class NodeTreeInterfaceSocketFloatCnt(NodeTreeInterfaceSocketCnt):
    bl_socket_idname = 'NodeSocketFloatCnt'

    def draw_color(self, context, node):
        return COLOR_FLOAT_SOCKET


class NodeSocketIntCnt(NodeSocketCnt):
    bl_label = "Integer"
    sock_col = COLOR_INT_SOCKET
    input_value: bpy.props.IntProperty(update=lambda self, context: self.update_prop(), name="Integer")


class NodeTreeInterfaceSocketIntCnt(NodeTreeInterfaceSocketCnt):
    bl_socket_idname = 'NodeSocketIntCnt'

    def draw_color(self, context, node):
        return COLOR_INT_SOCKET


class NodeSocketStringCnt(NodeSocketCnt):
    bl_label = "String"
    sock_col = COLOR_STRING_SOCKET
    input_value: bpy.props.StringProperty(update=lambda self, context: self.update_prop(), name="String")

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "input_value", text="", placeholder=self.name)


class NodeTreeInterfaceSocketStringCnt(NodeTreeInterfaceSocketCnt):
    bl_socket_idname = 'NodeSocketStringCnt'

    def draw_color(self, context, node):
        return COLOR_STRING_SOCKET


class NodeSocketBoolCnt(NodeSocketCnt):
    bl_label = 'Bool'
    sock_col = COLOR_BOOL_SOCKET
    input_value: bpy.props.BoolProperty(update=lambda self, context: self.update_prop(), name="Bool")

    def draw(self, context, layout, node, text):
        if self.is_constant:
            layout.alignment = 'LEFT'
            layout.prop(self, "input_value", text=text)
        else:
            if self.is_output or self.is_linked:
                layout.label(text=text)
            else:
                layout.prop(self, "input_value", text=text)


class NodeTreeInterfaceSocketBoolCnt(NodeTreeInterfaceSocketCnt):
    bl_socket_idname = 'NodeSocketBoolCnt'

    def draw_color(self, context, node):
        return COLOR_BOOL_SOCKET


classes = [
    NodeSocketObjectCnt, NodeTreeInterfaceSocketObjectCnt,
    NodeSocketFloatCnt, NodeTreeInterfaceSocketFloatCnt,
    NodeSocketIntCnt, NodeTreeInterfaceSocketIntCnt,
    NodeSocketStringCnt, NodeTreeInterfaceSocketStringCnt,
    NodeSocketBoolCnt, NodeTreeInterfaceSocketBoolCnt,
]
