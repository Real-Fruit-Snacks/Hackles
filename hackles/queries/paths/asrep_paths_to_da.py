"""Shortest Paths: AS-REP Roastable -> DA"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from hackles.queries.base import register_query
from hackles.display.colors import Severity
from hackles.display.tables import print_header, print_subheader, print_table, print_warning
from hackles.abuse.printer import print_abuse_info


if TYPE_CHECKING:
    from hackles.core.bloodhound import BloodHoundCE

@register_query(
    name="Shortest Paths: AS-REP Roastable -> DA",
    category="Attack Paths",
    default=True,
    severity=Severity.CRITICAL
)
def get_asrep_paths_to_da(bh: BloodHoundCE, domain: Optional[str] = None, severity: Severity = None) -> int:
    """Find shortest paths from AS-REP roastable users to Domain Admins"""
    domain_filter = "AND toUpper(u.domain) = toUpper($domain)" if domain else ""
    params = {"domain": domain} if domain else {}

    # Rewritten to avoid cartesian product warning
    query = f"""
    MATCH (u:User {{dontreqpreauth: true}})
    WHERE u.enabled = true
    {domain_filter}
    WITH u
    MATCH (g:Group)
    WHERE g.objectid ENDS WITH '-512' OR g.objectid ENDS WITH '-519'
    WITH u, g
    MATCH p=shortestPath((u)-[*1..]->(g))
    RETURN u.name AS user, g.name AS target_group, length(p) AS path_length
    ORDER BY length(p)
    LIMIT 20
    """
    results = bh.run_query(query, params)
    result_count = len(results)

    if not print_header("Shortest Paths: AS-REP Roastable -> Domain Admins", severity, result_count):
        return result_count
    print_subheader(f"Found {result_count} path(s) from AS-REP roastable to DA")

    if results:
        print_warning("AS-REP roast these users, crack password, then follow path to DA!")
        print_table(
            ["AS-REP User", "Target Group", "Path Length"],
            [[r["user"], r["target_group"], r["path_length"]] for r in results]
        )
        print_abuse_info("ASREPRoasting", [{"name": r["user"]} for r in results], domain)

    return result_count
