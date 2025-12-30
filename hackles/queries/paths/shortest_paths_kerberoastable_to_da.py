"""Shortest Paths: Kerberoastable -> DA"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from hackles.queries.base import register_query
from hackles.display.colors import Severity
from hackles.display.tables import print_header, print_subheader, print_table, print_warning
from hackles.abuse.printer import print_abuse_info
from hackles.core.utils import extract_domain

if TYPE_CHECKING:
    from hackles.core.bloodhound import BloodHoundCE


@register_query(
    name="Shortest Paths: Kerberoastable -> DA",
    category="Attack Paths",
    default=True,
    severity=Severity.CRITICAL
)
def get_shortest_paths_kerberoastable_to_da(bh: BloodHoundCE, domain: Optional[str] = None, severity: Severity = None) -> int:
    """Get shortest paths from Kerberoastable users to Domain Admins"""
    domain_filter = "AND toUpper(g.domain) = toUpper($domain)" if domain else ""
    params = {"domain": domain} if domain else {}

    query = f"""
    MATCH p=shortestPath((u:User {{hasspn: true}})-[*1..]->(g:Group))
    WHERE NOT u.name STARTS WITH 'KRBTGT'
    AND (g.objectid ENDS WITH '-512' OR g.objectid ENDS WITH '-519')
    {domain_filter}
    RETURN
        u.name AS user,
        g.name AS target_group,
        length(p) AS path_length
    ORDER BY length(p)
    LIMIT 20
    """
    results = bh.run_query(query, params)
    result_count = len(results)

    if not print_header("Shortest Paths: Kerberoastable -> Domain Admins", severity, result_count):
        return result_count
    print_subheader(f"Found {result_count} path(s) from Kerberoastable users to Domain Admins")

    if results:
        print_warning("[!] Prioritize cracking these accounts - they lead to DA!")
        print_table(
            ["Kerberoastable User", "Target Group", "Hops"],
            [[r["user"], r["target_group"], r["path_length"]] for r in results]
        )
        print_abuse_info("Kerberoasting", results, extract_domain(results, domain))

    return result_count
