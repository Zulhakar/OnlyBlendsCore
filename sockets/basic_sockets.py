import bpy
from bpy.types import NodeSocket, NodeTreeInterfaceSocket
from bpy.utils import register_class, unregister_class

from ..core.constants import (COLOR_OBJECT_SOCKET, COLOR_BLACK, COLOR_STRING_SOCKET, COLOR_INT_SOCKET, COLOR_FLOAT_SOCKET,
                              COLOR_FLOAT_VECTOR_SOCKET, COLOR_EMPTY_SOCKET, COLOR_BOOL_SOCKET, IS_DEBUG,
                              CntSocketTypes, cnt_sockets_list)
from ..core.helper import get_socket_index


class NodeSocketCnt(NodeSocket):
    is_constant: bpy.props.BoolProperty()
    selected_node_group_name: bpy.props.StringProperty()
    node_group_name: bpy.props.StringProperty()
    disable_socket_update : bpy.props.BoolProperty(default=False)

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
        if IS_DEBUG:
            log_string = f"{self.node.bl_idname}-> Socket: {self.bl_idname} update_prop: [name: {self.name},  value: {self.input_value}]"
            print(log_string)
        if hasattr(self.node, "socket_update"):
            self.node.socket_update(self)

        # ----------------------------------------------------------
        # inject update for build in nodes (Group Input/Output Node)

        if isinstance(self.node, bpy.types.NodeGroupOutput):
            if self.selected_node_group_name != "":
                if not self.disable_socket_update:
                    node = self.node
                    tree = bpy.data.node_groups[self.selected_node_group_name]
                    tree2 = bpy.data.node_groups[self.node_group_name]
                    for node_ in tree.nodes:
                        if node_.bl_idname == "GroupNodeCnt":
                            if node_.target_tree == tree2:
                                sock_index = get_socket_index(node.inputs, self)
                                if node_.outputs[sock_index].bl_idname != CntSocketTypes.FloatVectorField:
                                    #node_.was_fired = True
                                    if node_.was_fired:
                                        node_.outputs[sock_index].input_value = self.input_value
                                else:
                                    for link in node_.outputs[sock_index].links:
                                        link.to_socket.input_value.clear()
                                        for item in node.inputs[sock_index].input_value:
                                            new_item = link.to_socket.input_value.add()
                                            new_item.value = item.value
                                        for link2 in node_.outputs[sock_index].links:
                                            link2.to_node.socket_update(link2.to_socket)
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
    input_value: bpy.props.PointerProperty(update=lambda self, context: self.update_prop(), name="Object", type=bpy.types.Object)


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


class NodeSocketFloatVectorCnt(NodeSocketCnt):
    """Float Vector"""
    bl_label = "Float Vector"
    sock_col = COLOR_FLOAT_VECTOR_SOCKET

    input_value: bpy.props.FloatVectorProperty(update=lambda self, context: self.update_prop(), name="FloatVector")

    def draw(self, context, layout, node, text):
        if self.is_constant:
            layout.alignment = 'EXPAND'
            layout.prop(self, "input_value", text="")
        else:
            if self.is_output or self.is_linked:
                layout.label(text=text)
            else:
                layout.prop(self, "input_value", text=text)

class NodeTreeInterfaceSocketFloatVectorCnt(NodeTreeInterfaceSocketCnt):
    bl_socket_idname = 'NodeSocketFloatVectorCnt'

    def draw_color(self, context, node):
        return COLOR_FLOAT_VECTOR_SOCKET


class FloatVectorFieldItem(bpy.types.PropertyGroup):
    # value: bpy.props.FloatVectorProperty(update=lambda self, context: self.update_prop())
    value: bpy.props.FloatVectorProperty()


register_class(FloatVectorFieldItem)


class NodeSocketFloatVectorFieldCnt(NodeSocketCnt):
    bl_label = "Float Vector Field"
    sock_col = COLOR_FLOAT_VECTOR_SOCKET
    input_value: bpy.props.CollectionProperty(type=FloatVectorFieldItem)


class NodeTreeInterfaceSocketFloatVectorFieldCnt(NodeTreeInterfaceSocketCnt):
    bl_socket_idname = 'NodeSocketFloatVectorFieldCnt'
    def draw_color(self, context, node):
        return COLOR_FLOAT_VECTOR_SOCKET


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


class NodeTreeInterfaceSocketStringCnt(NodeTreeInterfaceSocketCnt):
    bl_socket_idname = 'NodeSocketStringCnt'
    def draw_color(self, context, node):
        return COLOR_STRING_SOCKET


class NodeSocketBoolCnt(NodeSocketCnt):
    bl_label = 'Bool'
    sock_col = COLOR_BOOL_SOCKET
    input_value: bpy.props.BoolProperty(update=lambda self, context: self.update_prop(), name="Bool")
    def draw(self, context, layout, node, text):
        layout.alignment = 'LEFT'
        layout.prop(self, "input_value", text=text)


class NodeTreeInterfaceSocketBoolCnt(NodeTreeInterfaceSocketCnt):
    bl_socket_idname = 'NodeSocketBoolCnt'
    def draw_color(self, context, node):
        return COLOR_BOOL_SOCKET


classes = (
    NodeSocketObjectCnt, NodeTreeInterfaceSocketObjectCnt,
    NodeSocketFloatCnt, NodeTreeInterfaceSocketFloatCnt,
    NodeSocketIntCnt, NodeTreeInterfaceSocketIntCnt,
    NodeSocketStringCnt, NodeTreeInterfaceSocketStringCnt,
    NodeSocketBoolCnt, NodeTreeInterfaceSocketBoolCnt,

    NodeSocketFloatVectorCnt, NodeTreeInterfaceSocketFloatVectorCnt,
    NodeSocketFloatVectorFieldCnt, NodeTreeInterfaceSocketFloatVectorFieldCnt
    )


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
