IS_DEBUG = True
APP_NAME = "CustomNodeTemplate"
APP_NAME_SHORT = "cnt"
OB_TREE_TYPE = 'CustomNodeTree'
NEW_NODE_GROUP_NAME = "Custom Nodes"
NODE_EDITOR_NAME = "Custom Node Editor"
TREE_ICON = 'GHOST_ENABLED'

########################################################################################################################
# don't change this
from .cnt.base.constants import *

CONSTANTS_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Constants'
INPUT_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Input'
GROUP_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Group'
REALTIME_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Realtime'
UTIL_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Util'
GEOMETRY_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Geometry'
MAKE_GROUP_OT_IDNAME = f'node.{APP_NAME_SHORT}_make_group'
