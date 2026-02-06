import bpy

from ..base.constants import MAKE_GROUP_OT_IDNAME
from ..base.helper import change_socket_shape
from ...config import OB_TREE_TYPE

def create_child_node_tree(old_tree, selected):
    new_tree = bpy.data.node_groups.new(
        "Custom Node",
        OB_TREE_TYPE
    )
    input_node = new_tree.nodes.new("NodeGroupInput")
    output_node = new_tree.nodes.new("NodeGroupOutput")

    min_x = 10000000000
    min_y = 10000000000
    max_x = -100000000000
    max_y = -100000000000
    new_names = {}
    for node in selected:
        new = new_tree.nodes.new(node.bl_idname)
        new.location = node.location

        # for i, inp_ in enumerate(node.inputs):
        #     new.inputs[i].input_value = inp_.input_value

        new.copy(node)
        if new.bl_idname == "GroupNodeCnt":
            new.target_tree = node.target_tree
        min_x, min_y = min(new.location.x, min_x), min(new.location.y, min_y)
        max_x, max_y = max(new.location.x, max_x), max(new.location.y, max_y)
        # mapping[node] = new
        new_names[node.name] = new.name
    if selected:
        input_node.location = (min_x - 200, min_y)
        output_node.location = (max_x + 200, min_y)
    else:
        input_node.location = (-200, 0)
        output_node.location = (200, 0)
    return new_tree, new_names, input_node, output_node


def get_index_of_socket(node, socket):
    index = 0
    for input in node.inputs:
        if input == socket:
            return index, "input"
        index += 1
    index = 0
    for output in node.outputs:
        if output == socket:
            return index, "output"
        index += 1

def get_node_by_name(tree, name):
    for node in tree.nodes:
        if node.name == name:
            return node
    return None


class MakeGroupOperator(bpy.types.Operator):
    bl_idname = MAKE_GROUP_OT_IDNAME
    bl_label = "Make Group"
    bl_description = "Create a group from selected nodes"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == 'NODE_EDITOR'
                and space.node_tree
                and space.node_tree.bl_idname == OB_TREE_TYPE)

    def execute(self, context):
        old_tree = context.space_data.node_tree
        selected = [n for n in old_tree.nodes if n.select]

        if not selected:
            self.report({'WARNING'}, "No nodes selected")
            return {'CANCELLED'}

        new_tree, new_names_dict, new_input_node, new_output_node = create_child_node_tree(old_tree, selected)

        group_node = old_tree.nodes.new("GroupNodeCnt")
        group_node.node_tree = new_tree
        group_node.target_tree = new_tree
        group_node.parent_node_tree = bpy.data.node_groups[old_tree.name]
        group_node.location = selected[0].location

        new_output_node.parent = group_node
        # new_output_node["parent_group_node"] = bpy.props.PointerProperty(type=bpy.types.Node)
        # new_output_node.parent_group_node = group_node
        new_tree.parent = old_tree
        group_node.group_input_node = new_input_node.name
        group_node.group_output_node = new_output_node.name

        old_tree_new_link_list = []
        group_input_socket_index = 0
        group_output_socket_index = 0
        for link in old_tree.links:
            if link.from_node not in selected and link.to_node in selected:
                new_sock = new_tree.interface.new_socket(link.to_socket.bl_label, socket_type=link.to_socket.bl_idname)

                # new_sock2 = group_node.inputs.new(link.to_socket.bl_idname, link.from_socket.bl_label)
                old_tree_new_link_list.append((group_node.inputs[group_input_socket_index], link.from_socket))

                #group_node.socket_update_disabled = True
                #group_node.inputs[group_input_socket_index].input_value = link.from_socket.input_value
                #new_input_node.outputs[group_input_socket_index].input_value = link.from_socket.input_value
                #group_node.socket_update_disabled = False

                tmp_node = get_node_by_name(new_tree, new_names_dict[link.to_node.name])

                new_tree.links.new(new_input_node.outputs[group_input_socket_index],
                                   tmp_node.inputs[
                                       get_index_of_socket(link.to_node, link.to_socket)[0]]).is_valid = True
                new_input_node.outputs[group_input_socket_index].input_value = link.from_socket.input_value
                tmp_node.inputs[get_index_of_socket(link.to_node, link.to_socket)[0]].input_value = link.from_socket.input_value

                group_input_socket_index += 1


            elif link.to_node not in selected and link.from_node in selected:
                new_sock = new_tree.interface.new_socket(link.to_socket.bl_label, socket_type=link.to_socket.bl_idname,
                                                         in_out="OUTPUT")

                #new_sock2 = group_node.outputs.new(link.to_socket.bl_idname, link.to_socket.bl_label)
                # new_link = old_tree.links.new(new_sock2, link.from_socket)
                # new_link_list.append((link.to_socket, new_sock2))
                old_tree_new_link_list.append((group_node.outputs[group_output_socket_index], link.to_socket))


                tmp_node = get_node_by_name(new_tree, new_names_dict[link.from_node.name])
                new_tree.links.new(tmp_node.outputs[
                                       get_index_of_socket(link.from_node, link.from_socket)[0]],
                                   new_output_node.inputs[
                                       get_index_of_socket(link.to_node, link.to_socket)[0]]).is_valid = True
                group_output_socket_index += 1

            elif link.to_node in selected and link.from_node in selected:
                new_tree.links.new(get_node_by_name(new_tree, new_names_dict[link.from_node.name]).outputs[
                                       get_index_of_socket(link.from_node, link.from_socket)[0]],
                                   get_node_by_name(new_tree, new_names_dict[link.to_node.name]).inputs[
                                       get_index_of_socket(link.to_node, link.to_socket)[0]]).is_valid = True

        for link_tupel in old_tree_new_link_list:
            old_tree.links.new(link_tupel[0], link_tupel[1]).is_valid = True

        change_socket_shape(new_input_node)
        change_socket_shape(new_output_node)
        change_socket_shape(group_node)

        for input in new_output_node.inputs[:-1]:
            input.group_node_tree_name = old_tree.name
            input.group_node_name = group_node.name

        group_name_string = new_tree.group_node_list.add()
        group_name_string.value = group_node.name

        for node in selected:
            old_tree.nodes.remove(node)

        return {'FINISHED'}


class NODE_OT_my_group_tab(bpy.types.Operator):
    bl_idname = "node.my_group_tab"
    bl_label = "Enter/Exit Group"
    bl_description = "Toggle entering/exiting a custom group node with Tab"

    @classmethod
    def poll(cls, context):
        if context.area.type != 'NODE_EDITOR':
            return False

        tree = context.space_data.node_tree
        if not tree:
            return False
        return tree.bl_idname == OB_TREE_TYPE

    def execute(self, context):
        space = context.space_data
        tree = space.node_tree
        # go into selected
        group_nodes = [
            n for n in tree.nodes
            if n.select and n.bl_idname == "GroupNodeCnt"
        ]
        if group_nodes:
            node = group_nodes[0]
            inner = node.target_tree
            if inner:
                space.node_tree = inner
                return {'FINISHED'}

        # go out to parent if nothing is selected
        if hasattr(tree, "parent") and tree.parent:
            space.node_tree = tree.parent
            return {'FINISHED'}

        return {'CANCELLED'}


class MY_MT_add_interface(bpy.types.Menu):
    bl_idname = "MY_MT_add_interface"
    bl_label = "Add"
    def draw(self, context):
        layout = self.layout
        layout.operator("my_interface.add_socket", text="Input").in_out = 'INPUT'
        layout.operator("my_interface.add_socket", text="Output").in_out = 'OUTPUT'


class MY_OT_AddSocket(bpy.types.Operator):
    bl_idname = "my_interface.add_socket"
    bl_label = "Add Interface Socket"
    in_out: bpy.props.EnumProperty(
        items=[
            ('INPUT', "Input", ""),
            ('OUTPUT', "Output", "")
        ]
    )

    def execute(self, context):
        tree = context.space_data.node_tree
        tree.interface.new_socket(
            name="Socket",
            socket_type="NodeSocketFloatCnt",
            in_out=self.in_out,
        )
        for node in tree.nodes:
            if node.bl_idname == "NodeGroupOutput" or node.bl_idname == "NodeGroupInput":
                change_socket_shape(node)
        return {'FINISHED'}


class MY_OT_RemoveSelected(bpy.types.Operator):
    bl_idname = "my_interface.remove_selected"
    bl_label = "Remove Selected Interface Item"

    def execute(self, context):
        tree = context.space_data.node_tree
        idx = tree.interface.active_index
        if len(tree.interface.items_tree) > idx:
            in_out = tree.interface.items_tree[idx].in_out
            num_outputs = 0
            for interface in tree.interface.items_tree:
                if interface.in_out == "OUTPUT":
                    num_outputs += 1
            if 0 <= idx < len(tree.interface.items_tree):
                tree.interface.remove(tree.interface.items_tree[idx])
                if in_out == "INPUT":
                    for node in tree.get_parent_group_nodes():
                        i = idx - num_outputs
                        if len(node.inputs) > i:
                            node.inputs.remove(node.inputs[i])
                elif in_out == "OUTPUT":
                    for node in tree.get_parent_group_nodes():
                        if len(node.outputs) > idx:
                            node.outputs.remove(node.outputs[idx])
                return {'FINISHED'}
        return {'FINISHED'}


def get_group_input(node_tree):
    inputs = []
    for node in node_tree.nodes:
        if node.bl_idname == 'NodeGroupInput':
            inputs.append(node)
    return inputs

class CUSTOM_UL_items2(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item.in_out == "INPUT":
            split = layout.split(factor=0.2)
            col = item.draw_color(context, None)
            split.template_node_socket(color=col)
            split2 = split.split(factor=0.5)
            split2.label(text=item.name)
            split2.label(text="")
            # split2.template_node_socket(color=(0.0, 0.0, 0.0, 0.0))
        else:
            split = layout.split(factor=0.2)
            col = item.draw_color(context, None)
            # split.template_node_socket(color=(0.0, 0.0, 0.0, 0.0))
            split.label(text="")
            split2 = split.split(factor=0.5)
            split2.label(text=item.name)
            split2.template_node_socket(color=col)



class NODE_PT_Sound_Group_Sockets(bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Group Sockets"
    bl_category = "Group"

    # bl_idname = "NODE_PT_Sound_Group_Sockets"

    @classmethod
    def poll(cls, context):
        return (
                context.space_data is not None and
                context.space_data.tree_type == OB_TREE_TYPE and
                context.space_data.node_tree is not None and
                context.space_data.edit_tree is not None
        )

    def draw(self, context):
        layout = self.layout
        tree = context.space_data.node_tree
        # --- Row: List + Buttons ---
        row = layout.row()
        row.template_list(
            "CUSTOM_UL_items2",  # Blender’s builtin UIList
            "interface",  # unique ID
            tree.interface,
            "items_tree",
            tree.interface,
            "active_index",
            rows=6,
        )

        # --- Buttons ---
        col = row.column(align=True)
        col.menu("MY_MT_add_interface", icon="ADD", text="")
        col.operator("my_interface.remove_selected", icon="REMOVE", text="")

        # --- Details for selected item ---
        idx = tree.interface.active_index
        interface_sockets = tree.interface.items_tree

        if 0 <= idx < len(interface_sockets):
            interface_socket = interface_sockets[idx]

            if interface_socket.item_type == 'SOCKET':
                split = layout.split(factor=0.9)
                split.prop(interface_socket, "name", text="Name")
                split.label(text="")
                col = interface_socket.draw_color(context, None)
                split2 = layout.split(factor=0.9)
                if hasattr(interface_socket, "cnt_socket_type"):
                    split2.prop(interface_socket, "cnt_socket_type", text="Type")
                    split2.template_node_socket(color=col)


operator_classes = (CUSTOM_UL_items2, NODE_OT_my_group_tab, MakeGroupOperator, MY_OT_AddSocket, NODE_PT_Sound_Group_Sockets,
                    MY_MT_add_interface, MY_OT_RemoveSelected)
