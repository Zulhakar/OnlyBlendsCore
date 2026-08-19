import bpy
from ...nodes.basic_nodes import NodeCnt
from ...base.helper import get_socket_index, get_parent_node_group
from ....config import OB_TREE_TYPE, IS_DEBUG


class GroupNodeCnt(NodeCnt, bpy.types.NodeCustomGroup):
    bl_label = "Group"
    bl_icon = 'NODETREE'

    target_tree: bpy.props.PointerProperty(
        name="Group",
        type=bpy.types.NodeTree,
        poll=lambda self, tree: (tree.bl_idname == OB_TREE_TYPE and get_parent_node_group(self, tree)),
        update=lambda self, context: self.node_group_tree_update(context)
    )

    parent_node_tree: bpy.props.PointerProperty(
        name="Node Tree",
        type=bpy.types.NodeTree
    )

    group_input_node: bpy.props.StringProperty()
    group_output_node: bpy.props.StringProperty()
    was_fired: bpy.props.BoolProperty(default=False)
    was_fired_internal: bpy.props.BoolProperty(default=False)

    def init(self, context):
        super().init(context)

    def node_group_tree_update(self, context):
        self.log("node_group_tree_update")
        if self.target_tree:
            self.target_tree.parent = self.parent_node_tree
            self.target_tree.group_node_name = self.name

    def draw_buttons(self, context, layout):
        layout.prop(self, "target_tree", text="")

    def socket_update(self, socket):
        if getattr(self, "_updating", False):
            return
        self._updating = True
        try:
            super().socket_update(socket)
            if not socket.is_output:
                if not self.target_tree:
                    return
                old_active = self.target_tree.active_group_node_name
                old_origin = self.target_tree.update_origin_is_input_push

                self.target_tree.active_group_node_name = self.name
                self.target_tree.update_origin_is_input_push = True

                self.socket_update_disabled = True
                try:
                    for node in self.target_tree.nodes:
                        if node.bl_idname == 'NodeGroupInput':
                            for i, inp in enumerate(self.inputs):
                                if i >= len(node.outputs): continue
                                inner_out = node.outputs[i]
                                inner_out.input_value = inp.input_value
                                for link in inner_out.links:
                                    link.to_socket.input_value = link.from_socket.input_value
                            idx = get_socket_index(self.inputs, socket)
                            if idx is not None and idx < len(node.outputs):
                                inner_out = node.outputs[idx]
                                inner_out.input_value = socket.input_value
                                for link in inner_out.links:
                                    link.to_socket.input_value = link.from_socket.input_value
                    if self.target_tree:
                        self.target_tree.update()
                finally:
                    self.socket_update_disabled = False
                    self.target_tree.active_group_node_name = old_active
                    self.target_tree.update_origin_is_input_push = old_origin
            else:
                for link in socket.links:
                    link.to_socket.input_value = socket.input_value
        finally:
            self._updating = False