import bpy
from ..basic_nodes import ConstantNodeCnt
from ...base.constants import CntSocketTypes, VERSATILE_SOCKET_SHAPE
from ....config import IS_DEBUG


class MathNodeCnt(ConstantNodeCnt):
    '''Basic Math operations'''
    bl_label = "Math"
    operations_enums = (
        ('ADD', 'Add', 'Add'),
        ('SUB', 'Subtract', 'Subtract'),
        ('MUL', 'Multiply', 'Multiply'),
        ('DIV', 'Divide', 'Divide')
    )
    operation: bpy.props.EnumProperty(  # type: ignore
        name="Operation"
        , items=operations_enums
        , default="ADD"
        , update=lambda self, context: self.operation_update())

    def operation_update(self):
        if self.operation == "ADD":
            self.outputs[0].input_value = (self.inputs[0].input_value + self.inputs[1].input_value)
        elif self.operation == "SUB":
            self.outputs[0].input_value = (self.inputs[0].input_value - self.inputs[1].input_value)
        elif self.operation == "MUL":
            self.outputs[0].input_value = (self.inputs[0].input_value * self.inputs[1].input_value)
        elif self.operation == "DIV":
            if self.inputs[1].input_value == 0.0:
                import sys
                self.outputs[0].input_value = sys.float_info.max
            else:
                self.outputs[0].input_value = (self.inputs[0].input_value / self.inputs[1].input_value)
        for link in self.outputs[0].links:
            link.to_socket.input_value = self.outputs[0].input_value

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            if len(self.outputs) > 0:
                layout.label(text=f"input1: {self.inputs[0].input_value}")
                layout.label(text=f"input2: {self.inputs[1].input_value}")
                layout.label(text=f"output: {self.outputs[0].input_value}")
        layout.prop(self, "operation", text="")


    def init(self, context):
        self.inputs.new(CntSocketTypes.Float, "Float")
        self.inputs.new(CntSocketTypes.Float, "Float")
        self.outputs.new(CntSocketTypes.Float, "Float")
        super().init(context)
        self.inputs[0].display_shape = VERSATILE_SOCKET_SHAPE
        self.inputs[1].display_shape = VERSATILE_SOCKET_SHAPE
        self.outputs[0].display_shape = VERSATILE_SOCKET_SHAPE
        #self.outputs[0].is_constant = True

    def socket_update(self, socket):
        if socket != self.outputs[0]:
            self.operation_update()


    def update(self):
        if self.mute:
            self.outputs[0].input_value = self.inputs[0].input_value
            for link in self.outputs[0].links:
                link.to_socket.input_value = self.outputs[0].input_value
        else:
            self.operation_update()

    def copy(self, node):
        super().copy(node)
        #ctrl + V / C crashed with the following line, this is a blender core problem or has to do with inheritance
        #self.operation = node.operation