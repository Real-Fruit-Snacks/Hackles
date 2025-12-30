"""Owned -> DA Session Chain"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from hackles.queries.base import register_query
from hackles.display.colors import Severity
from hackles.display.tables import print_header, print_subheader, print_table, print_warning


if TYPE_CHECKING:
    from hackles.core.bloodhound import BloodHoundCE

@register_query(
    name="Owned -> DA Session Chain",
    category="Owned",
    default=True,
    severity=Severity.CRITICAL
)
def get_owned_to_da_session_chain(bh: BloodHoundCE, domain: Optional[str] = None, severity: Severity = None) -> int:
    """Complete attack chain: owned → admin to computer → DA session"""
    domain_filter = "AND toUpper(o.domain) = toUpper($domain)" if domain else ""
    params = {"domain": domain} if domain else {}

    query = f"""
    MATCH (o)
    WHERE (o:Tag_Owned OR 'owned' IN o.system_tags OR o.owned = true)
    MATCH (o)-[:AdminTo|MemberOf*1..3]->(c:Computer)
    MATCH (c)-[:HasSession]->(da:User)-[:MemberOf*1..]->(g:Group)
    WHERE g.objectid ENDS WITH '-512'
    {domain_filter}
    RETURN DISTINCT o.name AS owned, c.name AS target_computer, da.name AS domain_admin
    """
    results = bh.run_query(query, params)
    result_count = len(results)

    if not print_header("Owned → Admin → DA Session Chain", severity, result_count):
        return result_count
    print_subheader(f"Found {result_count} complete attack chain(s)")

    if results:
        print_warning("[!] Direct path from owned principal to DA credential theft!")
        print_table(
            ["Owned Principal", "Target Computer", "Domain Admin"],
            [[r["owned"], r["target_computer"], r["domain_admin"]] for r in results]
        )

    return result_count
