import bpy
from bl_ui import node_add_menu
from ...config import OB_TREE_TYPE
from ..base.constants import CONSTANTS_MENU_IDNAME, INPUT_MENU_IDNAME, GROUP_MENU_IDNAME, MAKE_GROUP_OT_IDNAME


class ConstantsMenu(bpy.types.Menu):
    bl_label = 'Constants'
    bl_idname = CONSTANTS_MENU_IDNAME

    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "FloatNodeCnt")
        node_add_menu.add_node_type(layout, "IntNodeCnt")
        node_add_menu.add_node_type(layout, "StringNodeCnt")
        node_add_menu.add_node_type(layout, "BoolNodeCnt")
        #layout.separator()
        #node_add_menu.add_node_type(layout, "VectorNodeCnt")
        #node_add_menu.add_node_type(layout, "CombineXyzNodeCnt")


class InputMenu(bpy.types.Menu):
    bl_label = 'Input'
    bl_idname = INPUT_MENU_IDNAME

    def draw(self, context):
        layout = self.layout
        layout.menu(ConstantsMenu.bl_idname)
        node_add_menu.add_node_type(layout, "NodeGroupInput")


class GroupMenu(bpy.types.Menu):
    bl_label = 'Group'
    bl_idname = GROUP_MENU_IDNAME

    def draw(self, context):
        layout = self.layout
        node_add_menu.add_node_type(layout, "NodeGroupInput")
        node_add_menu.add_node_type(layout, "NodeGroupOutput")
        node_add_menu.add_node_type(layout, "GroupNodeCnt")


def menu_draw(self, context):
    tree = context.space_data.node_tree
    if tree and tree.bl_idname == OB_TREE_TYPE:
        self.layout.operator(MAKE_GROUP_OT_IDNAME,
                             text="Make Group",
                             icon='NODETREE')
