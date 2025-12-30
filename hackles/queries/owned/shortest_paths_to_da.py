"""Owned -> Domain Admins"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from hackles.queries.base import register_query
from hackles.display.colors import Severity
from hackles.display.tables import print_header, print_subheader, print_table, print_warning
from hackles.core.cypher import node_type


if TYPE_CHECKING:
    from hackles.core.bloodhound import BloodHoundCE

@register_query(
    name="Owned -> Domain Admins",
    category="Owned",
    default=True,
    severity=Severity.CRITICAL
)
def get_shortest_paths_to_da(bh: BloodHoundCE, domain: Optional[str] = None, severity: Severity = None) -> int:
    """Get shortest paths from owned principals to Domain Admins"""
    domain_filter = "AND toUpper(g.domain) = toUpper($domain)" if domain else ""
    params = {"domain": domain} if domain else {}

    query = f"""
    MATCH p=shortestPath((n)-[*1..]->(g:Group))
    WHERE (n:Tag_Owned OR 'owned' IN n.system_tags OR n.owned = true)
    AND (g.objectid ENDS WITH '-512' OR g.objectid ENDS WITH '-519')
    {domain_filter}
    RETURN
        n.name AS start,
        {node_type('n')} AS start_type,
        g.name AS end,
        length(p) AS path_length
    ORDER BY length(p)
    LIMIT 20
    """
    results = bh.run_query(query, params)
    result_count = len(results)

    if not print_header("Shortest Paths: Owned -> Domain Admins", severity, result_count):
        return result_count
    print_subheader(f"Found {result_count} path(s) from owned principals to Domain Admins")

    if results:
        print_warning("[!] These are your attack paths to Domain Admin!")
        print_table(
            ["Start (Owned)", "Type", "Target Group", "Hops"],
            [[r["start"], r["start_type"], r["end"], r["path_length"]] for r in results]
        )

    return result_count
