"""Owned -> Kerberoastable"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from hackles.queries.base import register_query
from hackles.display.colors import Severity
from hackles.display.tables import print_header, print_subheader, print_table
from hackles.abuse.printer import print_abuse_info
from hackles.core.cypher import node_type
from hackles.core.utils import extract_domain


if TYPE_CHECKING:
    from hackles.core.bloodhound import BloodHoundCE

@register_query(
    name="Owned -> Kerberoastable",
    category="Owned",
    default=True,
    severity=Severity.HIGH
)
def get_owned_to_kerberoastable(bh: BloodHoundCE, domain: Optional[str] = None, severity: Severity = None) -> int:
    """Find paths from owned principals to kerberoastable users"""
    query = f"""
    MATCH (owned)
    WHERE (owned:Tag_Owned OR 'owned' IN owned.system_tags OR owned.owned = true)
    WITH owned
    MATCH (target:User {{hasspn: true, enabled: true}})
    WHERE NOT target.name STARTS WITH 'KRBTGT'
    AND owned <> target
    WITH owned, target
    MATCH p=shortestPath((owned)-[*1..5]->(target))
    RETURN owned.name AS owned_principal, {node_type('owned')} AS owned_type,
           target.name AS kerberoastable_user, length(p) AS hops
    ORDER BY length(p)
    LIMIT 25
    """
    results = bh.run_query(query)
    result_count = len(results)

    if not print_header("Owned -> Kerberoastable Users", severity, result_count):
        return result_count
    print_subheader(f"Found {result_count} path(s) to kerberoastable users")

    if results:
        print_table(
            ["Owned Principal", "Type", "Kerberoastable User", "Hops"],
            [[r["owned_principal"], r["owned_type"], r["kerberoastable_user"], r["hops"]] for r in results]
        )
        print_abuse_info("Kerberoasting", [{"name": r["kerberoastable_user"]} for r in results], extract_domain(results, None))

    return result_count
