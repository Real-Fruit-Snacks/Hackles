"""Kerberoastable Users"""
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
    name="Kerberoastable Users",
    category="Privilege Escalation",
    default=True,
    severity=Severity.HIGH
)
def get_kerberoastable(bh: BloodHoundCE, domain: Optional[str] = None, severity: Severity = None) -> int:
    """Get Kerberoastable users (hasspn=true)"""
    domain_filter = "AND toUpper(u.domain) = toUpper($domain)" if domain else ""
    params = {"domain": domain} if domain else {}

    query = f"""
    MATCH (u:User {{hasspn: true}})
    WHERE NOT u.name STARTS WITH 'KRBTGT'
    {domain_filter}
    RETURN
        u.name AS name,
        u.displayname AS displayname,
        u.enabled AS enabled,
        u.admincount AS admincount,
        u.description AS description,
        u.serviceprincipalnames AS spns
    ORDER BY u.admincount DESC, u.name
    """
    results = bh.run_query(query, params)
    result_count = len(results)

    if not print_header("Kerberoastable Users (SPN Set)", severity, result_count):
        return result_count
    print_subheader(f"Found {result_count} Kerberoastable user(s)")

    if results:
        # Highlight admin accounts
        admin_count = sum(1 for r in results if r.get("admincount"))
        if admin_count:
            print_warning(f"[!] {admin_count} are admin accounts!")

        print_table(
            ["Name", "Display Name", "Enabled", "Admin", "SPN"],
            [[r["name"], r["displayname"], r["enabled"], r["admincount"], r["spns"]] for r in results]
        )
        print_abuse_info("Kerberoasting", results, extract_domain(results, domain))

    return result_count
