"""Owns Relationships (Non-Admin)"""
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
    name="Owns Relationships (Non-Admin)",
    category="ACL Abuse",
    default=True,
    severity=Severity.HIGH
)
def get_owns_relationships(bh: BloodHoundCE, domain: Optional[str] = None, severity: Severity = None) -> int:
    """Object ownership relationships (owners can grant themselves any permissions)"""
    domain_filter = "AND toUpper(n.domain) = toUpper($domain)" if domain else ""
    params = {"domain": domain} if domain else {}

    query = f"""
    MATCH (n)-[:Owns]->(m)
    WHERE NOT n.objectid ENDS WITH '-512'
      AND NOT n.objectid ENDS WITH '-519'
      AND NOT n.objectid ENDS WITH '-544'
    {domain_filter}
    RETURN n.name AS owner, labels(n)[1] AS owner_type,
           m.name AS owned_object, labels(m)[1] AS object_type
    ORDER BY labels(n)[1], n.name
    LIMIT 100
    """
    results = bh.run_query(query, params)
    result_count = len(results)

    if not print_header("Owns Relationships", severity, result_count):
        return result_count
    print_subheader(f"Found {result_count} ownership relationship(s)")

    if results:
        print_warning("[!] Object owners can grant themselves any permissions!")
        print_table(
            ["Owner", "Owner Type", "Owned Object", "Object Type"],
            [[r["owner"], r["owner_type"], r["owned_object"], r["object_type"]] for r in results]
        )
        print_abuse_info("WriteOwner", results, extract_domain(results, domain))

    return result_count
