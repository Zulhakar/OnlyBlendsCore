import bpy
from ..basic_nodes import ConstantNodeCnt
from ....config import IS_DEBUG, CntSocketTypes, VERSATILE_SOCKET_SHAPE, cnt_sockets_list


class CompareAndBoolNodeCnt(ConstantNodeCnt):
    '''Compare and Bool operations in one Node'''
    bl_label = "Compare / Bool"

    operation: bpy.props.EnumProperty(  # type: ignore
        name="Operation"
        , items=lambda self, context: self.get_operation_enums(context)
        , update=lambda self, context: self.operation_update())

    socket_type_enums = cnt_sockets_list[:4]

    socket_type: bpy.props.EnumProperty(  # type: ignore
        name="Socket Type"
        , items=socket_type_enums
        , default=socket_type_enums[0][0]
        , update=lambda self, context: self.socket_type_update())

    def init(self, context):
        for i, socket_type in enumerate(self.socket_type_enums):
            s = self.inputs.new(socket_type[0], socket_type[1])
            s1 = self.inputs.new(socket_type[0], socket_type[1])
            if i != 0:
                s.hide = True
                s1.hide = True
        self.outputs.new(CntSocketTypes.Bool, "Output")
        super().init(context)

    def socket_type_update(self):
        for input in self.inputs:
            if input.bl_idname == self.socket_type:
                input.hide = False
            else:
                input.hide = True

    def get_operation_enums(self, context):
        if self.socket_type == CntSocketTypes.Bool:
            return (
                ('AND', 'And', 'And'),
                ('OR', 'Or', 'Or'),
                ('XOR', 'Xor', 'Xor'),
                ('EQUAL', 'Equal', 'Equal'),
                ('NOTEQUAL', 'Not Equal', 'Not Equal'),
            )
        elif self.socket_type == CntSocketTypes.String:
            return (
                ('EQUAL', 'Equal', 'Equal'),
                ('NOTEQUAL', 'Not Equal', 'Not Equal')
            )
        else:
            return (
                ('GREATER', 'Greater Than', 'Greater Than'),
                ('LESS', 'Less Than', 'Less Than'),
                ('EQUAL', 'Equal', 'Equal'),
            )

    def operation_update(self):
        input1 = None
        input2 = None
        if len(self.outputs) > 0:
            output1 = self.outputs[0]
            for input in self.inputs:
                if not input.hide and not input1:
                    input1 = input
                    continue
                if not input.hide and input1:
                    input2 = input
                    break

            if self.operation == "GREATER":
                output1.input_value = input1.input_value > input2.input_value
            elif self.operation == "LESS":
                output1.input_value = input1.input_value < input2.input_value
            elif self.operation == "EQUAL":
                output1.input_value = input1.input_value == input2.input_value
            elif self.operation == "NOT EQUAL":
                output1.input_value = input1.input_value != input2.input_value
            elif self.operation == "AND":
                output1.input_value = input1.input_value and input2.input_value
            elif self.operation == "OR":
                output1.input_value = input1.input_value or input2.input_value
            elif self.operation == "XOR":
                output1.input_value = input1.input_value ^ input2.input_value

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            if len(self.outputs) > 0:
                for output in self.outputs:
                    if not output.hide:
                        layout.label(text=f"output: {output.input_value}")
                for input in self.inputs:
                    if not input.hide:
                        layout.label(text=f"input: {input.input_value}")

        layout.prop(self, "operation", text="")
        layout.prop(self, "socket_type", text="")

    def socket_update(self, socket):
        if not socket.is_output:
            self.operation_update()
        else:
            for link in socket.links:
                link.to_socket.input_value = socket.input_value

    def update(self):
        # ToDO test it
        if self.mute:
            self.outputs[0].input_value = self.inputs[0].input_value
            for link in self.outputs[0].links:
                link.to_socket.input_value = self.outputs[0].input_value
        else:
            self.operation_update()

    def copy(self, node):
        super().copy(node)
        # ctrl + V / C crashed with the following line, this is a blender core problem or has to do with inheritance
        # self.operation = node.operation
