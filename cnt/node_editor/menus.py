import bpy
from bl_ui import node_add_menu
from ...config import OB_TREE_TYPE
from ...config import (CONSTANTS_MENU_IDNAME, INPUT_MENU_IDNAME, GROUP_MENU_IDNAME, REALTIME_MENU_IDNAME,
                       UTIL_MENU_IDNAME, GEOMETRY_MENU_IDNAME, MAKE_GROUP_OT_IDNAME)


class ConstantsMenu(bpy.types.Menu):
    bl_label = 'Constants'
    bl_idname = CONSTANTS_MENU_IDNAME

    def draw(self, context):
        layout = self.layout
        node_add_menu.AddNodeMenu.node_operator(layout, "FloatNodeCnt")
        node_add_menu.AddNodeMenu.node_operator(layout, "IntNodeCnt")
        node_add_menu.AddNodeMenu.node_operator(layout, "StringNodeCnt")
        node_add_menu.AddNodeMenu.node_operator(layout, "BoolNodeCnt")



class InputMenu(bpy.types.Menu):
    bl_label = 'Input'
    bl_idname = INPUT_MENU_IDNAME

    def draw(self, context):
        layout = self.layout
        layout.menu(ConstantsMenu.bl_idname)
        node_add_menu.AddNodeMenu.node_operator(layout, "NodeGroupInput")


class GroupMenu(bpy.types.Menu):
    bl_label = 'Group'
    bl_idname = GROUP_MENU_IDNAME

    def draw(self, context):
        layout = self.layout
        node_add_menu.AddNodeMenu.node_operator(layout, "NodeGroupInput")
        node_add_menu.AddNodeMenu.node_operator(layout, "NodeGroupOutput")
        node_add_menu.AddNodeMenu.node_operator(layout, "GroupNodeCnt")


class RealtimeMenu(bpy.types.Menu):
    bl_label = 'Realtime'
    bl_idname = REALTIME_MENU_IDNAME

    def draw(self, context):
        layout = self.layout
        node_add_menu.AddNodeMenu.node_operator(layout, "RealtimeValueNode")
        node_add_menu.AddNodeMenu.node_operator(layout, "SceneInfoNodeCnt")
        # atm inside obg
        # node_add_menu.add_node_type(layout, "TransformObjectNodeCnt")
        node_add_menu.AddNodeMenu.node_operator(layout, "DuplicateObjectNode")


class GeometryMenu(bpy.types.Menu):
    bl_label = 'Geometry Nodes'
    bl_idname = GEOMETRY_MENU_IDNAME

    def draw(self, context):
        layout = self.layout
        node_add_menu.AddNodeMenu.node_operator(layout, "ModifierControlNode")


class UtilMenu(bpy.types.Menu):
    bl_label = 'Util'
    bl_idname = UTIL_MENU_IDNAME

    def draw(self, context):
        layout = self.layout
        node_add_menu.AddNodeMenu.node_operator(layout, "MathNodeCnt")
        node_add_menu.AddNodeMenu.node_operator(layout, "SwitchNodeCnt")
        node_add_menu.AddNodeMenu.node_operator(layout, "CompareAndBoolNodeCnt")


def menu_draw(self, context):
    tree = context.space_data.node_tree
    if tree and tree.bl_idname == OB_TREE_TYPE:
        self.layout.operator(MAKE_GROUP_OT_IDNAME,
                             text="Make Group",
                             icon='NODETREE')
