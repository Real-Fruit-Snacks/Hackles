"""Owned -> ADCS Templates"""
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
    name="Owned -> ADCS Templates",
    category="Owned",
    default=True,
    severity=Severity.HIGH
)
def get_owned_to_adcs(bh: BloodHoundCE, domain: Optional[str] = None, severity: Severity = None) -> int:
    """Find paths from owned principals to ADCS escalation (ESC1, ESC4, etc.)"""
    query = f"""
    MATCH (owned)
    WHERE (owned:Tag_Owned OR 'owned' IN owned.system_tags OR owned.owned = true)
    WITH owned
    MATCH p=(owned)-[*1..5]->(template:CertTemplate)-[:PublishedTo]->(ca:EnterpriseCA)
    WHERE template.enrolleesuppliessubject = true
    OR template.authenticationenabled = true
    RETURN owned.name AS owned_principal, {node_type('owned')} AS owned_type,
           template.name AS template, ca.name AS ca, length(p) AS hops
    ORDER BY length(p)
    LIMIT 20
    """
    results = bh.run_query(query)
    result_count = len(results)

    if not print_header("Owned -> ADCS Templates", severity, result_count):
        return result_count
    print_subheader(f"Found {result_count} path(s) to certificate templates")

    if results:
        print_table(
            ["Owned Principal", "Type", "Template", "CA", "Hops"],
            [[r["owned_principal"], r["owned_type"], r["template"], r["ca"], r["hops"]] for r in results]
        )
        print_abuse_info("ADCSESC1", [{"principal": r["owned_principal"], "template": r["template"], "ca": r["ca"]} for r in results], extract_domain(results, None))

    return result_count
