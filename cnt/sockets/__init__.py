from bpy.utils import register_class, unregister_class
from .basic_sockets import classes as basic_sockets
from .import_socket import NodeSocketImportObc, NodeTreeInterfaceSocketImportObc

basic_sockets.append(NodeSocketImportObc)
basic_sockets.append(NodeTreeInterfaceSocketImportObc)

def register():
    for cls in basic_sockets:
        register_class(cls)


def unregister():
    for cls in reversed(basic_sockets):
        try:
            unregister_class(cls)
        except Exception as e:
            print(e)