import bpy
from bl_ui import node_add_menu
from .cnt.node_editor import register as register_node_editor
from .cnt.node_editor import unregister as unregister_node_editor
from .cnt.sockets.basic_sockets import register as register_basic_sockets
from .cnt.sockets.basic_sockets import unregister as unregister_basic_sockets
from .cnt.nodes import register as register_nodes
from .cnt.nodes import unregister as unregister_nodes
from .cnt.node_editor.menus import InputMenu, GroupMenu

from .config import OB_TREE_TYPE


def draw_add_menu(self, context):
    layout = self.layout
    if context.space_data.tree_type != OB_TREE_TYPE:
        return
    layout.menu(InputMenu.bl_idname)
    layout.menu(GroupMenu.bl_idname)
    node_add_menu.add_node_type(layout, "MathNodeCnt")

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
