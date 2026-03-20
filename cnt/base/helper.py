import bpy
from ...config import VERSATILE_SOCKET_SHAPE, SINGLE_VALUES_SOCKET_SHAPE, FIELDS_SOCKET_SHAPE
from ...config import CntSocketTypes

def get_socket_index(sockets, socket):
    for i , value in enumerate(sockets):
        if socket == value:
            return i
    return None


def change_socket_shape(node):
    for socket in node.inputs:
        if socket.bl_idname != "NodeSocketVirtual":
            if bpy.app.version < (5, 0, 1):
                socket.display_shape = VERSATILE_SOCKET_SHAPE
            else:
                socket.display_shape = SINGLE_VALUES_SOCKET_SHAPE
    for socket in node.outputs:
        if socket.bl_idname != "NodeSocketVirtual":
            if bpy.app.version < (5, 0, 1):
                socket.display_shape = VERSATILE_SOCKET_SHAPE
            else:
                socket.display_shape = SINGLE_VALUES_SOCKET_SHAPE


def get_parent_node_group(self, tree):
    parent = self.parent_node_tree
    while parent:
        if tree == parent:
            return False
        parent = parent.parent
    return True
