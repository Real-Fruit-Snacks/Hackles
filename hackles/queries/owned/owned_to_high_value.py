"""Owned -> High Value Targets"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from hackles.queries.base import register_query
from hackles.display.colors import Severity
from hackles.display.tables import print_header, print_subheader, print_table
from hackles.core.cypher import node_type


if TYPE_CHECKING:
    from hackles.core.bloodhound import BloodHoundCE

@register_query(
    name="Owned -> High Value Targets",
    category="Owned",
    default=True,
    severity=Severity.CRITICAL
)
def get_owned_to_high_value(bh: BloodHoundCE, domain: Optional[str] = None, severity: Severity = None) -> int:
    """Find shortest paths from owned principals to any high value target"""
    # Rewritten to avoid cartesian product warning
    # BloodHound CE uses 'admin_tier_0' for tier zero assets
    query = f"""
    MATCH (n)
    WHERE (n:Tag_Owned OR 'owned' IN n.system_tags OR n.owned = true)
    WITH n
    MATCH (hvt)
    WHERE ('admin_tier_0' IN hvt.system_tags OR 'high_value' IN hvt.system_tags OR hvt.highvalue = true)
    AND n <> hvt
    WITH n, hvt
    MATCH p=shortestPath((n)-[*1..]->(hvt))
    RETURN n.name AS owned, {node_type('n')} AS owned_type, hvt.name AS high_value_target, {node_type('hvt')} AS hvt_type, length(p) AS path_length
    ORDER BY length(p)
    LIMIT 20
    """
    results = bh.run_query(query)
    result_count = len(results)

    if not print_header("Shortest Paths: Owned -> High Value Targets", severity, result_count):
        return result_count
    print_subheader(f"Found {result_count} path(s) from owned to high value")

    if results:
        print_table(
            ["Owned Principal", "Type", "High Value Target", "Target Type", "Path Length"],
            [[r["owned"], r["owned_type"], r["high_value_target"], r["hvt_type"], r["path_length"]] for r in results]
        )

    return result_count
