import bpy
from ..basic_nodes import ConstantNodeCnt
from ....config import IS_DEBUG, CntSocketTypes, VERSATILE_SOCKET_SHAPE, cnt_sockets_list


class RealtimeValueNode(ConstantNodeCnt):
    '''Like a Switch Node but without the False Value so that the last value is stored, this is useful for gamepad buttons'''
    bl_label = "Realtime Value"
    bl_icon = 'PLUGIN'

    input_type: bpy.props.EnumProperty(  # type: ignore
        name="Socket Type"
        , items=cnt_sockets_list
        , default=CntSocketTypes.Float
        , update=lambda self, context: self.input_update())


    def input_update(self):
        output_socket = self.outputs[0]
        for socket in self.outputs:
            socket.hide = True
            if socket.bl_idname == self.input_type:
                output_socket = socket
                output_socket.hide = False
        # if self.input_type == CntSocketTypes.Bool:
        #    out_sock.is_constant = True
        for socket in self.inputs:
            if socket.bl_idname == self.input_type and (socket.name == "True"):
                socket.hide = False
                if self.inputs[0].input_value and socket.name == "True":
                    output_socket.input_value = socket.input_value
            else:
                if socket.name == "True":
                    socket.hide = True

    def draw_buttons(self, context, layout):
        layout.prop(self, "input_type", text="")

    def init(self, context):
        self.inputs.new(CntSocketTypes.Bool, "Switch")
        for socket_type in cnt_sockets_list:

            s1 = self.inputs.new(socket_type[0], "True")
            out = self.outputs.new(socket_type[0], "Output")

            if socket_type[0] != CntSocketTypes.Float:
                s1.hide = True
                out.hide = True
        super().init(context)

    def socket_update(self, socket):
        if not socket.is_output:
            self.input_update()
        else:
            for link in socket.links:
                link.to_socket.input_value = socket.input_value

    def copy(self, node):
        super().copy(node)
        # ctrl + V / C crashed with the following line, this is a blender core problem or has to do with inheritance
        # self.input_type = node.input_type
