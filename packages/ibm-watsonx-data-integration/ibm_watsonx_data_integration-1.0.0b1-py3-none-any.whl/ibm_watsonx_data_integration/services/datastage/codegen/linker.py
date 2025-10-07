from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.services.datastage.codegen.code_generator import MasterCodeGenerator
    from ibm_watsonx_data_integration.services.datastage.models.flow.dag import DAG, Link, Node


def format_dag(master_gen: "MasterCodeGenerator", dag: "DAG", schema: dict, composer: str = "flow") -> str:
    visited = set()

    roots = [node for node in dag.nodes() if not node.metadata["parents"]]
    q = deque(roots)

    lines: list[str] = []
    while q:
        node = q.popleft()
        if node in visited:
            continue
        visited.add(node)

        for child in node.metadata["children"]:
            for link in node.get_links_to(child):
                lines.append(format_connect_output_to(master_gen, node, child, link))
                schema_name, schema_code = None, None
                if link in schema:
                    schema_name, schema_code = schema[link]
                lines.append(format_link_configuration(master_gen, link, schema_name, schema_code))
            q.appendleft(child)

        lines.append("")

    return "\n".join(lines)


def format_link_settings(master_gen: "MasterCodeGenerator", link: "Link"):
    fmt = ""
    if link.type == "REJECT":
        fmt += ".reject()"
    if link.type == "REFERENCE":
        fmt += ".reference()"
    # if link._schema:
    #     if not (hasattr(link.src, "model") and link.src.model.op_name == "PxCFF"):
    #         fmt += f".use_schema({master_gen.get_object_var(link._schema)})"
    if link.maps_to_link:
        fmt += f".map_to_link({repr(link._maps_to_link)})"
    if link.maps_from_link:
        fmt += f".map_from_link({repr(link._maps_from_link)})"
    return fmt


def format_connect_output_to(master_gen: "MasterCodeGenerator", src: "Node", dest: "Node", link: "Link"):
    if not link.name:
        return ""
    return (
        master_gen.get_object_var(link)
        + " = "
        + master_gen.get_object_var(src)
        + ".connect_output_to("
        + master_gen.get_object_var(dest)
        + ")"
        + format_link_settings(master_gen, link)
    )


def format_link_configuration(master_gen: "MasterCodeGenerator", link: "Link", schema_name: str, schema_code: str):
    ret: list[str] = []
    if link.name:
        ret.append(master_gen.get_object_var(link) + f".name = {repr(link.name)}")
    if link.schema:
        if not (hasattr(link.src, "configuration") and link.src.configuration.op_name == "PxCFF"):
            ret.append(master_gen.get_object_var(link.schema) + " = " + master_gen.get_object_var(link) + ".create_schema()")
            ret.append(schema_code)
    if link.maps_to_link:
        ret.append(master_gen.get_object_var(link) + f".maps_to_link = {repr(link.maps_to_link)}")
    if link.maps_from_link:
        ret.append(master_gen.get_object_var(link) + f".maps_from_link = {repr(link.maps_from_link)}")
    return "\n".join(ret)
