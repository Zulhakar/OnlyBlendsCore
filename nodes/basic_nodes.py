import bpy
from ..core.constants import IS_DEBUG, SINGLE_VALUES_SOCKET_SHAPE, VERSATILE_SOCKET_SHAPE
from ..core.constants import OB_TREE_TYPE, CntSocketTypes


class NodeCnt:
    socket_update_disabled: bpy.props.BoolProperty(default=False)

    def log(self, func_name):
        if IS_DEBUG:
            log_string = f"{self.bl_idname}-> {self.name}: {func_name} was called"
            print(log_string)

    def init(self, context):
        for output in self.outputs:
            if not output.is_multi_input:
                if bpy.app.version < (5, 0, 1):
                    output.display_shape = VERSATILE_SOCKET_SHAPE
                else:
                    output.display_shape = SINGLE_VALUES_SOCKET_SHAPE
        for input in self.inputs:
            if not input.is_multi_input:
                if bpy.app.version < (5, 0, 1):
                    input.display_shape = VERSATILE_SOCKET_SHAPE
                else:
                    input.display_shape = SINGLE_VALUES_SOCKET_SHAPE

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == OB_TREE_TYPE

    def copy(self, node):
        self.log("copy")

    def free(self):
        self.log("free")

    def draw_label(self):
        return self.bl_label

    def insert_link(self, link):
        self.log("insert_link")
        if link.to_socket.bl_idname == link.from_socket.bl_idname:
            link.is_valid = True
        elif link.to_socket.bl_idname == CntSocketTypes.Float and link.from_socket.bl_idname == CntSocketTypes.Integer:
            link.is_valid = True
        elif link.to_socket.bl_idname == CntSocketTypes.Integer and link.from_socket.bl_idname == CntSocketTypes.Float:
            link.is_valid = True
        else:
            if IS_DEBUG:
                print("Wrong Socket ", str(link.from_socket.bl_idname))
            link.is_valid = False
        if link.is_valid and not self.mute:
            for input in self.inputs:
                if link.to_socket == input:
                    if link.to_socket.is_multi_input:
                        pass
                    else:
                        if link.to_socket.bl_idname != CntSocketTypes.FloatVectorField:
                            input.input_value = link.from_socket.input_value

        else:
            pass

    def update(self):
        self.log("update")

    def socket_update(self, socket):
        self.log("socket_update")
        if IS_DEBUG:
            if self.socket_update_disabled:
                print("socket_update_disabled")

    def socket_value_update(self, context):
        self.log("socket_value_update")


class ConstantNodeCnt(NodeCnt, bpy.types.NodeCustomGroup):
    def socket_update(self, socket):
        super().socket_update(socket)
        if not self.mute:
            if not self.socket_update_disabled:
                if len(self.outputs) > 0:
                    for link in self.outputs[0].links:
                        if link.to_socket.bl_idname == CntSocketTypes.Integer and link.from_socket.bl_idname == CntSocketTypes.Float:
                            link.to_socket.input_value = int(self.outputs[0].input_value)
                        else:
                            link.to_socket.input_value = self.outputs[0].input_value


class ObjectNodeCnt(ConstantNodeCnt):
    '''Object Node'''
    bl_label = "Object"

    def init(self, context):
        object_socket = self.outputs.new(CntSocketTypes.Object, "Object")
        object_socket.is_constant = True
        super().init(context)


class FloatNodeCnt(ConstantNodeCnt):
    '''Float Value Node'''
    bl_label = "Value"

    def init(self, context):
        float_socket = self.outputs.new(CntSocketTypes.Float, "Float")
        float_socket.is_constant = True
        super().init(context)

    def copy(self, node):
        self.socket_update_disabled = True
        super().copy(node)
        self.outputs[0].input_value = node.outputs[0].input_value
        self.socket_update_disabled = False


class IntNodeCnt(ConstantNodeCnt):
    '''Integer Node'''
    bl_label = "Integer"

    def init(self, context):
        int_socket = self.outputs.new(CntSocketTypes.Integer, "Integer")
        int_socket.is_constant = True
        super().init(context)


class StringNodeCnt(ConstantNodeCnt):
    '''String Node'''
    bl_label = "String"

    def init(self, context):
        string_socket = self.outputs.new(CntSocketTypes.String, "String")
        string_socket.is_constant = True
        super().init(context)


class BoolNodeCnt(ConstantNodeCnt):
    # class BooleanNodeCnt(FunctionNodeInputBool):
    '''Boolean Value Node'''
    bl_label = "Boolean"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == OB_TREE_TYPE or ntree.bl_idname == "GeometryNodeTree"

    def init(self, context):
        bool_socket = self.outputs.new(CntSocketTypes.Bool, "Boolean")
        bool_socket.is_constant = True
        super().init(context)
