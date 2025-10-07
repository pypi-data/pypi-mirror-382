import collections
import typing
from ibm_watsonx_data_integration.services.datastage.models.flow.dag import (
    DAG,
    Link,
    Node,
    StageNode,
)
from ibm_watsonx_data_integration.services.datastage.models.layout.common import GroupBoundingBox, NodeBoundingBox

NodeLayer = list[Node]


class LayeredLayout:
    # Default node dimensions
    NODE_WIDTH = 48
    NODE_HEIGHT = 48
    COMMENT_WIDTH = 175
    COMMENT_HEIGHT = 60

    # Constraints for spacing
    NODE_SPACING = 200
    LAYER_SPACING = 200

    # Estimated center of the canvas
    CANVAS_WIDTH = 1600
    CANVAS_HEIGHT = 800

    # Number of iterations of node-swapping to minimize edge crossings. One iteration consists of two sweeps
    BARYCENTRIC_SWEEP_ITERATIONS = 2

    # Number of iterations to refine node positions
    REFINEMENT_ITERATIONS = 300

    def __init__(self, dag: DAG):
        self.dag = dag
        self.layers: list[NodeLayer] = []
        #self.comments: list[CommentNode] = []
        self.node_boxes: dict[Node, NodeBoundingBox] = {}
        self.master_container = GroupBoundingBox()

    def compute(self):
        """Compute the layered layout of the DAG, populating the x, y, and height (if non-default) properties of each node."""
        # self.__collect_comment_nodes()
        # self.__insert_ghost_nodes()
        self.__collect_layers()
        self.__order_layer_nodes()

        self.__position_nodes()

        for _ in range(self.REFINEMENT_ITERATIONS):
            self.__apply_forces()

        # self.__remove_ghost_nodes()
        self.master_container.center_within(GroupBoundingBox(width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT))
        self.master_container.update_absolute_positions(0, 0)

    # def __collect_comment_nodes(self):
    #     """Collect comment nodes from the DAG and set their dimensions."""
    #     for node in self.dag.nodes():
    #         if not isinstance(node, CommentNode):
    #             continue
    #         self.comments.append(node)

    # def __insert_ghost_nodes(self):
    #     """Insert ghost nodes for edges that span non-adjacent layers. This helps reduce edge crossings caused by
    #     long edges that span multiple layers.

    #     For each edge from a parent to a child where child's layer > parent's layer + 1, create ghost nodes for each
    #     intermediate layer. Each ghost node is marked with metadata['ghost'] = True.
    #     """
    #     for parent in list(self.dag.nodes()):
    #         # Not necessary for comment nodes, as we will position these later
    #         if isinstance(parent, CommentNode):
    #             continue

    #         for child in list(parent.metadata["children"]):
    #             parent_layer_num = parent.metadata["layer"]
    #             child_layer_num = child.metadata["layer"]

    #             # Check if the edge spans more than one layer
    #             if child_layer_num > parent_layer_num + 1:
    #                 last: Node = parent
    #                 # Insert ghost nodes for each intermediate layer
    #                 for layer_num in range(parent_layer_num + 1, child_layer_num):
    #                     ghost_node = GhostNode()
    #                     ghost_node.metadata["layer"] = layer_num
    #                     ghost_node.metadata["children"] = []
    #                     ghost_node.metadata["parents"] = [last]
    #                     # Connect the previous node to the ghost node
    #                     self.dag.adj.setdefault(last, {})[ghost_node] = []
    #                     last.metadata["children"].append(ghost_node)
    #                     last = ghost_node

    #                 # Connect the last ghost node to the child node
    #                 last.metadata["children"].append(child)
    #                 child.metadata["parents"].append(last)
    #                 self.dag.adj.setdefault(last, {})[child] = []

    # def __remove_ghost_nodes(self):
    #     """Remove previously inserted ghost nodes from the DAG."""
    #     clean_adj: dict[Node, dict[Node, list[Link]]] = {}

    #     for from_node in self.dag.nodes():
    #         if from_node.metadata.get("ghost", False):
    #             continue

    #         # Add non-ghost parent nodes to the new adjacency list
    #         # If the parent has any non-ghost children, their links will also be added
    #         clean_adj.setdefault(from_node, {})
    #         for to_node, links in self.dag.adj[from_node].items():
    #             if not to_node.metadata.get("ghost", False):
    #                 # Only keep links where both the parent and child are not ghost nodes
    #                 clean_adj[from_node][to_node] = links

    #     self.dag.adj = clean_adj

    def __apply_forces(self):
        """Applies two sets of forces:
        1. Weak attractive forces from nodes to their parents
        2. Strong repulsive forces between neighboring nodes in the same layer
        """
        for layer_box in self.master_container.children:
            layer_box = typing.cast(GroupBoundingBox, layer_box)
            for node_box in layer_box.children:
                node_box = typing.cast(NodeBoundingBox, node_box)
                node = node_box.node

                for parent in node.metadata["parents"]:
                    parent_box = self.node_boxes[parent]
                    # TODO: Diminishing force based on layer proximity
                    node_box.add_force(0, min(80, (parent_box.center_y() - node_box.center_y()) * 0.2))

        # Apply repulsive forces between neighboring nodes in the same layer
        for layer_box in self.master_container.children:
            layer_box = typing.cast(GroupBoundingBox, layer_box)
            for i, node_box in enumerate(layer_box.children):
                node_box = typing.cast(NodeBoundingBox, node_box)
                for j, other_node_box in enumerate(layer_box.children):
                    if i == j:
                        continue
                    other_node_box = typing.cast(NodeBoundingBox, other_node_box)
                    # Apply force that exponentially grows as the nodes get closer to MIN_NODE_SPACING
                    sign = -1 if node_box.center_y() < other_node_box.center_y() else 1
                    dist = node_box.y_boundary_distance(other_node_box)
                    # Only apply force if nodes are close enough
                    if dist < 300:
                        force = (600 / max(dist, 1)) ** 2
                        node_box.add_force(0, sign * force)

        for layer_box in self.master_container.children:
            layer_box = typing.cast(GroupBoundingBox, layer_box)
            for node_box in layer_box.children:
                node_box = typing.cast(NodeBoundingBox, node_box)
                node_box.apply_forces()

    @staticmethod
    def __count_node_relatives(node: Node):
        """Count the number of relatives (parents and children) of a node, excluding ghost nodes."""

        def is_relative(n: Node):
            return not n.metadata.get("ghost", False) #and not isinstance(n, CommentNode)

        parent_count = len([n for n in node.metadata["parents"] if is_relative(n)])
        child_count = len([n for n in node.metadata["children"] if is_relative(n)])

        return max(parent_count, child_count)

    def __position_nodes(self):
        """Position nodes based on their layer number and order within the layer as an initial starting point.
        Also adjust the height of nodes with many relatives to improve visual distinction.
        """
        for layer_num, layer in enumerate(self.layers):
            has_comment = False
            layer_container = GroupBoundingBox()

            for node_num, node in enumerate(layer):
                # Resize non-comment nodes if conditions are met
                if isinstance(node, StageNode):
                    width = self.NODE_WIDTH
                    height = self.NODE_HEIGHT
                    if (relatives := self.__count_node_relatives(node)) >= 3:
                        # Increase height of nodes with many relatives (either many parents or many children)
                        height = (self.NODE_HEIGHT + 10) * relatives
                else:
                    width = self.COMMENT_WIDTH
                    height = self.COMMENT_HEIGHT
                    has_comment = True

                box = NodeBoundingBox(node=node, width=width, height=height)
                self.node_boxes[node] = box
                layer_container.children.append(box)

            layer_container.width = self.COMMENT_WIDTH if has_comment else self.NODE_WIDTH
            layer_container.arrange_children_vertically(self.NODE_SPACING)
            self.master_container.children.append(layer_container)
            self.master_container.arrange_children_horizontally(self.LAYER_SPACING)

    def __order_layer_nodes(self):
        """Order nodes within each layer based on the barycentric heuristic.

        The barycentric heuristic reduces edge crossings by ordering nodes in one layer based on the average order of
        their neighbors. We perform alternating downward and upward sweeps to iteratively improve the ordering of nodes
        within each layer.
        """
        # Initially order nodes within each layer alphabetically for consistency
        for layer in self.layers:
            layer.sort(key=lambda n: type(n).__name__)

        # Then order nodes based on barycentric heuristic
        for _ in range(self.BARYCENTRIC_SWEEP_ITERATIONS):
            # Downward sweep - order layers from top to bottom
            for i in range(1, len(self.layers)):
                barycenters = {}
                for node in self.layers[i]:
                    barycenters[node] = self.__compute_weighted_barycenter(node, i)
                self.layers[i].sort(key=lambda n: barycenters[n])

            # Upward sweep - order layers from bottom to top
            for i in range(len(self.layers) - 2, -1, -1):
                barycenters = {}
                for node in self.layers[i]:
                    barycenters[node] = self.__compute_weighted_barycenter(node, i)
                self.layers[i].sort(key=lambda n: barycenters[n])

    def __compute_normalized_index(self, node: Node, current_layer_num: int):
        """Computes the continuous normalized index of a node within its layer.
        0.5 means the node is in the middle of the layer.
        0 means the node is the first in the layer.
        1 means the node is last.
        """
        layer = self.layers[current_layer_num]
        if len(layer) == 1:
            return 0.5
        return layer.index(node) / (len(layer) - 1)

    def __compute_weighted_barycenter(self, node: Node, current_layer_num: int):
        """Computes the barycenter of a node within its layer. The computation discounts the influence of neighbor nodes
        that are in layers further away from the current layer.
        """
        total_weight = 0
        weighted_sum = 0

        for parent in node.metadata["parents"]:
            parent_layer_num = parent.metadata["layer"]
            if parent_layer_num < current_layer_num:
                weight = 1 / (current_layer_num - parent_layer_num)
                weighted_sum += weight * self.__compute_normalized_index(parent, parent_layer_num)
                total_weight += weight

        for child in node.metadata["children"]:
            child_layer_num = child.metadata["layer"]
            if child_layer_num > current_layer_num:
                weight = 1 / (child_layer_num - current_layer_num)
                weighted_sum += weight * self.__compute_normalized_index(child, child_layer_num)
                total_weight += weight

        if total_weight > 0:
            return weighted_sum / total_weight
        else:
            return 0.5

    def __collect_layers(self):
        """Collect nodes into list of layers based on the topological order of the DAG."""
        assert self.dag.adj, "DAG is empty"

        # Collect nodes into a dictionary mapping the layer # to the Layer
        layer_dict: dict[int, NodeLayer] = collections.defaultdict(list)
        max_layer = 0
        for node in self.dag.nodes():
            # Don't include comment nodes in layers yet
            # if isinstance(node, CommentNode):
            #     continue
            layer_num = node.metadata["layer"]
            max_layer = max(max_layer, layer_num)
            layer_dict[layer_num].append(node)

        # Assign comment nodes to layers
        # for comment in self.comments:
        #     children = comment.metadata["children"]
        #     if not children:
        #         layer_dict[0].append(comment)
        #         continue

        #     # Put comment node in layer upstream to children
        #     layer_num = min([child.metadata["layer"] for child in children]) - 1
        #     comment.metadata["layer"] = layer_num
        #     layer_dict[layer_num].append(comment)

        # Convert the dictionary mapping to an ordered list of Layers
        for layer_num in range(max_layer + 1):
            self.layers.append(layer_dict[layer_num])
