import bpy
from bpy.app.handlers import persistent
from .operators import operator_classes
from .node_tree import CustomNodeTree, GroupStringCollectionItem, GroupSocketCollectionItem
from .menus import (ConstantsMenu, InputMenu, GroupMenu, UtilMenu, RealtimeMenu, GeometryMenu, menu_draw)
from .operators import NODE_OT_my_group_tab
from ..base.global_data import Data
# attention: the order matters
import_classes_ = [GroupStringCollectionItem, GroupSocketCollectionItem, ConstantsMenu, InputMenu, GroupMenu, UtilMenu,
                   RealtimeMenu, GeometryMenu, CustomNodeTree]
addon_keymaps = []

@persistent
def load_blend_file_job(file_name):
    for group in bpy.data.node_groups:
        for node in group.nodes:
            if hasattr(node, "refresh"):
                node.refresh()

def register_keymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc:
        km = kc.keymaps.new(name="Node Editor", space_type='NODE_EDITOR')
        kmi = km.keymap_items.new(
            NODE_OT_my_group_tab.bl_idname,
            'TAB', 'PRESS'
        )
        addon_keymaps.append((km, kmi))


def unregister_keymap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    for o_class in operator_classes:
        bpy.utils.register_class(o_class)

    register_keymap()
    # bpy.types.NODE_MT_add.append(draw_add_menu)
    bpy.types.NODE_MT_context_menu.append(menu_draw)
    for cls in import_classes_:
        bpy.utils.register_class(cls)
    bpy.app.handlers.load_post.append(load_blend_file_job)

def unregister():
    bpy.app.handlers.load_post.remove(load_blend_file_job)
    #keys = list(Data.uuid_message_bus.keys())
    #for key in keys:
    #    bpy.msgbus.clear_by_owner(Data.uuid_message_bus[key])
    #    del Data.uuid_message_bus[key]
    #keys = list(Data.uuid_handler.keys())
    #for key in keys:
    #    bpy.app.handlers.frame_change_pre.remove(Data.uuid_handler[key].frame_change_handler)
    #    del Data.uuid_handler[key]
    unregister_keymap()
    for cls in reversed(import_classes_):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(e)
    for o_class in reversed(operator_classes):
        try:
            bpy.utils.unregister_class(o_class)
        except Exception as e:
            print(e)
    bpy.types.NODE_MT_context_menu.remove(menu_draw)
    # bpy.types.NODE_MT_add.remove(draw_add_menu)
