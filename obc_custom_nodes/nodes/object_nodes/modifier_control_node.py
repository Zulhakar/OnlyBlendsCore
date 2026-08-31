import bpy
from bpy.app.handlers import persistent
import uuid
from ..basic_nodes import ConstantNodeCnt
from ...base.global_data import Data
from ...sockets.basic_sockets import NodeSocketCnt

_active_nodes = set()
_depsgraph_syncing = False
_initial_scan_done = False


def _register_node(node):
    _active_nodes.add(node)


def _unregister_node(node):
    _active_nodes.discard(node)


def _rescan_active_nodes():
    """(Re)build the registry from the current blend file."""
    _active_nodes.clear()
    for tree in bpy.data.node_groups:
        for node in tree.nodes:
            if node.bl_idname == "ModifierControlNode":
                if node.obj and node.modifier_name and node.node_tree:
                    _active_nodes.add(node)


def _depsgraph_sync():
    global _depsgraph_syncing, _initial_scan_done
    if _depsgraph_syncing:
        return
    # bpy.data is a restricted dummy during register(), so the first scan is
    # deferred to the first depsgraph update (by then bpy.data is available).
    if not _initial_scan_done:
        _rescan_active_nodes()
        _initial_scan_done = True
    if not _active_nodes:  # gate 1: nothing bound -> return immediately
        return
    _depsgraph_syncing = True
    try:
        for node in list(_active_nodes):
            try:
                if node._modifier_differs():  # gate 2: only act when values differ
                    node._pull_from_modifier()
            except Exception:
                pass
    finally:
        _depsgraph_syncing = False


@persistent
def _depsgraph_sync_handler(dg):
    _depsgraph_sync()


@persistent
def _on_file_load(dg):
    _rescan_active_nodes()


def register_depsgraph_handler():
    if _depsgraph_sync_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_depsgraph_sync_handler)
    if _on_file_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_file_load)
    # NOTE: no scan here – bpy.data is restricted during register().
    # The first scan is deferred to the first depsgraph update (see above).


def unregister_depsgraph_handler():
    global _initial_scan_done
    if _depsgraph_sync_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_depsgraph_sync_handler)
    if _on_file_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_file_load)
    _active_nodes.clear()
    _initial_scan_done = False


def node_tree_interface_changed(*args):
    self = args[0]
    if self:
        self.update_node_tree(None)


def find_objects_of_node_group(target_node_group_name):
    found_objects = []
    for obj in bpy.data.objects:
        for mod in obj.modifiers:
            if mod.type == 'NODES':
                if mod.node_group and mod.node_group.name == target_node_group_name:
                    found_objects.append((obj, mod.name))
                    break
    return found_objects[0]


def get_group_input(node_tree):
    inputs = []
    for node in node_tree.nodes:
        if node.bl_idname == 'NodeGroupInput':
            inputs.append(node)
    return inputs


def get_group_output(node_tree):
    inputs = []
    for node in node_tree.nodes:
        if node.bl_idname == 'NodeGroupOutput':
            inputs.append(node)
    return inputs


class ModifierControlNode(ConstantNodeCnt):
    '''This Node can control the Group Inputs of a Geometry Node Modifier'''
    bl_label = "Modifier Control"

    node_tree: bpy.props.PointerProperty(
        name="Group",
        type=bpy.types.NodeTree,
        poll=lambda self, tree: (tree.bl_idname == "GeometryNodeTree" and tree.is_modifier),
        update=lambda self, context: self.update_node_tree(context)
    )

    obj: bpy.props.PointerProperty(
        type=bpy.types.Object
    )

    modifier_name: bpy.props.StringProperty()

    uuid_msg_bus: bpy.props.StringProperty()

    def _get_name_to_id(self):
        name_to_id = {}
        if self.node_tree:
            for item in self.node_tree.interface.items_tree:
                if getattr(item, "in_out", None) == "INPUT":
                    name_to_id[item.name] = item.identifier
        return name_to_id

    def _init_inputs_from_modifier(self, modifier):
        """Initialization: read the modifier's current input values into the sockets."""
        if modifier is None:
            return
        name_to_id = self._get_name_to_id()

        for socket in self.inputs:
            identifier = name_to_id.get(socket.name)
            if identifier is None:
                continue

            if bpy.app.version < (5, 2, 0):
                val = modifier[identifier]
            else:
                attr = getattr(modifier.properties.inputs, identifier)
                val = attr.value if hasattr(attr, "value") else None
            if val:
                if hasattr(socket, "disable_socket_update"):
                    socket.disable_socket_update = True
                if hasattr(socket, "input_value"):
                    socket.input_value = val
                elif hasattr(socket, "default_value"):
                    socket.default_value = val
                if hasattr(socket, "disable_socket_update"):
                    socket.disable_socket_update = False

    def _modifier_differs(self):
        """Gate 2: cheap check whether any unlinked input differs from the modifier."""
        if not self.obj or not self.node_tree:
            return False
        modifier = self.obj.modifiers.get(self.modifier_name)
        if modifier is None:
            return False
        name_to_id = self._get_name_to_id()
        for socket in self.inputs:
            if socket.is_linked:
                continue
            identifier = name_to_id.get(socket.name)
            if identifier is None:
                continue
            try:
                if bpy.app.version < (5, 2, 0):
                    val = modifier[identifier]
                else:
                    val = getattr(modifier.properties.inputs, identifier).value
            except Exception:
                continue
            if hasattr(socket, "input_value"):
                cur = socket.input_value
                if isinstance(val, float) or isinstance(cur, float):
                    if abs(cur - val) > 1e-6:
                        return True
                elif cur != val:
                    return True
            elif hasattr(socket, "default_value"):
                if socket.default_value != val:
                    return True
        return False

    def _pull_from_modifier(self):
        """Modifier -> node: write the modifier's input values into the unlinked sockets."""
        if not self.obj or not self.node_tree:
            return
        modifier = self.obj.modifiers.get(self.modifier_name)
        if modifier is None:
            return
        name_to_id = self._get_name_to_id()
        prev_silent = NodeSocketCnt.silent_updates
        NodeSocketCnt.silent_updates = True
        try:
            for socket in self.inputs:
                if socket.is_linked:
                    continue
                identifier = name_to_id.get(socket.name)
                if identifier is None:
                    continue
                try:
                    if bpy.app.version < (5, 2, 0):
                        val = modifier[identifier]
                    else:
                        val = getattr(modifier.properties.inputs, identifier).value
                except Exception:
                    continue
                if hasattr(socket, "input_value"):
                    cur = socket.input_value
                    if isinstance(val, float) or isinstance(cur, float):
                        if abs(cur - val) > 1e-6:
                            socket.input_value = val
                    elif cur != val:
                        socket.input_value = val
                elif hasattr(socket, "default_value"):
                    if socket.default_value != val:
                        socket.default_value = val
        finally:
            NodeSocketCnt.silent_updates = prev_silent

    def __add_input_sockets(self, modifier):
        # TODO: check if group input exits or check interface
        group_input = get_group_input(self.node_tree)[0]
        self.inputs.clear()
        for i, socket in enumerate(group_input.outputs):
            if socket.bl_idname in ('NodeSocketVirtual'):
                continue
            if socket.bl_idname == 'NodeSocketFloat':
                self.inputs.new('NodeSocketFloatCnt', socket.name)
            elif socket.bl_idname == 'NodeSocketInt':
                self.inputs.new('NodeSocketIntCnt', socket.name)
            elif socket.bl_idname == 'NodeSocketBool':
                self.inputs.new('NodeSocketBoolCnt', socket.name)
            elif socket.bl_idname == 'NodeSocketString':
                self.inputs.new('NodeSocketStringCnt', socket.name)
            elif socket.bl_idname == 'NodeSocketObject':
                self.inputs.new('NodeSocketObjectCnt', socket.name)
            elif socket.bl_idname == 'NodeSocketMenu':
                menu_sock = self.inputs.new('NodeSocketStringCnt', socket.name)
                menu_sock.input_value = socket.default_value
            elif socket.bl_idname == 'NodeSocketSound':
                try:
                    self.inputs.new('NodeSocketSoundObm', socket.name)
                except Exception as e:
                    print("OnlyBlends.Mixer not installed")
                    self.inputs.new('NodeSocketSound', socket.name)
            else:
                # TODO test different blender versions
                self.inputs.new(socket.bl_idname, socket.name)
                #if socket.bl_idname == 'NodeSocketSound':
                #    print(socket.draw_color(modifier, socket.node))

    def __add_socket_outputs(self, modifier):
        group_output = get_group_output(self.node_tree)[0]
        self.outputs.clear()
        for i, socket in enumerate(group_output.inputs):
            if socket.bl_idname == 'NodeSocketGeometry' and i == 0:
                self.outputs.new('NodeSocketObjectCnt', "Object")
            # useless atm
            # else:
            #     if socket.bl_idname == 'NodeSocketFloat':
            #         self.outputs.new('NodeSocketFloatCnt', socket.name)
            #     elif socket.bl_idname == 'NodeSocketInt':
            #         self.outputs.new('NodeSocketIntCnt', socket.name)
            #     elif socket.bl_idname == 'NodeSocketBool':
            #         self.outputs.new('NodeSocketBoolCnt', socket.name)
            #     elif socket.bl_idname == 'NodeSocketString':
            #         self.outputs.new('NodeSocketStringCnt', socket.name)
            #     elif socket.bl_idname == 'NodeSocketObject':
            #         self.outputs.new('NodeSocketObjectCnt', socket.name)
            #     else:
            #         self.outputs.new(socket.bl_idname, socket.name)

    def _push_to_modifier(self):
        if not self.obj or not self.node_tree:
            return
        modifier = self.obj.modifiers[self.modifier_name]

        name_to_id = {}
        for item in self.node_tree.interface.items_tree:
            if getattr(item, "in_out", None) == "INPUT":
                name_to_id[item.name] = item.identifier

        changed = False
        for socket in self.inputs:
            identifier = name_to_id.get(socket.name)
            if identifier is None:
                continue
            try:
                if bpy.app.version < (5, 2, 0):
                    if hasattr(socket, "input_value"):
                        modifier[identifier] = socket.input_value
                    elif hasattr(socket, "default_value"):
                        modifier[identifier] = socket.default_value
                    changed = True
                else:
                    prop = getattr(modifier.properties.inputs, identifier)
                    if hasattr(socket, "input_value"):
                        prop.value = socket.input_value
                    elif hasattr(socket, "default_value"):
                        prop.value = socket.default_value
                    changed = True
            except Exception as e:
                print(e)

        if changed:
            self.obj.update_tag()
            # self.node_tree.interface.active.hide_in_modifier = self.node_tree.interface.active.hide_in_modifier

        for i, out_socket in enumerate(self.outputs):
            if out_socket.bl_idname == 'NodeSocketObjectCnt' and i == 0:
                self.outputs[0].input_value = self.obj

    def init(self, context):
        self.node_tree = None
        self.uuid_msg_bus = str(uuid.uuid4()).replace("-", "")
        Data.uuid_message_bus[self.uuid_msg_bus] = object()
        super().init(context)

    def recompute(self):
        self._push_to_modifier()

    def update_node_tree(self, context):
        print("update_node_tree")
        if self.node_tree:
            self.obj, self.modifier_name = find_objects_of_node_group(self.node_tree.name)
            modifier = self.obj.modifiers[self.modifier_name]
            self.__add_input_sockets(context)
            self.__add_socket_outputs(modifier)
            self._init_inputs_from_modifier(modifier)
            self.subscribe_to_interface()
            _register_node(self)
        else:
            _unregister_node(self)

    def subscribe_to_interface(self):
        if self.uuid_msg_bus in Data.uuid_message_bus.keys():
            bpy.msgbus.clear_by_owner(Data.uuid_message_bus[self.uuid_msg_bus])
        Data.uuid_message_bus[self.uuid_msg_bus] = object()

        bpy.msgbus.subscribe_rna(
            key=self.node_tree.path_resolve("interface", False),
            owner=Data.uuid_message_bus[self.uuid_msg_bus],
            args=(self,),
            notify=node_tree_interface_changed,
            options={'PERSISTENT'}
        )
        for i in range(len(self.node_tree.interface.items_tree)):
            bpy.msgbus.subscribe_rna(
                key=self.node_tree.interface.items_tree[i].path_resolve("socket_type", False),
                # key=(bpy.types.NlaStrip, "frame_end_ui"),
                owner=Data.uuid_message_bus[self.uuid_msg_bus],
                args=(self,),
                notify=node_tree_interface_changed,
                options={'PERSISTENT'}
            )

    def free(self):
        super().free()
        _unregister_node(self)
        if self.uuid_msg_bus in Data.uuid_message_bus.keys():
            bpy.msgbus.clear_by_owner(Data.uuid_message_bus[self.uuid_msg_bus])
            del Data.uuid_message_bus[self.uuid_msg_bus]

    def draw_buttons(self, context, layout):
        layout.prop(self, "node_tree", text="")

    def socket_update(self, socket):
        super().socket_update(socket)
        if not socket.is_output:
            self._push_to_modifier()
        else:
            if hasattr(socket, "input_value"):
                for link in socket.links:
                    link.to_socket.input_value = socket.input_value

    def copy(self, node):
        super().copy(node)