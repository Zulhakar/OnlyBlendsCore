import bpy
from ..basic_nodes import ConstantNodeCnt
from ...base.global_data import Data
import uuid


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

    def __add_input_sockets(self, modifier):
        # TODO: check if group input exits or check interface
        group_input = get_group_input(self.node_tree)[0]
        self.inputs.clear()
        for i, socket in enumerate(group_input.outputs):
            # skip virtual / non-controllable sockets (e.g. the Geometry input)
            if socket.bl_idname in ('NodeSocketVirtual', 'NodeSocketGeometry',
                                    'NodeSocketMatrix', 'NodeSocketClosure',
                                    'NodeSocketBundle'):
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
            else:
                # TODO test different blender versions
                self.inputs.new(socket.bl_idname, socket.name)

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
            self.__add_input_sockets(modifier)
            self.__add_socket_outputs(modifier)
            self.subscribe_to_interface()

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
