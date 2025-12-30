"""Stale Accounts (90+ days)"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from hackles.queries.base import register_query
from hackles.display.colors import Severity
from hackles.display.tables import print_header, print_subheader, print_table
import time


if TYPE_CHECKING:
    from hackles.core.bloodhound import BloodHoundCE

@register_query(
    name="Stale Accounts (90+ days)",
    category="Security Hygiene",
    default=True,
    severity=Severity.LOW
)
def get_stale_accounts(bh: BloodHoundCE, domain: Optional[str] = None, severity: Severity = None) -> int:
    """Get stale user accounts (no login in 90+ days)"""
    domain_filter = "AND toUpper(u.domain) = toUpper($domain)" if domain else ""
    params = {"domain": domain} if domain else {}

    # Calculate 90 days ago in epoch (approximate)
    import time
    ninety_days_ago = int(time.time()) - (90 * 24 * 60 * 60)

    query = f"""
    MATCH (u:User)
    WHERE u.enabled = true
    AND u.lastlogon < $cutoff
    AND u.lastlogon > 0
    {domain_filter}
    RETURN
        u.name AS name,
        u.displayname AS displayname,
        u.admincount AS admincount,
        u.lastlogon AS lastlogon,
        u.pwdlastset AS pwdlastset
    ORDER BY u.lastlogon
    LIMIT 50
    """
    params["cutoff"] = ninety_days_ago
    results = bh.run_query(query, params)
    result_count = len(results)

    if not print_header("Stale User Accounts (90+ days)", severity, result_count):
        return result_count
    print_subheader(f"Found {result_count} stale account(s) (limit 50)")

    if results:
        # Convert epoch to readable dates
        def epoch_to_date(epoch):
            if epoch and epoch > 0:
                try:
                    return time.strftime('%Y-%m-%d', time.localtime(epoch))
                except:
                    return "Unknown"
            return "Never"

        print_table(
            ["User", "Display Name", "Admin", "Last Login", "Pwd Last Set"],
            [[r["name"], r["displayname"], r["admincount"],
              epoch_to_date(r["lastlogon"]), epoch_to_date(r["pwdlastset"])] for r in results]
        )

    return result_count
