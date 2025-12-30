"""Attack path display functions"""
from hackles.display.colors import Colors
from hackles.display.tables import print_warning
from hackles.core.config import config


def print_path(path_data: dict):
    """Pretty-print an attack path with relationship arrows (only in table mode)"""
    if config.output_format != 'table':
        return

    nodes = path_data.get("nodes", [])
    node_types = path_data.get("node_types", [])
    rels = path_data.get("relationships", [])

    if not nodes:
        print_warning("No path found")
        return

    path_len = path_data.get("path_length", len(nodes) - 1)
    print(f"    {Colors.BOLD}Path ({path_len} hop{'s' if path_len != 1 else ''}):{Colors.END}")

    for i, node in enumerate(nodes):
        type_str = f"({node_types[i]})" if i < len(node_types) else ""

        if node in config.owned_cache:
            is_admin = config.owned_cache[node]
            marker = f"{Colors.FAIL}[!]{Colors.END}" if is_admin else f"{Colors.WARNING}[!]{Colors.END}"
            print(f"      {marker} {node} {type_str}")
        else:
            print(f"      {node} {type_str}")

        if i < len(rels):
            print(f"        {Colors.CYAN}--[{rels[i]}]-->{Colors.END}")
