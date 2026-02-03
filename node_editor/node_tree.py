from typing import Any
import bpy
from ..core.helper import change_socket_shape
from ..core.constants import IS_DEBUG, TREE_ICON, CntSocketTypes

class GroupStringCollectionItem(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty()
    name: bpy.props.StringProperty()

class GroupSocketCollectionItem(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    type_name: bpy.props.StringProperty()


def get_group_input_output_nodes(tree):
    all_nodes = []
    for node in tree.nodes:
        if node.bl_idname == "NodeGroupOutput":
            all_nodes.append(node)
        elif node.bl_idname == "NodeGroupInput":
            all_nodes.append(node)
    return all_nodes

def change_all_socket_shapes(tree):
    nodes = get_group_input_output_nodes(tree)
    for node in nodes:
        change_socket_shape(node)

class CustomNodeTree(bpy.types.NodeTree):
    bl_label = "Custom Nodes"
    bl_icon = TREE_ICON
    bl_use_group_interface = False
    parent: bpy.props.PointerProperty(
        name="Node Tree",
        type=bpy.types.NodeTree
    )

    group_node_list: bpy.props.CollectionProperty(type=GroupStringCollectionItem)
    group_node_input_list: bpy.props.CollectionProperty(type=GroupSocketCollectionItem)
    group_node_output_list: bpy.props.CollectionProperty(type=GroupSocketCollectionItem)

    was_fired : bpy.props.BoolProperty(default=False)

    def get_parent_group_nodes(self):
        #error if there are more than one TODO
        parent_group_nodes = []
        if self.parent:
            for node in self.parent.nodes:
                if node.bl_idname == "GroupNodeCnt":
                    parent_group_nodes.append(node)
        return parent_group_nodes

    def interface_update(self, context):
        if IS_DEBUG:
            print("interface update")

    def update(self):
        if IS_DEBUG:
            print("update Node Tree:", self.name)
        self.validate_links()

        for node in self.nodes:
            if node.bl_idname == "GroupNodeCnt":
                node.parent_node_tree = self
                is_in_list = False
                for key, value in self.group_node_list.items():
                    if value.name == node.name:
                        is_in_list = True
                if not is_in_list:
                    new_group_node_item = self.group_node_list.add()
                    new_group_node_item.name = node.name
                    new_group_node_item.id = node.name
            elif node.bl_idname == "NodeGroupOutput":
                #add reference to socket for group output update
                for inp_sock in node.inputs:
                    if inp_sock.bl_idname != "NodeSocketVirtual":
                        if self.parent:
                            inp_sock.selected_node_group_name = self.parent.name
                        inp_sock.node_group_name = self.name

        inputs = []
        outputs = []
        for interface in self.interface.items_tree:
            if hasattr(interface, "in_out"):
                if interface.in_out == 'INPUT':
                    inputs.append(interface)
                elif interface.in_out == 'OUTPUT':
                    outputs.append(interface)
        

        self.handle_socks(inputs, True)
        self.handle_socks(outputs, False)

    def validate_links(self):
        for link in list(self.links):
            if link.to_socket.bl_idname == link.from_socket.bl_idname:
                link.is_valid = True
            elif link.to_socket.bl_idname == CntSocketTypes.Float and link.from_socket.bl_idname == CntSocketTypes.Integer:
                link.is_valid = True
            elif link.to_socket.bl_idname == CntSocketTypes.Integer and link.from_socket.bl_idname == CntSocketTypes.Float:
                link.is_valid = True
            if not link.is_valid:
                if IS_DEBUG:
                    print("invalid link removed:", link)
                    print(link.to_socket.bl_idname, link.from_socket.bl_idname)
                    print(link.to_node.name, link.from_node.name)
                self.links.remove(link)

    def handle_socks(self, sockets: list[Any], are_inputs=True):
        if IS_DEBUG:
            print("handle_socks Node Tree:", self.name)
        ids_collection = set()
        sockets_collection = []
        if are_inputs:
            group_node_in_out_list = self.group_node_input_list
        else:
            group_node_in_out_list = self.group_node_output_list
        if len(sockets) == 0:
            #group_node_in_out_list.clear()
            self.sync_sockets(sockets, are_inputs)
        else:
            for item in group_node_in_out_list:
                ids_collection.add(item.id)
                sockets_collection.append(item)
            ids = set()
            sockets_tmp = []
            for item in sockets:
                if item.bl_socket_idname != "NodeSocketVirtual":
                    ids.add(item.identifier)
                    sockets_tmp.append(item)
            removed_ids = ids_collection - ids
            added_ids = ids - ids_collection
            if len(removed_ids) == 0 and len(added_ids) == 0:
                for i, value in enumerate(sockets_collection):
                    if sockets_collection[i].type_name != sockets_tmp[i].bl_socket_idname:
                        self.sync_sockets(sockets, are_inputs)
                        change_all_socket_shapes(self)
                        sockets_collection[i].type_name = sockets_tmp[i].bl_socket_idname
                    if sockets_collection[i].name != sockets_tmp[i].name:
                        sockets_collection[i].name = sockets_tmp[i].name
                        self.sync_sockets(sockets, are_inputs)
                        change_all_socket_shapes(self)

            if len(removed_ids) > 0:
                remove_sockets = []
                for i, value in enumerate(sockets_tmp):
                    if sockets_collection[i].id in removed_ids:
                        remove_sockets.append(i)
                for remove_socket in remove_sockets:
                    group_node_in_out_list.remove(remove_socket)
                self.sync_sockets(sockets, are_inputs)
                change_all_socket_shapes(self)
            if len(added_ids) > 0:
                for i, value in enumerate(sockets_tmp):
                    if sockets_tmp[i].identifier in added_ids:
                        new_item = group_node_in_out_list.add()
                        new_item.id = sockets_tmp[i].identifier
                        new_item.name = sockets_tmp[i].name
                        new_item.type_name = sockets_tmp[i].bl_socket_idname
                self.sync_sockets(sockets, are_inputs)
                change_all_socket_shapes(self)

    def sync_sockets(self, sockets, is_input=True):
        if IS_DEBUG:
            print("sync_sockets Node Tree:", self.name)
        for key, value in bpy.data.node_groups.items():
            for node_ in value.nodes:
                if node_.bl_idname == "GroupNodeCnt":
                    if node_.target_tree == self:
                        if is_input:
                            node_.inputs.clear()
                            for old_output in sockets:
                                if old_output.bl_socket_idname != "NodeSocketVirtual":
                                    old_output.selected_node_group_name = node_.parent_node_tree.name
                                    old_output.node_group_name = node_.name
                                    node_.inputs.new(old_output.bl_socket_idname, old_output.name)
                                    change_socket_shape(node_)
                        else:
                            node_.outputs.clear()
                            for old_input in sockets:
                                if old_input.bl_socket_idname != "NodeSocketVirtual":
                                    old_input.selected_node_group_name = node_.parent_node_tree.name
                                    old_input.node_group_name = node_.name
                                    node_.outputs.new(old_input.bl_socket_idname, old_input.name)
                                    change_socket_shape(node_)
