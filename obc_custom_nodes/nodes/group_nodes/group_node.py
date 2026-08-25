import bpy
from ...nodes.basic_nodes import NodeCnt
from ...base.helper import get_socket_index, get_parent_node_group
from ....config import OB_TREE_TYPE, IS_DEBUG

import bpy

import bpy

def duplicate_node_tree(src_tree: bpy.types.NodeTree, new_name: str) -> bpy.types.NodeTree:
    if not src_tree:
        return None
    if new_name in bpy.data.node_groups:
        return bpy.data.node_groups[new_name]

    new_tree = bpy.data.node_groups.new(name=new_name, type=src_tree.bl_idname)
    new_tree.bl_label = src_tree.bl_label

    # ---- Interface ----
    if hasattr(src_tree, "interface"):
        for item in src_tree.interface.items_tree:
            if not hasattr(item, "in_out"):
                continue
            new_tree.interface.new_socket(
                name=item.name,
                in_out=item.in_out,
                socket_type=item.socket_type
            )

    # ---- Nodes ----
    node_map = {}
    for node in src_tree.nodes:
        new_node = new_tree.nodes.new(node.bl_idname)
        new_node.name = node.name
        new_node.label = node.label
        new_node.location = node.location.copy()

        for prop_name in ["width","height","hide","mute","select","use_custom_color","color"]:
            if hasattr(node, prop_name):
                try:
                    setattr(new_node, prop_name, getattr(node, prop_name))
                except Exception:
                    pass

        for i, s in enumerate(node.inputs):
            if i < len(new_node.inputs):
                try: new_node.inputs[i].default_value = s.default_value
                except Exception: pass
        for i, s in enumerate(node.outputs):
            if i < len(new_node.outputs):
                try: new_node.outputs[i].default_value = s.default_value
                except Exception: pass

        node_map[node] = new_node

    # ---- Links ----
    for link in src_tree.links:
        fn = node_map.get(link.from_node)
        tn = node_map.get(link.to_node)
        if not fn or not tn:
            continue

        # find sockets by name in the new nodes
        from_sock = next((s for s in fn.outputs if s.name == link.from_socket.name), None)
        to_sock   = next((s for s in tn.inputs  if s.name == link.to_socket.name),   None)

        if from_sock and to_sock:
            new_tree.links.new(from_sock, to_sock)

    return new_tree




class GroupNodeCnt(NodeCnt, bpy.types.NodeCustomGroup):
    bl_label = "Group"
    bl_icon = 'NODETREE'

    target_tree: bpy.props.PointerProperty(
        name="Group",
        type=bpy.types.NodeTree,
        poll=lambda self, tree: (tree.bl_idname == OB_TREE_TYPE and get_parent_node_group(self, tree)),
        update=lambda self, context: self.node_group_tree_update(context)
    )
    parent_node_tree: bpy.props.PointerProperty(name="Node Tree", type=bpy.types.NodeTree)
    instance_id: bpy.props.StringProperty(default="")

    def init(self, context):
        super().init(context)
        if not self.instance_id:
            self.instance_id = f"{self.name}_{id(self)}"

    def recompute(self):
        """Called by the parent tree's topological evaluator.
        Evaluates this group's target tree for THIS instance only."""
        if self.target_tree and hasattr(self.target_tree, 'evaluate_instance'):
            self.target_tree.evaluate_instance(self)


    def copy(self, node):
        super().copy(node)
        # keep the same template tree, only new instance id
        if not self.instance_id:
            self.instance_id = f"{self.name}_{id(self)}"

    def node_group_tree_update(self, context):
        if self.target_tree:
            self.target_tree.parent = self.parent_node_tree
            self.target_tree.get_or_create_instance(self)

    def socket_update(self, socket):
        if getattr(self, "_updating", False) or not self.target_tree:
            return
        self._updating = True
        try:
            super().socket_update(socket)
            if socket.is_output:
                for link in socket.links:
                    link.to_socket.input_value = socket.input_value
                return
            # an instance input changed -> re-evaluate all instances
            if hasattr(self.target_tree, 'evaluate_all'):
                self.target_tree.evaluate_all()
        finally:
            self._updating = False

    def draw_buttons(self, context, layout):
        layout.prop(self, "target_tree", text="")