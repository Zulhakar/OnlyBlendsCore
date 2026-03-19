IS_DEBUG = True
APP_NAME = "OnlyBlends.Core"
APP_NAME_SHORT = "obc"
OB_TREE_TYPE = 'OnlyBlendsCoreNodeTree'
NEW_NODE_GROUP_NAME = "Core Nodes"
NODE_EDITOR_NAME = "OnlyBlends.Core Node Editor"
TREE_ICON = 'GHOST_ENABLED'
VALID_TREES = [OB_TREE_TYPE, 'OnlyBlendsGamepadNodeTree', 'OnlyBlendsMixerNodeTree']
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
