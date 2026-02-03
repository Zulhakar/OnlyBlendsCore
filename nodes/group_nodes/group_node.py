import bpy

from ...core.constants import OB_TREE_TYPE, IS_DEBUG
from ...nodes.basic_nodes import NodeCnt
from ...core.helper import get_socket_index, get_parent_node_group


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

    group_input_node : bpy.props.StringProperty()
    group_output_node :  bpy.props.StringProperty()
    was_fired : bpy.props.BoolProperty(default=False)
    was_fired_external : bpy.props.BoolProperty(default=False)

    def init(self, context):
        super().init(context)

    def node_group_tree_update(self, context):
        self.log("node_group_tree_update")
        self.target_tree.group_node_input_list.clear()
        self.target_tree.group_node_output_list.clear()
        self.target_tree.update()
        self.target_tree.parent = self.parent_node_tree

    def draw_buttons(self, context, layout):
        layout.prop(self, "target_tree", text="")
        # if IS_DEBUG:
        #     for i, in_sock in enumerate(self.inputs):
        #         layout.prop(in_sock, "input_value", text=in_sock.name)
        #     for i, out_sock in enumerate(self.outputs):
        #         layout.prop(in_sock, "input_value", text=out_sock.name)

    def socket_update(self, socket):
        super().socket_update(socket)
        if not socket.is_output:
            index = get_socket_index(self.inputs, socket)
            for node in self.target_tree.nodes:
                if node.bl_idname == 'NodeGroupInput':
                    if node.outputs[index].bl_idname != 'NodeSocketVirtual':
                        for i, tmp in enumerate(self.inputs):
                            node.outputs[i].input_value = self.inputs[i].input_value
                            for link in node.outputs[i].links:
                                link.to_node.socket_update_disabled = True
                                link.to_socket.input_value = link.from_socket.input_value
                                link.to_node.socket_update_disabled = False
                        self.was_fired = True
                        node.outputs[index].input_value = socket.input_value
                        for link in node.outputs[index].links:
                            link.to_socket.input_value = socket.input_value
        else:
            if self.was_fired:
                for link in socket.links:
                    link.to_socket.input_value = socket.input_value
                self.was_fired = False
