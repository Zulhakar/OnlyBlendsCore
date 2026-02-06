import bpy
from bpy.utils import register_class
from bpy.utils import unregister_class
from .group_nodes.group_node import GroupNodeCnt
from .basic_nodes import IntNodeCnt, FloatNodeCnt, StringNodeCnt, ObjectNodeCnt, BoolNodeCnt
from .constant_nodes.math_node import MathNodeCnt

classes = [
    ObjectNodeCnt,
    FloatNodeCnt,
    IntNodeCnt,
    StringNodeCnt,
    BoolNodeCnt,
    GroupNodeCnt,
    MathNodeCnt,

]

def register():
    for node_class in classes:
        bpy.utils.register_class(node_class)

def unregister():
    for node_class in classes:
        bpy.utils.unregister_class(node_class)