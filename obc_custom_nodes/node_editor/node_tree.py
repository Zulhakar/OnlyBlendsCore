from typing import Any
import bpy
from ..base.helper import change_socket_shape
from ...config import IS_DEBUG, TREE_ICON, CntSocketTypes, OB_TREE_TYPE, NODE_EDITOR_NAME


class GroupStringCollectionItem(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty()
    name: bpy.props.StringProperty()

class GroupSocketCollectionItem(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    type_name: bpy.props.StringProperty()

class GroupInstanceState(bpy.types.PropertyGroup):
    group_node_name: bpy.props.StringProperty()
    instance_id: bpy.props.StringProperty()
    dirty: bpy.props.BoolProperty(default=False)


def get_group_input_output_nodes(tree):
    all_nodes = []
    for node in tree.nodes:
        if node.bl_idname in {"NodeGroupOutput","NodeGroupInput"}:
            all_nodes.append(node)
    return all_nodes

def change_all_socket_shapes(tree):
    for node in get_group_input_output_nodes(tree):
        change_socket_shape(node)

class CustomNodeTree(bpy.types.NodeTree):
    bl_idname = OB_TREE_TYPE
    bl_label = NODE_EDITOR_NAME
    bl_icon = TREE_ICON
    bl_use_group_interface = False

    parent: bpy.props.PointerProperty(name="Node Tree", type=bpy.types.NodeTree)

    group_node_list: bpy.props.CollectionProperty(type=GroupStringCollectionItem)
    group_node_input_list: bpy.props.CollectionProperty(type=GroupSocketCollectionItem)
    group_node_output_list: bpy.props.CollectionProperty(type=GroupSocketCollectionItem)

    group_instances: bpy.props.CollectionProperty(type=GroupInstanceState)

    was_fired : bpy.props.BoolProperty(default=False)
    re_evaluating2: bpy.props.BoolProperty(default=False)

    def get_or_create_instance(self, group_node):
        for inst in self.group_instances:
            if inst.group_node_name == group_node.name and inst.instance_id == group_node.instance_id:
                return inst
        inst = self.group_instances.add()
        inst.group_node_name = group_node.name
        inst.instance_id = group_node.instance_id
        return inst

    def _evaluate_for_instance(self, group_node):
        # snapshot shared sockets we will touch
        snapshot = {}
        for node in self.nodes:
            if node.bl_idname == 'NodeGroupInput':
                for out in node.outputs:
                    if out.bl_idname != "NodeSocketVirtual":
                        snapshot[(node, out)] = out.input_value
            if node.bl_idname == 'NodeGroupOutput':
                for inp in node.inputs:
                    if inp.bl_idname != "NodeSocketVirtual":
                        snapshot[(node, inp)] = inp.input_value

        try:
            # push this instance's inputs only
            for node in self.nodes:
                if node.bl_idname != 'NodeGroupInput':
                    continue
                for i, inp in enumerate(group_node.inputs):
                    if i >= len(node.outputs): continue
                    inner_out = node.outputs[i]
                    inner_out.input_value = inp.input_value
                    for link in inner_out.links:
                        link.to_socket.input_value = link.from_socket.input_value

            # evaluate
            self.validate_links()
            self.handle_socks(self._get_interface_sockets(True), True)
            self.handle_socks(self._get_interface_sockets(False), False)

            # pull outputs back to this instance only
            for node in self.nodes:
                if node.bl_idname != 'NodeGroupOutput':
                    continue
                for i, out_sock in enumerate(node.inputs):
                    if i >= len(group_node.outputs): continue
                    group_node.outputs[i].input_value = out_sock.input_value
                    for link in group_node.outputs[i].links:
                        link.to_socket.input_value = link.from_socket.input_value
        finally:
            # restore shared tree to its previous state
            for (node, sock), val in snapshot.items():
                sock.input_value = val

    def update_instance(self, group_node):
        inst = self.get_or_create_instance(group_node)
        inst.dirty = True
        self._evaluate_for_instance(group_node)
        inst.dirty = False

    def get_parent_group_nodes(self):
        nodes = []
        if self.parent:
            for node in self.parent.nodes:
                if node.bl_idname == "GroupNodeCnt" and node.target_tree == self:
                    nodes.append(node)
        return nodes

    def get_owner_node(self):
        for n in self.parent.nodes if self.parent else []:
            if n.bl_idname == "GroupNodeCnt" and n.target_tree == self:
                return n
        return None

    def get_instance(self, group_node):
        for inst in self.group_instances:
            if inst.group_node_name == group_node.name and inst.instance_id == group_node.instance_id:
                return inst
        return None


    def _get_interface_sockets(self, is_input):
        return [i for i in self.interface.items_tree if hasattr(i, "in_out") and ((i.in_out=='INPUT')==is_input)]

    def update(self):
        if IS_DEBUG:
            print("update Node Tree:", self.name)
        self.validate_links()
        for node in self.nodes:
            if node.bl_idname == "GroupNodeCnt":
                node.parent_node_tree = self
            elif node.bl_idname == "NodeGroupOutput":
                for inp_sock in node.inputs:
                    if inp_sock.bl_idname != "NodeSocketVirtual":
                        if self.parent:
                            inp_sock.selected_node_group_name = self.parent.name
                        inp_sock.node_group_name = self.name

        # sync sockets
        self.handle_socks(self._get_interface_sockets(True), True)
        self.handle_socks(self._get_interface_sockets(False), False)

        # push to all owners individually
        for owner in self.get_parent_group_nodes():
            inst = self.get_or_create_instance(owner)
            if inst.dirty:
                self._evaluate_for_instance(owner, inst)

    def validate_links(self):
        for link in list(self.links):
            if link.to_socket.bl_idname == link.from_socket.bl_idname:
                link.is_valid = True
            elif link.to_socket.bl_idname == CntSocketTypes.Float and link.from_socket.bl_idname == CntSocketTypes.Integer:
                link.is_valid = True
            elif link.to_socket.bl_idname == CntSocketTypes.Integer and link.from_socket.bl_idname == CntSocketTypes.Float:
                link.is_valid = True
            if not link.is_valid:
                self.links.remove(link)
    def handle_socks(self, sockets: list[Any], are_inputs=True):
        if IS_DEBUG:
            print("handle_socks Node Tree:", self.name)
        coll = self.group_node_input_list if are_inputs else self.group_node_output_list
        sockets_tmp = [s for s in sockets if s.bl_socket_idname != "NodeSocketVirtual"]

        if len(sockets_tmp) == 0:
            self.sync_sockets(sockets, are_inputs)
            return

        # update existing items by order, then add/remove
        for i, coll_item in enumerate(list(coll)):
            if i < len(sockets_tmp):
                s = sockets_tmp[i]
                if coll_item.type_name != s.bl_socket_idname or coll_item.name != s.name:
                    coll_item.type_name = s.bl_socket_idname
                    coll_item.name = s.name
                    self.sync_sockets(sockets, are_inputs)
                    change_all_socket_shapes(self)

        # add new
        existing_ids = {i.id for i in coll}
        for s in sockets_tmp:
            if s.identifier not in existing_ids:
                new_item = coll.add()
                new_item.id = s.identifier
                new_item.name = s.name
                new_item.type_name = s.bl_socket_idname

        # remove old
        ids = {s.identifier for s in sockets_tmp}
        for i in range(len(coll)-1, -1, -1):
            if coll[i].id not in ids:
                coll.remove(i)

        self.sync_sockets(sockets, are_inputs)
        change_all_socket_shapes(self)

    def sync_sockets(self, sockets, is_input=True):
        if IS_DEBUG:
            print("sync_sockets Node Tree:", self.name)
        owner = self.get_owner_node()
        if not owner:
            return

        # never clear – keep existing links alive
        target = owner.inputs if is_input else owner.outputs
        # adjust count only
        while len(target) < len([s for s in sockets if s.bl_socket_idname != "NodeSocketVirtual"]):
            s = [s for s in sockets if s.bl_socket_idname != "NodeSocketVirtual"][len(target)]
            target.new(s.bl_socket_idname, s.name)
            change_socket_shape(owner)
        while len(target) > len([s for s in sockets if s.bl_socket_idname != "NodeSocketVirtual"]):
            target.remove(target[-1])

        for i, s in enumerate([s for s in sockets if s.bl_socket_idname != "NodeSocketVirtual"]):
            if i >= len(target):
                break
            if target[i].name != s.name or target[i].bl_idname != s.bl_socket_idname:
                # rename / type change – recreate this socket only
                # Blender does not allow type change in place, so recreate
                old_links = [l for l in target[i].links]
                target.remove(target[i])
                new_sock = target.new(s.bl_socket_idname, s.name)
                change_socket_shape(owner)
                # links are lost – they will be rebuilt by the UI
            # no value write here