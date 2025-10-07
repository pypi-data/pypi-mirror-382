import inspect
import pydantic
from abc import ABC
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from ibm_watsonx_data_integration.services.datastage.models.schema import Schema


class Node(ABC):
    def __init__(self, dag: "DAG"):
        self._dag = dag
        self.metadata: dict[str, Any] = {}

        try:
            self.var_name = inspect.stack()[-1].code_context[0].split("=")[0].strip()
        except:
            self.var_name = "node"

    def connect_output_to(self, node: "Node") -> "Link":
        """Connects the output of this node to the input of another node.

        Args:
            node: The destination node to connect to.

        Returns:
            A Link object representing the connection.
        """
        link = Link(self._dag)
        link.src = self
        link.dest = node
        self._dag.add_link(link)
        return link

    def connect_input_to(self, node: "Node") -> "Link":
        """Connects the input of this node to the output of another node.

        Args:
            node: The source node to connect from.

        Returns:
            A Link object representing the connection.
        """
        link = Link(self._dag)
        link.src = node
        link.dest = self
        self._dag.add_link(link)
        return link

    def disconnect_output_from(self, dest: "Node") -> list["Link"]:
        """Disconnects the output of this node from the input of another node.

        Args:
            dest: The destination node to disconnect from.

        Returns:
            The list of Links that were removed.
        """
        links = self._dag.remove_link(self, dest, self.get_link(dest).name)
        if not links:
            raise ValueError(f"No link found between {self} and {dest}")
        return links

    def disconnect_input_from(self, src: "Node") -> list["Link"]:
        """Disconnects the input of this node from the output of another node.

        Args:
            src: The source node to disconnect from.

        Returns:
            The list of Links that were removed.
        """
        links = self._dag.remove_link(src, self, self.get_link(src).name)
        if not links:
            raise ValueError(f"No link found between {src} and {self}")
        return links

    def get_link(self, dest: "Node") -> "Link":
        links = self.get_links_to(dest)
        if links == 0:
            raise ValueError(f"No links found between {self} and {dest}")
        if len(links) > 1:
            raise ValueError(f"Multiple links found between {self} and {dest}")
        return links[0]

    def get_links_to(self, dest: "Node") -> list["Link"]:
        """Returns:
        All links between this node and the destination node.
        """
        return self._dag.get_links_between(self, dest)

    def _get_min_primary_inputs(self) -> int:
        """Returns:
        The minimum number of primary inputs for this node. -1 indicates no limit.
        """
        return -1

    def _get_max_primary_inputs(self) -> int:
        """Returns:
        The maximum number of primary inputs for this node. -1 indicates no limit.
        """
        return -1

    def _get_min_primary_outputs(self) -> int:
        """Returns:
        The minimum number of primary outputs for this node. -1 indicates no limit.
        """
        return -1

    def _get_max_primary_outputs(self) -> int:
        """Returns:
        The maximum number of primary outputs for this node. -1 indicates no limit.
        """
        return -1

    def _get_min_reject_outputs(self) -> int:
        """Returns:
        The minimum number of reject outputs for this node. -1 indicates no limit.
        """
        return -1

    def _get_max_reject_outputs(self) -> int:
        """Returns:
        The maximum number of reject outputs for this node. -1 indicates no limit.
        """
        return -1

    def _get_min_reference_inputs(self) -> int:
        """Returns:
        The minimum number of reference inputs for this node. -1 indicates no limit.
        """
        return -1

    def _get_max_reference_inputs(self) -> int:
        """Returns:
        The maximum number of reference inputs for this node. -1 indicates no limit.
        """
        return -1


class Link:
    def __init__(self, dag: "DAG", name: str = None):
        self._dag = dag
        self.name = name
        self.type = "PRIMARY"
        self.schema: Schema | None = None
        self.maps_to_link: str | None = None
        self.maps_from_link: str | None = None
        self.__src = None
        self.__dest = None

    @property
    def src(self):
        return self.__src

    @src.setter
    def src(self, new_left: Node):
        self.__src = new_left

    @property
    def dest(self):
        return self.__dest

    @dest.setter
    def dest(self, new_right: Node):
        self.__dest = new_right

    def set_name(self, name: str) -> "Link":
        self.name = name
        return self

    def primary(self) -> "Link":
        """Sets the link type to primary. Modifies the current link object.

        Returns:
            The current link object.
        """
        self.type = "PRIMARY"
        return self

    def reference(self) -> "Link":
        """Sets the link type to reference. Modifies the current link object.

        Returns:
            The current link object.
        """
        self.type = "REFERENCE"
        return self

    def reject(self) -> "Link":
        """Sets the link type to reject. Modifies the current link object.

        Returns:
            The current link object.
        """
        self.type = "REJECT"
        return self

    def map_to_link(self, link_name: str) -> "Link":
        self.maps_to_link = link_name
        return self

    def map_from_link(self, link_name: str) -> "Link":
        self.maps_from_link = link_name
        return self

    def create_schema(self) -> "Schema":
        """Initializes the schema that the link uses.

        Returns:
            The new link object.
        """
        self.schema = Schema()
        return self.schema


class DAG:
    def __init__(self):
        self.adj: dict[Node, dict[Node, list[Link]]] = {}
        self.is_metadata_computed = False

    def stages(self):
        for stage in self.adj.keys():
            yield stage

    def nodes(self):
        for node in self.adj.keys():
            yield node

    def links(self):
        for from_node, to_dict in self.adj.items():
            for to_node, links in to_dict.items():
                yield from links

    def links_stable(self):
        top_order = self.get_topological_ordering(stages_only=True)
        for node in top_order:
            to_nodes = list(self.adj[node].keys())
            to_nodes.sort(key=lambda n: top_order.index(n))
            for to_node in to_nodes:
                yield from self.adj[node][to_node]

    def get_links_between(self, src: "Node", dest: "Node") -> list[Link]:
        return self.adj.get(src, {}).get(dest, [])

    def add_node(self, node: "Node") -> "Node":
        self.adj.setdefault(node, {})
        return node

    def replace_node(self, old_node: Node, new_node: Node):
        if old_node not in self.adj:
            raise ValueError(f"Node {old_node.label} not found in DAG")

        self.adj[new_node] = self.adj.pop(old_node)

        for from_node, to_dict in self.adj.items():
            if old_node in to_dict:
                to_dict[new_node] = to_dict.pop(old_node)

        for to_node, links in self.adj[new_node].items():
            for link in links:
                if link.src == old_node:
                    link.src = new_node
        for from_node, links in self.adj.items():
            for to_node, links in self.adj[from_node].items():
                for link in links:
                    if link.dest == old_node:
                        link.dest = new_node

        if hasattr(old_node, "metadata"):
            new_node.metadata = old_node.metadata.copy()
            new_node.metadata["var_name"] = old_node.var_name
        else:
            new_node.metadata = {"var_name": old_node.var_name}
        self.remove_node(old_node)

    def remove_node(self, node: "Node"):
        if node in self.adj:
            del self.adj[node]
        for from_node, to_dict in self.adj.items():
            if node in to_dict:
                del to_dict[node]

    def add_link(self, link: "Link"):
        from_node = self.add_node(link.src)
        to_node = self.add_node(link.dest)

        if link in self.adj.get(from_node, {}).get(to_node, []):
            return

        self.adj[from_node].setdefault(to_node, [])
        self.adj[from_node][to_node].append(link)

    def remove_link(self, src: "Node", dest: "Node", link_name: str) -> list[Link]:
        removed = []
        if src in self.adj and dest in self.adj[src]:
            kept = []
            for l in self.adj[src][dest]:
                if l.name == link_name:
                    removed.append(l)
                else:
                    kept.append(l)
            if not kept:
                del self.adj[src][dest]
            else:
                self.adj[src][dest] = kept
        return removed

    def remove_links(self, src: "Node", dest: "Node") -> list[Link]:
        if src in self.adj and dest in self.adj[src]:
            links = self.adj[src][dest]
            del self.adj[src][dest]
            return links
        return []

    def get_topological_ordering(self, *, stages_only: bool):
        if stages_only:
            in_degrees = self.__compute_in_degrees(lambda n: isinstance(n, StageNode))
        else:
            in_degrees = self.__compute_in_degrees()

        # Queue of nodes with in-degree 0
        queue: list[Node] = [node for node, in_degree in in_degrees.items() if in_degree == 0]

        # Perform topological sorting of nodes using Kahn's algorithm
        top_order = []
        while queue:
            node = queue.pop(0)
            top_order.append(node)
            for to_node, links in self.adj[node].items():
                in_degrees[to_node] -= len(links)
                if in_degrees[to_node] == 0:
                    queue.append(to_node)

        # Check if graph has cycle
        if len(top_order) != len(self.adj):
            raise ValueError(f"Graph contains cycle {self.__print_cycle(self.adj)}")

        return top_order

    def compute_metadata(self):
        in_degrees_stages = self.__compute_in_degrees(lambda n: isinstance(n, StageNode))
        out_degrees_stages = self.__compute_out_degrees(lambda n: isinstance(n, StageNode))

        for node in self.nodes():
            node.metadata["in_degree"] = in_degrees_stages[node]
            node.metadata["out_degree"] = out_degrees_stages[node]
            node.metadata["parents"] = []
            node.metadata["children"] = []

        top_order = self.get_topological_ordering(stages_only=False)

        # Check if graph has cycle
        if len(top_order) != len(self.adj):
            raise ValueError(f"Graph contains cycle {self.__print_cycle(self.adj)}")

        # Compute parents of each node
        for link in self.links():
            # If link src is already in dest's parents, skip (this can happen due to multi-links between 2 nodes)
            if link.src not in link.dest.metadata["parents"]:
                link.dest.metadata["parents"].append(link.src)
            # Do the same for src's children
            if link.dest not in link.src.metadata["children"]:
                link.src.metadata["children"].append(link.dest)

        # Compute cardinality
        for node in self.nodes():
            if not isinstance(node, StageNode):
                continue

            node.metadata["primary_inputs"] = 0
            node.metadata["primary_outputs"] = 0
            node.metadata["reference_inputs"] = 0
            node.metadata["reference_outputs"] = 0
            node.metadata["reject_inputs"] = 0
            node.metadata["reject_outputs"] = 0

            for parent in node.metadata["parents"]:
                if not isinstance(parent, StageNode):
                    continue

                links = self.adj[parent][node]
                for link in links:
                    match link.type:
                        case "PRIMARY":
                            node.metadata["primary_inputs"] += 1
                        case "REFERENCE":
                            node.metadata["reference_inputs"] += 1
                        case "REJECT":
                            node.metadata["reject_inputs"] += 1
                        case _:
                            raise ValueError(f"Unknown link type {link.type}")

            for child in node.metadata["children"]:
                if not isinstance(child, StageNode):
                    continue

                links = self.adj[node][child]
                for link in links:
                    match link.type:
                        case "PRIMARY":
                            node.metadata["primary_outputs"] += 1
                        case "REFERENCE":
                            node.metadata["reference_outputs"] += 1
                        case "REJECT":
                            node.metadata["reject_outputs"] += 1
                        case _:
                            raise ValueError(f"Unknown link type {link.type}")

        # Assign each node to a layer based on topological order
        for node in top_order:
            if not node.metadata["parents"]:
                # Source nodes reside in layer 0
                node.metadata["layer"] = 0
            else:
                # Non-source nodes reside in layer 1 + max(parents' layers)
                node.metadata["layer"] = max(parent.metadata["layer"] for parent in node.metadata["parents"]) + 1

        self.is_metadata_computed = True

    def get_connected_subgraphs(self):
        assert self.adj, "DAG is empty"

        # Compute mapping from nodes to their parents
        parents: dict[Node, list[Node]] = {}

        for parent_node, children_dict in self.adj.items():
            parents.setdefault(parent_node, [])
            for child_node, links in children_dict.items():
                parents.setdefault(child_node, [])
                parents[child_node].append(parent_node)

        subgraphs: list[DAG] = []
        visited = set()

        def dfs(cur_node: Node, dag: DAG):
            if cur_node in visited:
                return

            visited.add(cur_node)
            dag.adj[cur_node] = self.adj[cur_node]

            # DFS downstream
            for n in self.adj[cur_node].keys():
                dfs(n, dag)
            # DFS upstream
            for n in parents.get(cur_node):
                dfs(n, dag)

        for node in self.nodes():
            subgraph = DAG()
            dfs(node, subgraph)
            if subgraph.adj:
                subgraphs.append(subgraph)

        return subgraphs

    def __compute_in_degrees(self, condition: Callable[[Node], bool] = lambda _: True):
        in_degrees = {node: 0 for node in self.nodes()}
        for link in self.links():
            in_degrees[link.dest] += 1 if condition(link.src) else 0
        return in_degrees

    def __compute_out_degrees(self, condition: Callable[[Node], bool] = lambda _: True):
        out_degrees = {node: 0 for node in self.nodes()}
        for link in self.links():
            out_degrees[link.src] += 1 if condition(link.dest) else 0
        return out_degrees

    def __str__(self):
        out = ""
        for link in self.links():
            out += f"{link.src} -> {link.dest}\n"
        return out

    def __print_cycle(self, adj):
        """nodes: a list of nodes
        adj: a dict as adjacency graph
        output: string.
        """
        nodes = adj.keys()
        nodes_not_lead_to_deadend = set()

        for node in nodes:
            stack = [(node, [])]

            while len(stack) != 0:
                curr_node, visited = stack.pop()

                if curr_node in nodes_not_lead_to_deadend:
                    # since this node will not lead to any deadend, we ignore this node
                    continue

                if curr_node in visited:
                    # if current node is already visited in current path, we detected a cycle.
                    path = visited + [curr_node]
                    cycle = path[path.index(path[-1]) :]
                    cycle = [n.var_name for n in cycle]
                    cycle[0] = "\033[31m" + cycle[0] + "\033[0m"
                    cycle[-1] = "\033[31m" + cycle[-1] + "\033[0m"
                    return "[" + " >> ".join(cycle) + "]"

                if len(adj[node]) == 0:
                    # if this node has no outdegree. we ignore
                    nodes_not_lead_to_deadend.add(node)
                    continue

                for adj_node in adj[curr_node]:
                    if adj_node not in nodes_not_lead_to_deadend:
                        stack.append((adj_node, visited + [curr_node]))

        # if we got this far, this means our algorithm didn't detect any cycle. Though this shouldn't be the case.
        return ""

class StageNode(Node):
    def __init__(
        self,
        dag: "DAG",
        configuration: pydantic.BaseModel,
        *,
        label: str = None,
    ):
        super().__init__(dag)
        self.label = label
        self.configuration = configuration

    def _get_node_type(self) -> str | None:
        return self.configuration.node_type

    def _get_node_label(self) -> str | None:
        return self.label

    def _get_op_name(self) -> str | None:
        return self.configuration.op_name

    def _get_image(self) -> str:
        return self.configuration.image

    def _get_node_params(self) -> dict[str, Any] | None:
        return self.configuration.get_parameters_props()

    def _get_advanced_params(self) -> dict[str, Any] | None:
        return self.configuration.get_advanced_props()

    def _get_input_port_params(self, link=None) -> dict[str, Any] | None:
        if link:
            return self.configuration.get_input_ports_props(link)
        return self.configuration.get_input_ports_props()

    def _get_output_port_params(self, link=None) -> dict[str, Any] | None:
        if link:
            return self.configuration.get_output_ports_props(link)
        return self.configuration.get_output_ports_props()

    def _get_source_connection_params(self) -> dict[str, Any] | None:
        return self.configuration.get_source_props()

    def _get_target_connection_params(self):
        return self.configuration.get_target_props()

    def _get_max_primary_inputs(self) -> int:
        in_card = self.configuration.get_input_cardinality()
        return in_card["max"]

    def _get_min_primary_inputs(self) -> int:
        in_card = self.configuration.get_input_cardinality()
        return in_card["min"]

    def _get_max_primary_outputs(self) -> int:
        out_card = self.configuration.get_output_cardinality()
        return out_card["max"]

    def _get_min_primary_outputs(self) -> int:
        out_card = self.configuration.get_output_cardinality()
        return out_card["min"]

    def _get_min_reject_outputs(self) -> int:
        try:
            return self.configuration.get_app_data_props()["datastage"]["minRejectOutputs"]
        except AttributeError | KeyError:
            return super()._get_min_reject_outputs()

    def _get_max_reject_outputs(self) -> int:
        try:
            return self.configuration.get_app_data_props()["datastage"]["maxRejectOutputs"]
        except AttributeError | KeyError:
            return super()._get_max_reject_outputs()

    def _get_min_reference_inputs(self) -> int:
        try:
            return self.configuration.get_app_data_props()["datastage"]["minReferenceInputs"]
        except AttributeError | KeyError:
            return super()._get_min_reference_inputs()

    def _get_max_reference_inputs(self) -> int:
        try:
            return self.configuration.get_app_data_props()["datastage"]["maxReferenceInputs"]
        except AttributeError | KeyError:
            return super()._get_max_reference_inputs()

    def _get_rcp(self) -> bool | None:
        return self.configuration.runtime_column_propagation

    def _get_acp(self) -> bool | None:
        # Added this check as not every model has the `auto_column_propagation` property, and accessing it causes an error
        if hasattr(self.configuration, "auto_column_propagation"):
            return self.configuration.auto_column_propagation

    def _get_connection_params(self, location) -> dict[str, Any] | None:
        if location == "both":
            return {
                **self.configuration.get_source_props(),
                **self.configuration.get_target_props(),
            }
        elif location == "source":
            return self.configuration.get_source_props()
        elif location == "target":
            return self.configuration.get_target_props()
        return None

    def _get_connection_name(self) -> str | None:
        return self.configuration.connection.name

    def _get_project_id(self) -> str | None:
        return self.configuration.connection.proj_id

    def _get_connection_id(self) -> str | None:
        return self.configuration.connection.asset_id

    def __str__(self):
        return f"<{type(self).__name__}>"
