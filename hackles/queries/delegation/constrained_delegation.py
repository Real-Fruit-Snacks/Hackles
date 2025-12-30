"""Constrained Delegation"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from hackles.queries.base import register_query
from hackles.display.colors import Severity
from hackles.display.tables import print_header, print_subheader, print_table
from hackles.abuse.printer import print_abuse_info
from hackles.core.utils import extract_domain

if TYPE_CHECKING:
    from hackles.core.bloodhound import BloodHoundCE


@register_query(
    name="Constrained Delegation",
    category="Delegation",
    default=True,
    severity=Severity.MEDIUM
)
def get_constrained_delegation(bh: BloodHoundCE, domain: Optional[str] = None, severity: Severity = None) -> int:
    """Get users and computers with constrained delegation"""
    domain_filter = "AND toUpper(n.domain) = toUpper($domain)" if domain else ""
    params = {"domain": domain} if domain else {}

    # Users with constrained delegation
    query = f"""
    MATCH (n:User)
    WHERE n.allowedtodelegate IS NOT NULL AND size(n.allowedtodelegate) > 0
    {domain_filter}
    RETURN
        n.name AS name,
        'User' AS type,
        n.allowedtodelegate AS targets,
        n.enabled AS enabled
    ORDER BY n.name
    """
    user_results = bh.run_query(query, params)

    # Computers with constrained delegation
    query = f"""
    MATCH (n:Computer)
    WHERE n.allowedtodelegate IS NOT NULL AND size(n.allowedtodelegate) > 0
    {domain_filter}
    RETURN
        n.name AS name,
        'Computer' AS type,
        n.allowedtodelegate AS targets,
        n.enabled AS enabled
    ORDER BY n.name
    """
    computer_results = bh.run_query(query, params)

    all_results = user_results + computer_results
    result_count = len(all_results)

    if not print_header("Constrained Delegation", severity, result_count):
        return result_count
    print_subheader(f"Found {result_count} object(s) with constrained delegation")

    if all_results:
        print_table(
            ["Name", "Type", "Delegation Targets", "Enabled"],
            [[r["name"], r["type"], r["targets"], r["enabled"]] for r in all_results]
        )
        print_abuse_info("ConstrainedDelegation", all_results, extract_domain(all_results, domain))

    return result_count
