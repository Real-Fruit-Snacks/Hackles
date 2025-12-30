"""Domain Statistics"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from hackles.queries.base import register_query
from hackles.display.colors import Colors, Severity
from hackles.display.tables import print_header, print_subheader, print_table
from hackles.core.config import config


if TYPE_CHECKING:
    from hackles.core.bloodhound import BloodHoundCE

@register_query(
    name="Domain Statistics",
    category="Basic Info",
    default=True,
    severity=Severity.INFO
)
def get_domain_stats(bh: BloodHoundCE, domain: Optional[str] = None, severity: Severity = None) -> int:
    """Get statistics for a domain"""
    domain_filter = "WHERE toUpper(n.domain) = toUpper($domain)" if domain else ""
    params = {"domain": domain} if domain else {}

    print_header("Domain Statistics", severity, 1)  # Always show as has content

    # User stats
    query = f"""
    MATCH (n:User) {domain_filter}
    RETURN
        count(n) AS total,
        sum(CASE WHEN n.enabled = true THEN 1 ELSE 0 END) AS enabled,
        sum(CASE WHEN n.enabled = false THEN 1 ELSE 0 END) AS disabled,
        sum(CASE WHEN n.pwdneverexpires = true THEN 1 ELSE 0 END) AS pwd_never_expires,
        sum(CASE WHEN n.passwordnotreqd = true THEN 1 ELSE 0 END) AS pwd_not_required
    """
    results = bh.run_query(query, params)
    if results:
        r = results[0]
        print_subheader("Users")
        print_table(
            ["Metric", "Count"],
            [
                ["Total Users", r["total"]],
                ["Enabled", r["enabled"]],
                ["Disabled", r["disabled"]],
                ["Password Never Expires", r["pwd_never_expires"]],
                ["Password Not Required", r["pwd_not_required"]]
            ]
        )

    # Computer stats
    query = f"""
    MATCH (n:Computer) {domain_filter}
    RETURN
        count(n) AS total,
        sum(CASE WHEN n.enabled = true THEN 1 ELSE 0 END) AS enabled,
        sum(CASE WHEN n.haslaps = true THEN 1 ELSE 0 END) AS has_laps
    """
    results = bh.run_query(query, params)
    if results:
        r = results[0]
        print_subheader("Computers")
        print_table(
            ["Metric", "Count"],
            [
                ["Total Computers", r["total"]],
                ["Enabled", r["enabled"]],
                ["LAPS Enabled", r["has_laps"]]
            ]
        )

    # Group stats
    query = f"""
    MATCH (n:Group) {domain_filter}
    RETURN count(n) AS total
    """
    results = bh.run_query(query, params)
    if results:
        print_subheader(f"Groups: {results[0]['total']}")

    # Risk scoring
    from hackles.core.scoring import calculate_exposure_metrics, calculate_risk_score, get_risk_rating
    metrics = calculate_exposure_metrics(bh, domain)
    score = calculate_risk_score(metrics)
    rating = get_risk_rating(score)

    # Color-coded risk rating
    rating_colors = {
        "CRITICAL": Colors.FAIL,
        "HIGH": Colors.FAIL,
        "MEDIUM": Colors.WARNING,
        "LOW": Colors.GREEN,
        "MINIMAL": Colors.GREEN,
    }
    color = rating_colors.get(rating, Colors.END)

    print_subheader("Risk Assessment")
    if config.output_format == 'table':
        print(f"    Risk Score: {color}{score}/100 ({rating}){Colors.END}")
        print()

    risk_data = [
        ["Users with path to DA", f"{metrics.get('users_with_path_to_da', 0)} ({metrics.get('pct_users_with_path_to_da', 0)}%)"],
        ["Computers without LAPS", f"{metrics.get('computers_without_laps', 0)} ({metrics.get('pct_computers_without_laps', 0)}%)"],
        ["Kerberoastable Admins", metrics.get("kerberoastable_admins", 0)],
        ["AS-REP Roastable Users", metrics.get("asrep_roastable", 0)],
        ["Unconstrained Delegation (non-DC)", metrics.get("unconstrained_delegation_non_dc", 0)],
        ["Domain Admin Count", metrics.get("domain_admin_count", 0)],
        ["Tier Zero Objects", metrics.get("tier_zero_count", 0)],
    ]
    print_table(["Metric", "Value"], risk_data)

    return 1  # Domain stats always returns 1 (metadata query)
