import collections
from ibm.datastage._framework.dag import (
    DAG,
    CommentNode,
    GhostNode,
    Link,
    Node,
)
from math import floor

Layer = list[Node]


class LayeredLayout:
    """Layered layout produces a graph layout by organizing nodes into layers ideal for visualizing data pipelines and
    other directed workflows. Earlier layers contain nodes with no incoming edges, while later layers contain nodes with
    no outgoing edges.

    The layout algorithm builds on top of the Sugiyama layered graph drawing technique.
    It consists of the following steps:
        1. Run DAG.compute_metadata() to assign useful node metadata such as x, y positioning, topological order,
           parents, children, etc.
        2. Collect comment nodes from the DAG and set their dimensions.
        3. Insert ghost (fake) nodes for edges that span non-adjacent layers. These are used to reduce edge crossings
           caused by long edges that span multiple layers. The ghost nodes are removed after the layout is computed.
        4. Collect nodes into layers based on their topological order in the DAG so that nodes always have inputs from
           earlier layers and outputs to later layers.
        5. Order nodes within each layer based on the barycentric heuristic, which reduces edge crossings by ordering
           nodes based on the average order of their neighbors.
        6. Position nodes based on their layer number and order within the layer as an initial starting point.
        7. Iteratively refine node positions based on the average Y position of their neighbors to reduce edge crossings.
        8. Remove ghost nodes and round node positions to the nearest integer.
    """

    # Default node dimensions
    NODE_WIDTH = 48
    NODE_HEIGHT = 48
    COMMENT_WIDTH = 175
    COMMENT_HEIGHT = 60

    # Constraints for spacing
    MIN_NODE_SPACING = 48
    NODE_SPACING = 200
    LAYER_SPACING = 200
    COMMENT_LAYER_SPACING = 300

    # Estimated center of the canvas
    CANVAS_OFFSET_X = 800
    CANVAS_OFFSET_Y = 400

    # Number of iterations of node-swapping to minimize edge crossings. One iteration consists of two sweeps
    BARYCENTRIC_SWEEP_ITERATIONS = 2

    # Alpha value (0-1) for node position refinement. Higher values increase convergence speed but may cause oscillation
    ALPHA = 0.4
    # Number of iterations to refine node positions
    REFINEMENT_ITERATIONS = 10

    def __init__(self, dag: DAG):
        self.dag = dag
        self.layers: list[Layer] = []
        self.comments: list[CommentNode] = []

    def compute(self):
        """Compute the layered layout of the DAG, populating the x, y, and height (if non-default) properties of each node."""
        self.__collect_comment_nodes()
        self.__insert_ghost_nodes()
        self.__collect_layers()
        self.__order_layer_nodes()
        self.__position_nodes()

        for _ in range(self.REFINEMENT_ITERATIONS):
            self.__refine_node_positions()

        self.__remove_ghost_nodes()
        self.__round_node_positions()

        for layer in self.layers:
            for i, node in enumerate(layer):
                node.metadata["index"] = i

    def __collect_comment_nodes(self):
        """Collect comment nodes from the DAG and set their dimensions."""
        for node in self.dag.nodes():
            if not isinstance(node, CommentNode):
                continue

            node.metadata["width"] = self.COMMENT_WIDTH
            node.metadata["height"] = self.COMMENT_HEIGHT
            self.comments.append(node)

    def __insert_ghost_nodes(self):
        """Insert ghost nodes for edges that span non-adjacent layers. This helps reduce edge crossings caused by
        long edges that span multiple layers.

        For each edge from a parent to a child where child's layer > parent's layer + 1, create ghost nodes for each
        intermediate layer. Each ghost node is marked with metadata['ghost'] = True.
        """
        for parent in list(self.dag.nodes()):
            # Not necessary for comment nodes, as we will position these later
            if isinstance(parent, CommentNode):
                continue

            for child in list(parent.metadata["children"]):
                parent_layer_num = parent.metadata["layer"]
                child_layer_num = child.metadata["layer"]

                # Check if the edge spans more than one layer
                if child_layer_num > parent_layer_num + 1:
                    last: Node = parent
                    # Insert ghost nodes for each intermediate layer
                    for layer_num in range(parent_layer_num + 1, child_layer_num):
                        ghost_node = GhostNode()
                        ghost_node.metadata["layer"] = layer_num
                        ghost_node.metadata["children"] = []
                        ghost_node.metadata["parents"] = [last]
                        # Connect the previous node to the ghost node
                        self.dag.adj.setdefault(last, {})[ghost_node] = None
                        last.metadata["children"].append(ghost_node)
                        last = ghost_node

                    # Connect the last ghost node to the child node
                    last.metadata["children"].append(child)
                    child.metadata["parents"].append(last)
                    self.dag.adj.setdefault(last, {})[child] = None

    def __remove_ghost_nodes(self):
        """Remove previously inserted ghost nodes from the DAG."""
        clean_adj: dict[Node, dict[Node, Link]] = {}

        for from_node in self.dag.nodes():
            if from_node.metadata.get("ghost", False):
                continue

            # Add non-ghost parent nodes to the new adjacency list
            # If the parent has any non-ghost children, their links will also be added
            clean_adj.setdefault(from_node, {})
            for to_node, link in self.dag.adj[from_node].items():
                if not to_node.metadata.get("ghost", False):
                    # Only keep links where both the parent and child are not ghost nodes
                    clean_adj[from_node][to_node] = link

        self.dag.adj = clean_adj

    def __round_node_positions(self):
        """Round node positions to the nearest integer."""
        for node in self.dag.nodes():
            node.metadata["x"] = round(node.metadata["x"])
            node.metadata["y"] = round(node.metadata["y"])

    def __refine_node_positions(self):
        """Refine node positions based on the average Y position of their neighbors."""
        new_positions: dict[Node, float] = {}

        # Shift nodes vertically based on the average Y position of their neighbors
        for node in self.dag.nodes():
            # Fixed weights adjusting relative influence or "pull" of parent and child nodes
            parent_weight = 0.5
            child_weight = 0.5

            neighbor_y_sum = 0
            neighbor_y_weight = 0

            # Factor in the Y positions of parent nodes
            for parent in node.metadata["parents"]:
                neighbor_y_sum += (
                    parent.metadata["y"] + parent.metadata.get("height", self.NODE_HEIGHT) / 2
                ) * parent_weight
                neighbor_y_weight += parent_weight

            # Factor in the Y positions of child nodes
            for child in node.metadata["children"]:
                neighbor_y_sum += (
                    child.metadata["y"] + child.metadata.get("height", self.NODE_HEIGHT) / 2
                ) * child_weight
                neighbor_y_weight += child_weight

            if neighbor_y_weight:
                # Compute target Y position based on average Y position of neighbors
                target_y = neighbor_y_sum / neighbor_y_weight - node.metadata.get("height", self.NODE_HEIGHT) / 2
                # Move node towards (but not fully onto) target Y position based on ALPHA
                new_y = node.metadata["y"] + self.ALPHA * (target_y - node.metadata["y"])
                new_positions[node] = new_y

        # Replace old Y positions with new Y positions
        for node, new_y in new_positions.items():
            node.metadata["y"] = new_y

        # Prevent nodes from overlapping by ensuring a minimum vertical spacing between sibling nodes
        for layer in self.layers:
            # Skip empty layers
            if not layer:
                continue

            for i in range(1, len(layer)):
                prev_node = layer[i - 1]
                cur_node = layer[i]
                # Compute desired vertical space between sibling nodes
                height_space = prev_node.metadata.get("height", self.NODE_HEIGHT)
                desired_space = self.MIN_NODE_SPACING + height_space
                gap = cur_node.metadata["y"] - prev_node.metadata["y"]
                if gap < desired_space:
                    # If nodes are too close, move the current node down (higher Y)
                    cur_node.metadata["y"] += desired_space - gap

            # Center the entire layer vertically on the canvas
            all_y = [node.metadata["y"] + node.metadata.get("height", self.NODE_HEIGHT) / 2 for node in layer]
            center_y = (min(all_y) + max(all_y)) / 2
            for node in layer:
                node.metadata["y"] += self.CANVAS_OFFSET_Y - center_y

    @staticmethod
    def __count_node_relatives(node: Node):
        """Count the number of relatives (parents and children) of a node, excluding ghost nodes."""

        def is_relative(n: Node):
            return not n.metadata.get("ghost", False) and not isinstance(n, CommentNode)

        return len([n for n in node.metadata["parents"] + node.metadata["children"] if is_relative(n)])

    def __position_nodes(self):
        """Position nodes based on their layer number and order within the layer as an initial starting point.
        Also adjust the height of nodes with many relatives to improve visual distinction.
        """
        x_pos = 0
        max_x_pos = 0
        max_y_pos = 0

        for layer_num, layer in enumerate(self.layers):
            y_pos = 0
            has_comment = False

            for node_num, node in enumerate(layer):
                # Resize non-comment nodes if conditions are met
                if not isinstance(node, CommentNode):
                    if (relatives := self.__count_node_relatives(node)) >= 3:
                        # Increase height of nodes with many relatives (either many parents or many children)
                        node.metadata["height"] = (self.NODE_HEIGHT + self.MIN_NODE_SPACING / 2) * relatives
                else:
                    has_comment = True

                node.metadata["x"] = x_pos
                node.metadata["y"] = y_pos
                y_pos += self.NODE_SPACING
                max_x_pos = max(max_x_pos, x_pos)
                max_y_pos = max(max_y_pos, y_pos)

            if has_comment:
                x_pos += self.COMMENT_LAYER_SPACING
            else:
                x_pos += self.LAYER_SPACING

        # Center entire flow
        x_offset = x_pos / 2
        y_offset = max_y_pos / 2

        for node in self.dag.nodes():
            node.metadata["x"] += self.CANVAS_OFFSET_X - x_offset
            node.metadata["y"] += self.CANVAS_OFFSET_Y - y_offset

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
        layer_dict: dict[int, Layer] = collections.defaultdict(list)
        max_layer = 0
        for node in self.dag.nodes():
            # Don't include comment nodes in layers yet
            if isinstance(node, CommentNode):
                continue
            layer_num = node.metadata["layer"]
            max_layer = max(max_layer, layer_num)
            layer_dict[layer_num].append(node)

        # Assign comment nodes to layers
        for comment in self.comments:
            children = comment.metadata["children"]
            if not children:
                layer_dict[0].append(comment)
                continue

            layer_num = floor(sum([child.metadata["layer"] for child in children]) / len(children))
            comment.metadata["layer"] = layer_num
            layer_dict[layer_num].append(comment)

        # Convert the dictionary mapping to an ordered list of Layers
        for layer_num in range(max_layer + 1):
            self.layers.append(layer_dict[layer_num])
