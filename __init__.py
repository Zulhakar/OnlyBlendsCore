import bpy
from .obc_custom_nodes.node_editor import register as register_node_editor
from .obc_custom_nodes.node_editor import unregister as unregister_node_editor
from .obc_custom_nodes.sockets import register as register_basic_sockets
from .obc_custom_nodes.sockets import unregister as unregister_basic_sockets
from .obc_custom_nodes.nodes import register as register_nodes
from .obc_custom_nodes.nodes import unregister as unregister_nodes
from .obc_custom_nodes.node_editor.menus import InputMenu, GroupMenu, UtilMenu, RealtimeMenu, GeometryMenu

from .config import OB_TREE_TYPE


def draw_add_menu(self, context):
    layout = self.layout
    if context.space_data.tree_type != OB_TREE_TYPE:
        return
    layout.menu(InputMenu.bl_idname)
    layout.menu(GroupMenu.bl_idname)
    layout.menu(UtilMenu.bl_idname)
    layout.menu(RealtimeMenu.bl_idname)
    layout.menu(GeometryMenu.bl_idname)


def register():
    register_basic_sockets()
    register_nodes()
    register_node_editor()
    bpy.types.NODE_MT_add.append(draw_add_menu)


def unregister():
    bpy.types.NODE_MT_add.remove(draw_add_menu)
    unregister_basic_sockets()
    unregister_nodes()
    unregister_node_editor()


if __name__ == "__main__":
    register()
