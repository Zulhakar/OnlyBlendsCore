import bpy
from ..basic_nodes import ConstantNodeCnt
from ....config import IS_DEBUG, CntSocketTypes, VERSATILE_SOCKET_SHAPE


class MathNodeCnt(ConstantNodeCnt):
    '''Basic Math operations'''
    bl_label = "Math"
    operations_enums = (
        ('ADD', 'Add', 'Add'),
        ('SUB', 'Subtract', 'Subtract'),
        ('MUL', 'Multiply', 'Multiply'),
        ('DIV', 'Divide', 'Divide'),
        ('GREATER', 'Greater Than', 'Greater Than'),
        ('LESS', 'Less Than', 'Less Than'),
        ('EQUAL', 'Equal', 'Equal'),
    )
    operation: bpy.props.EnumProperty(  # type: ignore
        name="Operation"
        , items=operations_enums
        , default="ADD"
        , update=lambda self, context: self.operation_update())

    def operation_update(self):
        if len(self.outputs) > 0:
            self.outputs[0].hide = False
            self.outputs[1].hide = True
            self.inputs[0].name = "Value"
            self.inputs[1].name = "Value"
            if self.operation == "ADD":
                self.outputs[0].input_value = (self.inputs[0].input_value + self.inputs[1].input_value)
            elif self.operation == "SUB":
                self.outputs[0].input_value = (self.inputs[0].input_value - self.inputs[1].input_value)
            elif self.operation == "MUL":
                self.outputs[0].input_value = (self.inputs[0].input_value * self.inputs[1].input_value)
            elif self.operation == "DIV":
                if self.inputs[1].input_value == 0.0:
                    import sys
                    self.outputs[0].input_value = 0.0
                else:
                    self.outputs[0].input_value = (self.inputs[0].input_value / self.inputs[1].input_value)
            elif self.operation == "GREATER":
                self.outputs[0].hide = True
                self.outputs[1].hide = False
                self.inputs[1].name = "Threshold"
                self.outputs[1].input_value = (self.inputs[0].input_value > self.inputs[1].input_value)
            elif self.operation == "LESS":
                self.outputs[0].hide = True
                self.outputs[1].hide = False
                self.inputs[1].name = "Threshold"
                self.outputs[1].input_value = (self.inputs[0].input_value < self.inputs[1].input_value)
            elif self.operation == "EQUAL":
                self.outputs[0].hide = True
                self.outputs[1].hide = False
                self.outputs[1].input_value = (self.inputs[0].input_value == self.inputs[1].input_value)

    def draw_buttons(self, context, layout):
        if IS_DEBUG:
            if len(self.outputs) > 0:
                layout.label(text=f"input1: {self.inputs[0].input_value}")
                layout.label(text=f"input2: {self.inputs[1].input_value}")
                layout.label(text=f"output1: {self.outputs[0].input_value}")
                layout.label(text=f"output2: {self.outputs[1].input_value}")

        layout.prop(self, "operation", text="")


    def init(self, context):
        self.inputs.new(CntSocketTypes.Float, "Float")
        self.inputs.new(CntSocketTypes.Float, "Float")
        self.outputs.new(CntSocketTypes.Float, "Float")
        out2 = self.outputs.new(CntSocketTypes.Bool, "Bool")
        out2.hide = True
        super().init(context)
        self.inputs[0].display_shape = VERSATILE_SOCKET_SHAPE
        self.inputs[1].display_shape = VERSATILE_SOCKET_SHAPE
        self.outputs[0].display_shape = VERSATILE_SOCKET_SHAPE
        self.outputs[1].display_shape = VERSATILE_SOCKET_SHAPE

        #self.outputs[0].is_constant = True

    def socket_update(self, socket):
        if not socket.is_output:
            self.operation_update()
        else:
            for link in socket.links:
                link.to_socket.input_value = socket.input_value

    def update(self):
        #ToDO test it
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