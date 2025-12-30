"""Owned -> DCSync"""
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
    name="Owned -> DCSync",
    category="Owned",
    default=True,
    severity=Severity.CRITICAL
)
def get_owned_to_dcsync(bh: BloodHoundCE, domain: Optional[str] = None, severity: Severity = None) -> int:
    """Find paths from owned principals to DCSync privileges"""
    query = f"""
    MATCH (owned)
    WHERE (owned:Tag_Owned OR 'owned' IN owned.system_tags OR owned.owned = true)
    WITH owned
    MATCH (d:Domain)
    WITH owned, d
    MATCH p=shortestPath((owned)-[*1..5]->(d))
    WHERE ANY(r IN relationships(p) WHERE type(r) IN ['GetChanges', 'GetChangesAll', 'DCSync', 'AllExtendedRights', 'GenericAll'])
    RETURN owned.name AS owned_principal, {node_type('owned')} AS owned_type,
           d.name AS domain, length(p) AS hops
    ORDER BY length(p)
    LIMIT 20
    """
    results = bh.run_query(query)
    result_count = len(results)

    if not print_header("Owned -> DCSync Privileges", severity, result_count):
        return result_count
    print_subheader(f"Found {result_count} path(s) to DCSync")

    if results:
        print_table(
            ["Owned Principal", "Type", "Target Domain", "Hops"],
            [[r["owned_principal"], r["owned_type"], r["domain"], r["hops"]] for r in results]
        )
        print_abuse_info("DCSync", [{"principal": r["owned_principal"]} for r in results], extract_domain(results, None))

    return result_count
