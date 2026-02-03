IS_DEBUG = True
APP_NAME = "CustomNodeTemplate"
APP_NAME_SHORT = "cnt"
OB_TREE_TYPE = 'CustomNodeTree'

TREE_ICON = 'GHOST_ENABLED'

SINGLE_VALUES_SOCKET_SHAPE = 'LINE'
VERSATILE_SOCKET_SHAPE = 'CIRCLE'
FIELDS_SOCKET_SHAPE = 'DIAMOND'

CONSTANTS_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Constants'
INPUT_MENU_IDNAME = f'NODE_MT_{APP_NAME_SHORT}_Input'
GROUP_MENU_IDNAME = f'NOD_MT_{APP_NAME_SHORT}_Group'

MAKE_GROUP_OT_IDNAME= f'node.{APP_NAME_SHORT}_make_group'


COLOR_BLACK = (0.0, 0.0, 0.0, 1.0)
COLOR_WHITE = (1.0, 1.0, 1.0, 1.0)
COLOR_GRAY = (0.62890625, 0.62890625, 0.62890625, 1.0)
COLOR_GRAY_2 = (0.2, 0.2, 0.2, 1.0)
COLOR_GREEN = (0.3515625, 0.546875, 0.36328125, 1.0)

COLOR_OBJECT_SOCKET = (0.92578125, 0.6171875, 0.3593750, 1.0)
COLOR_GEOMETRY_SOCKET = (0.0, 0.8359375, 0.640625, 1.0)
COLOR_FLOAT_SOCKET = COLOR_GRAY
COLOR_INT_SOCKET = COLOR_GREEN
COLOR_STRING_SOCKET = (0.156862745, 0.662745098, 0.980392157, 1.0)
COLOR_EMPTY_SOCKET = COLOR_GRAY_2
COLOR_BOOL_SOCKET = (0.803921569, 0.654901961, 0.839215686, 1.0)
COLOR_FLOAT_VECTOR_SOCKET = (0.388235294, 0.388235294, 0.780392157, 1.0)

class CntNodeTypes:
    GroupNode = 'GroupNode'
    ObjectNode = 'ObjectNode'

class CntSocketTypes:
    String = 'NodeSocketStringCnt'
    Float = 'NodeSocketFloatCnt'
    Integer = 'NodeSocketIntCnt'
    Bool = 'NodeSocketBoolCnt'
    Object = 'NodeSocketObjectCnt'

    FloatVector = 'NodeSocketFloatVectorCnt'
    FloatVectorField = 'NodeSocketFloatVectorFieldCnt'

cnt_sockets_list = [
    (CntSocketTypes.FloatVectorField, "Float Vector Field", "Float Vector Field"),
    (CntSocketTypes.FloatVector, "Float Vector", "Float Vector"),

    (CntSocketTypes.Float, "Float", "Float"),
    (CntSocketTypes.String, "String", "String"),
    (CntSocketTypes.Integer, "Integer", "Integer"),
    (CntSocketTypes.Bool, "Boolean", "Boolean"),
    (CntSocketTypes.Object, "Object", "Object")
]
