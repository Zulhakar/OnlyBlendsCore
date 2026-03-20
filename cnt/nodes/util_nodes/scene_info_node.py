import bpy
import uuid
from ..basic_nodes import ConstantNodeCnt
from ...base.constants import CntSocketTypes
from ...base.global_data import Data


def update_fps(*args):
    self = args[0]
    self.outputs[1].input_value = bpy.data.scenes["Scene"].render.fps


class SceneInfoNodeCnt(ConstantNodeCnt):
    bl_label = "Scene Info"
    bl_icon = 'SCENE_DATA'
    uuid_msg_bus: bpy.props.StringProperty()

    def init(self, context):
        self.outputs.new(CntSocketTypes.Integer, "Current Frame")
        self.outputs.new(CntSocketTypes.Integer, "FPS")
        self.uuid_msg_bus = str(uuid.uuid4()).replace("-", "")
        self.subscribe_msg_bus()
        super().init(context)

    def subscribe_msg_bus(self):
        Data.uuid_handler[self.uuid_msg_bus] = self
        bpy.app.handlers.frame_change_pre.append(Data.uuid_handler[self.uuid_msg_bus].frame_change_handler)
        msg_bus_obj = object()
        Data.uuid_message_bus[self.uuid_msg_bus] = msg_bus_obj
        bpy.msgbus.subscribe_rna(
            key=bpy.data.scenes["Scene"].render.path_resolve("fps", False),
            #key=(bpy.types.Scene, "frame_current"),
            owner=msg_bus_obj,
            args=(self,),
            notify=update_fps,
            options={'PERSISTENT'}
        )
        update_fps(self)
        self.frame_change_handler(None, None)

    def frame_change_handler(self, context, scene):
        self.outputs[0].input_value = bpy.context.scene.frame_current

    def free(self):
        super().free()
        bpy.msgbus.clear_by_owner(Data.uuid_message_bus[self.uuid_msg_bus])
        del Data.uuid_message_bus[self.uuid_msg_bus]
        bpy.app.handlers.frame_change_pre.remove(Data.uuid_handler[self.uuid_msg_bus].frame_change_handler)
        del Data.uuid_handler[self.uuid_msg_bus]

    def refresh(self):
        self.log("refresh")
        self.subscribe_msg_bus()

    def socket_update(self, socket):
        if socket.is_output:
            for link in socket.links:
                link.to_socket.input_value = socket.input_value