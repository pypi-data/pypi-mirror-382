from ibm_watsonx_data_integration.services.datastage.models.flow.dag import (
    DAG,
    Link,
    Node,
)
from ibm_watsonx_data_integration.services.datastage.models.stages import *


class StageComposer:
    def __init__(self):
        self.dag = DAG()

    def get_dag(self):
        return self.dag

    def get_link(self, left: Node, right: Node) -> Link | None:
        links = self.dag.get_links_between(left, right)
        if len(links) == 0:
            raise ValueError("No link between nodes")
        if len(links) > 1:
            raise ValueError("Multiple links between nodes")
        return links[0]

    def get_links(self, left: Node, right: Node) -> list[Link]:
        return self.dag.get_links_between(left, right)

    def add(self, node: Node):
        self.dag.add_node(node)

    def remove(self, node: Node):
        self.dag.remove_node(node)

    def add_link(self, src: Node, dest: Node, link: Link = None) -> Link:
        if not link:
            link = Link(self, name=None)
        link.src = src
        link.dest = dest
        self.dag.add_link(link)
        return link

    def remove_links(self, src: Node, dest: Node) -> list[Link]:
        removed = self.dag.remove_links(src, dest)
        if not removed:
            raise ValueError(f"No links found between {src} and {dest}")
        return removed

    def remove_link(self, src: Node, dest: Node, link_name: str) -> Link:
        removed = self.dag.remove_link(src, dest, link_name)
        if not removed:
            raise ValueError(f"Link {link_name} not found between {src} and {dest}")
        if len(removed) > 1:
            # console.print(
            #     f"WARN: Multiple links found with name {link_name}. Returning first one"
            # )
            print(f"WARN: Multiple links found with name {link_name}. Returning first one")
        return removed[0]
