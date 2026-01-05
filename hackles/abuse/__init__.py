"""Abuse command display module for showing exploitation commands alongside findings."""

from __future__ import annotations

from typing import Any

from hackles.core.config import config
from hackles.display.colors import colors


def print_abuse_section(
    results: list[dict[str, Any]],
    edge_type: str,
    target_type_key: str = "target_type",
    target_name_key: str = "target",
) -> None:
    """Display abuse commands for edge-based findings (ACL, delegation, etc.).

    Args:
        results: Query results containing target information
        edge_type: The edge type (GenericAll, WriteDacl, etc.)
        target_type_key: Key in result dict for target type
        target_name_key: Key in result dict for target name
    """
    if not config.show_abuse or config.output_format != "table":
        return

    if not results:
        return

    from hackles.abuse.loader import get_abuse_commands

    # Group results by target type
    targets_by_type: dict[str, list[str]] = {}
    for r in results:
        t_type = r.get(target_type_key, "Unknown")
        t_name = r.get(target_name_key, "Unknown")
        if t_type not in targets_by_type:
            targets_by_type[t_type] = []
        if t_name not in targets_by_type[t_type]:
            targets_by_type[t_type].append(t_name)

    # Print abuse commands for each target type
    for target_type, targets in targets_by_type.items():
        commands = get_abuse_commands(edge_type, target_type)
        if not commands:
            continue

        _print_abuse_block(
            edge_type=edge_type,
            target_type=target_type,
            targets=targets,
            commands=commands,
        )


def print_abuse_for_query(
    query_name: str,
    results: list[dict[str, Any]],
    target_key: str = "name",
) -> None:
    """Display abuse commands for query-based findings (Kerberoasting, etc.).

    Args:
        query_name: The query identifier (kerberoastable, asrep, dcsync, etc.)
        results: Query results containing target information
        target_key: Key in result dict for target name
    """
    if not config.show_abuse or config.output_format != "table":
        return

    if not results:
        return

    from hackles.abuse.loader import get_query_abuse_commands

    commands = get_query_abuse_commands(query_name)
    if not commands:
        return

    targets = [r.get(target_key, "Unknown") for r in results if r.get(target_key)]

    _print_query_abuse_block(
        query_name=query_name,
        targets=targets,
        commands=commands,
    )


def _print_abuse_block(
    edge_type: str,
    target_type: str,
    targets: list[str],
    commands: dict[str, Any],
) -> None:
    """Print formatted abuse command block for edge-based attacks."""
    print()
    print(f"    {colors.HEADER}[ABUSE COMMANDS]{colors.END}")
    print(f"    {'=' * 50}")
    print()
    print(f"    {colors.BOLD}Target Type:{colors.END} {target_type} via {edge_type}")

    # Show example targets
    example = targets[0] if targets else "<TARGET>"
    more = f" (+{len(targets) - 1} more)" if len(targets) > 1 else ""
    print(f"    {colors.BOLD}Example:{colors.END} {example}{more}")
    print(f"    {'-' * 50}")

    # Description
    if commands.get("description"):
        print(f"    {commands['description']}")
        print()

    # Commands
    cmd_list = commands.get("commands", [])
    for i, cmd in enumerate(cmd_list, 1):
        name = cmd.get("name", "Command")
        tool = cmd.get("tool", "")
        command = cmd.get("command", "").strip()

        tool_info = f" ({tool})" if tool else ""
        print(f"    {colors.GREEN}[{i}] {name}{tool_info}{colors.END}")

        # Substitute first target as example
        example_cmd = command.replace("<TARGET>", _extract_name(example))
        for line in example_cmd.split("\n"):
            print(f"        {line}")
        print()

    # OPSEC notes
    opsec = commands.get("opsec", [])
    if opsec:
        print(f"    {colors.WARNING}OPSEC:{colors.END}")
        for note in opsec:
            print(f"      - {note}")
        print()


def _print_query_abuse_block(
    query_name: str,
    targets: list[str],
    commands: dict[str, Any],
) -> None:
    """Print formatted abuse command block for query-based attacks."""
    print()
    print(f"    {colors.HEADER}[ABUSE COMMANDS]{colors.END}")
    print(f"    {'=' * 50}")
    print()

    # Show example targets
    example = targets[0] if targets else "<TARGET>"
    more = f" (+{len(targets) - 1} more)" if len(targets) > 1 else ""
    print(f"    {colors.BOLD}Target:{colors.END} {example}{more}")
    print(f"    {'-' * 50}")

    # Description
    if commands.get("description"):
        print(f"    {commands['description']}")
        print()

    # Commands
    cmd_list = commands.get("commands", [])
    for i, cmd in enumerate(cmd_list, 1):
        name = cmd.get("name", "Command")
        tool = cmd.get("tool", "")
        command = cmd.get("command", "").strip()

        tool_info = f" ({tool})" if tool else ""
        print(f"    {colors.GREEN}[{i}] {name}{tool_info}{colors.END}")

        # Substitute first target as example
        example_cmd = command.replace("<TARGET>", _extract_name(example))
        for line in example_cmd.split("\n"):
            print(f"        {line}")
        print()

    # OPSEC notes
    opsec = commands.get("opsec", [])
    if opsec:
        print(f"    {colors.WARNING}OPSEC:{colors.END}")
        for note in opsec:
            print(f"      - {note}")
        print()


def _extract_name(principal: str) -> str:
    """Extract the name part from a principal (before @DOMAIN)."""
    if "@" in principal:
        return principal.split("@")[0]
    return principal
