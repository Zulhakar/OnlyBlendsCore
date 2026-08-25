import bpy
from ..basic_nodes import ConstantNodeCnt


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

    def __del_object_if_exit(self, object_name):
        if object_name in bpy.data.objects:
            obj = bpy.data.objects[object_name]
            # obj.data.clear_geometry()
            # mesh = obj.data
            bpy.data.meshes.remove(obj.data)

    def _do_duplicate(self):
        src = self.inputs[0].input_value
        name = self.inputs[1].input_value
        if src:
            if self.obj is not None and self.obj.name == name and getattr(self, "_dup_src", None) == src:
                self.outputs[0].input_value = self.obj
                return
            if self.obj:
                self.__del_object_if_exit(self.obj.name)
            self.obj = duplicate(src, True, True, self.inputs[2].default_value, name)
            self._dup_src = src
            self.outputs[0].input_value = self.obj
        else:
            if self.obj:
                self.__del_object_if_exit(self.obj.name)
                self.obj = None
            self._dup_src = None

    def init(self, context):
        self.inputs.new("NodeSocketObjectCnt", "Object")
        self.inputs.new("NodeSocketStringCnt", "Name")
        self.inputs.new("NodeSocketCollection", "Collection")
        self.outputs.new("NodeSocketObjectCnt", "Object")
        super().init(context)

    def recompute(self):
        self._do_duplicate()

    def socket_update(self, socket):
        super().socket_update(socket)
        if not socket.is_output:
            self._do_duplicate()

    def copy(self, node):
        super().copy(node)
        self.obj = None
        self._dup_src = None

    def free(self):
        super().free()
        if self.obj:
            bpy.data.objects.remove(self.obj, do_unlink=True)
        if self.outputs[0].input_value:
            bpy.data.objects.remove(self.obj, do_unlink=True)
