import bpy
from ..basic_nodes import ConstantNodeCnt
from ...base.helper import get_socket_index


def duplicate(obj, data=True, actions=True, collection=None, name=None):
    obj_copy = obj.copy()
    if name:
        obj_copy.name = name
    if data:
        obj_copy.data = obj_copy.data.copy()
    if actions and obj_copy.animation_data:
        obj_copy.animation_data.action = obj_copy.animation_data.action.copy()
    if collection:
        collection.objects.link(obj_copy)
    else:
        bpy.context.collection.objects.link(obj_copy)
    return obj_copy


class DuplicateObjectNode(ConstantNodeCnt):
    '''Duplicate an Object'''
    bl_label = "Duplicate Object"

    obj: bpy.props.PointerProperty(
        type=bpy.types.Object
    )

    last_name: bpy.props.StringProperty()

    def init(self, context):
        self.inputs.new("NodeSocketObjectCnt", "Object")
        self.inputs.new("NodeSocketStringCnt", "Name")
        self.inputs.new("NodeSocketCollection", "Collection")
        self.outputs.new("NodeSocketObjectCnt", "Object")
        super().init(context)

    def __del_object_if_exit(self, object_name):
        if object_name in bpy.data.objects:
            obj = bpy.data.objects[object_name]
            #obj.data.clear_geometry()
            #mesh = obj.data
            bpy.data.meshes.remove(obj.data)

    def socket_update(self, socket):
        super().socket_update(socket)
        if not socket.is_output:
            if self.inputs[0].input_value:
                if self.obj:
                    self.__del_object_if_exit(self.obj.name)
                self.obj = duplicate(self.inputs[0].input_value, True, True, self.inputs[2].default_value, self.inputs[1].input_value)
                self.outputs[0].input_value = self.obj
            else:
                if self.obj:
                    self.__del_object_if_exit(self.obj.name)
                    self.obj = None

    def copy(self, node):
        super().copy(node)
        self.obj = None

    def free(self):
        super().free()
        if self.obj:
            bpy.data.objects.remove(self.obj, do_unlink=True)
        if self.outputs[0].input_value:
            bpy.data.objects.remove(self.obj, do_unlink=True)

