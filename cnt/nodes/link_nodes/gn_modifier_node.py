import bpy
from ..basic_nodes import ConstantNodeCnt
from ...base.helper import get_socket_index


def find_objects_of_node_group(target_node_group_name):
    found_objects = []
    # Iterate through all objects in the current blend file
    for obj in bpy.data.objects:
        # Iterate through all modifiers on the object
        for mod in obj.modifiers:
            # Check if the modifier is a Geometry Nodes modifier ('NODES')
            if mod.type == 'NODES':
                # Check if the node group assigned to the modifier matches the target name
                if mod.node_group and mod.node_group.name == target_node_group_name:
                    found_objects.append((obj, mod.name))
                    # Optional: Break to avoid adding the same object multiple times
                    # if it uses the group in multiple modifiers
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


class GeometryGroupInputCollectionItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    name_in_modifier: bpy.props.StringProperty()
    index: bpy.props.IntProperty()


class ModifierNode(ConstantNodeCnt):
    '''Get Object from Geometry Node Modifier'''
    bl_label = "Modifier Object"

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

    modifier_key_socket_pairs_input: bpy.props.CollectionProperty(type=GeometryGroupInputCollectionItem)

    def update_node_tree(self, context):
        if self.node_tree:
            self.obj, self.modifier_name = find_objects_of_node_group(self.node_tree.name)
            modifier = self.obj.modifiers[self.modifier_name]
            # TODO: check if group input exits or check interface
            group_input = get_group_input(self.node_tree)[0]
            self.inputs.clear()
            for i, socket in enumerate(group_input.outputs):
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
                else:
                    # TODO test different blender versions
                    if (socket.bl_idname != 'NodeSocketGeometry' and socket.bl_idname != 'NodeSocketMatrix'
                            and socket.bl_idname != 'NodeSocketClosure' and socket.bl_idname != 'NodeSocketVirtual'):
                        self.inputs.new(socket.bl_idname, socket.name)

            self.outputs.clear()
            self.outputs.new('NodeSocketObjectCnt', "Object")

            i = 0
            self.modifier_key_socket_pairs_input.clear()
            for key, value in modifier.items():
                if not "_use_attribute" in key and not "_attribute_name" in key:
                    socket = group_input.outputs[i]
                    new_col_item = self.modifier_key_socket_pairs_input.add()
                    new_col_item.name = socket.name
                    new_col_item.name_in_modifier = key
                    new_col_item.index = i
                    i += 1

    def init(self, context):
        self.node_tree = None
        super().init(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "node_tree")

    def socket_update(self, socket):
        super().socket_update(socket)
        if not socket.is_output:
            index = get_socket_index(self.inputs, socket)
            modifier = self.obj.modifiers[self.modifier_name]
            key = self.modifier_key_socket_pairs_input[index].name_in_modifier
            modifier[key] = socket.input_value
            self.node_tree.interface.active.hide_in_modifier = True
            self.node_tree.interface.active.hide_in_modifier = False
            if len(self.outputs) > 0 and self.outputs[0].bl_idname == 'NodeSocketObjectCnt':
                self.outputs[0].input_value = self.obj
                for link in self.outputs[0].links:
                    link.to_socket.input_value = self.outputs[0].input_value
