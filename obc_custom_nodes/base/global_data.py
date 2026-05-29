import bpy
from bpy.app.handlers import persistent


class Data:
    uuid_message_bus = {}
    uuid_handler = {}
    uuid_operator_class_storage = {}


@persistent
def on_file_load_handler(dummy):
    for key in Data.uuid_message_bus.keys():
        bpy.msgbus.clear_by_owner(Data.uuid_message_bus[key])
    Data.uuid_message_bus.clear()
    Data.uuid_handler.clear()
    Data.uuid_operator_class_storage.clear()


bpy.app.handlers.load_pre.append(on_file_load_handler)
