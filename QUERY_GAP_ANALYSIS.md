# Hackles Query & Abuse Template Gap Analysis

**Generated**: 2025-12-29
**Methodology**: Parallel research agents analyzing OSCP+, GOAD lab, BloodHound CE community resources, and SpecterOps documentation

---

## Executive Summary

Hackles has **97 registered queries** and **42 abuse templates**. After comprehensive research:

| Category | Count |
|----------|-------|
| Queries with abuse templates | 41 |
| Queries correctly without templates (informational) | 40 |
| **Queries SHOULD have templates but don't** | 16 |
| **Missing ADCS ESC templates** | 10 |
| **Missing queries (popular in community)** | 12+ |

---

## Part 1: Queries Missing Abuse Templates

These queries identify exploitable vulnerabilities but don't call `print_abuse_info()`:

### HIGH PRIORITY - Should Use Existing Templates

| Query | File | Should Use Template | Why |
|-------|------|---------------------|-----|
| GPO Abuse Paths | `acl/gpo_abuse.py` | `GPOAbuse` | Has write rights on GPO - exploitable |
| Owns Relationships | `acl/owns_relationships.py` | `WriteOwner` | Ownership = full control chain |
| Constrained Delegation (Dangerous) | `delegation/constrained_delegation_dangerous.py` | `ConstrainedDelegation` | LDAP/CIFS to DC = DCSync |
| SID History (Same Domain) | `domain/sid_history_same_domain.py` | `HasSIDHistory` | Persistence indicator |
| ADCS ESC1 Vulnerable | `adcs/esc1_vulnerable.py` | `ADCSESC1` | Template exists, not wired up |
| Owned -> RDP Access | `owned/owned_rdp_access.py` | `CanRDP` | Lateral movement opportunity |
| Owned -> DCSync | `owned/owned_to_dcsync.py` | `DCSync` | Critical attack path |
| Owned -> Kerberoastable | `owned/owned_to_kerberoastable.py` | `Kerberoasting` | Credential harvesting |
| Owned -> Unconstrained | `owned/owned_to_unconstrained.py` | `UnconstrainedDelegation` | TGT theft vector |
| Owned -> ADCS Templates | `owned/owned_to_adcs.py` | `ADCSESC1` (dynamic) | Certificate abuse |

### MEDIUM PRIORITY - Need New Templates

| Query | File | Needs Template | Exploitation Tool |
|-------|------|----------------|-------------------|
| ADCS ESC8 (Web Enrollment) | `adcs/adcs_esc8.py` | `ADCSESC8` | ntlmrelayx + PetitPotam |
| ADCS ESC2/ESC3 Any Purpose | `adcs/any_purpose_templates.py` | `ADCSESC2` | Certipy |
| ADCS ESC15 (CVE-2024-49019) | `adcs/esc15_vulnerable.py` | `ADCSESC15` | Certipy EKUwu |
| Coerce & Relay Edges | `lateral/coerce_relay_edges.py` | `NTLMRelay` | ntlmrelayx + coercion |
| NTLM Relay Targets | `lateral/ntlm_relay_targets.py` | `NTLMRelay` | ntlmrelayx |
| userPassword Attribute | `credentials/userpassword_attribute.py` | `PlaintextPassword` | Direct credential |

---

## Part 2: Missing ADCS Templates

The `adcs_escalation_paths.py` query looks for edges: `ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC5|ADCSESC6a|ADCSESC6b|ADCSESC7|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|ADCSESC13`

**Templates we have:** `ADCSESC1`, `ADCSESC4`

**Templates we need to create:**

| Template | Attack | Exploitation |
|----------|--------|--------------|
| `ADCSESC2` | Any Purpose EKU | `certipy req -template <ANY_PURPOSE>` |
| `ADCSESC3` | Certificate Request Agent | Multi-step enrollment |
| `ADCSESC5` | PKI Object ACL Abuse | Modify PKI objects |
| `ADCSESC6a/b` | CA EDITF_ATTRIBUTESUBJECTALTNAME2 | CA config abuse |
| `ADCSESC7` | ManageCA + Issue | Different from ManageCA alone |
| `ADCSESC8` | Web Enrollment Relay | `ntlmrelayx -t http://CA/certsrv` |
| `ADCSESC9a/b` | GenericWrite + No Security Extension | Shadow creds chain |
| `ADCSESC10a/b` | Weak Certificate Mapping | Certificate impersonation |
| `ADCSESC13` | Issuance Policy OID Abuse | Policy OID bypass |
| `ADCSESC15` | EKUwu (CVE-2024-49019) | Schema v1 SAN abuse |

---

## Part 3: Missing Queries (Community Standards)

Based on research of OSCP+, GOAD, hausec, CompassSecurity, and SpecterOps Query Library:

### HIGH PRIORITY - Common Attack Paths

| Query Name | Description | Cypher Pattern |
|------------|-------------|----------------|
| **DA Sessions on Non-DCs** | Find where to steal DA creds | `(c:Computer)-[:HasSession]->(u:User)-[:MemberOf*1..]->(g {objectid ENDS WITH '-512'}) WHERE NOT c:DC` |
| **Trust Abuse (SID Filtering)** | Trusts without SID filtering | `(d1:Domain)-[r:TrustedBy]->(d2) WHERE r.sidfiltering = false` |
| **Shadow Admins (Nested)** | Indirect admin rights | `(u:User)-[:MemberOf*1..]->(g:Group)-[:AdminTo]->(c:Computer)` |
| **Cross-Domain Ownership** | Foreign domain object control | `(n {domain:'A'})-[:Owns]->(m {domain:'B'})` |
| **Computers to DA** | Shortest path from any computer | `(c:Computer),(g {objectid ENDS WITH '-512'}) shortestPath` |
| **AZUREADSSOACC Account** | Seamless SSO key holder | `(c:Computer) WHERE c.name =~ '(?i).*AZUREADSSOACC.*'` |

### MEDIUM PRIORITY - Statistics & Prioritization

| Query Name | Description | Purpose |
|------------|-------------|---------|
| **Top Controllers** | Objects with most outbound edges | Identify key targets |
| **Busiest Attack Paths** | Most users affected by single path | GoodHound-style prioritization |
| **Stale High-Value Sessions** | Old sessions on HVT | Potentially exploitable |
| **Non-Admin DCSync** | Non-admin with GetChanges+GetChangesAll | Critical finding |
| **Computer-to-Computer Admin** | Admin chains between computers | Lateral movement |
| **Percentage Users with Path to DA** | Risk metric | Executive reporting |

### LOW PRIORITY - Nice to Have

| Query Name | Description |
|------------|-------------|
| Password spray candidates | Users with old passwords + weak policy |
| Service account enumeration | High-priv service accounts |
| AdminSDHolder protected review | Who's protected (and shouldn't be) |
| Duplicate SPNs (Kerberos) | SPN collision issues |
| GPO with interesting keywords | Password/admin/security in name |

---

## Part 4: Templates That Exist But Underutilized

These templates exist but could be used by more queries:

| Template | Used By | Could Also Be Used By |
|----------|---------|----------------------|
| `ADCSESC1` | `adcs_escalation_paths.py` | `esc1_vulnerable.py`, `owned_to_adcs.py` |
| `WriteOwner` | `acl_abuse.py` (dynamic) | `owns_relationships.py` |
| `GPOAbuse` | 3 queries | `gpo_abuse.py` |
| `ConstrainedDelegation` | `constrained_delegation.py` | `constrained_delegation_dangerous.py` |
| `HasSIDHistory` | `sid_history.py` | `sid_history_same_domain.py` |

---

## Part 5: BloodHound CE Edge Documentation

BloodHound CE provides abuse info for these edges (we should have templates for all):

**Traversable Edges with Abuse Info:**
- MemberOf, AdminTo, HasSession, CanRDP, CanPSRemote, ExecuteDCOM
- GenericAll, GenericWrite, WriteDacl, WriteOwner, Owns
- ForceChangePassword, AddMember, AddSelf, AllExtendedRights
- ReadLAPSPassword, ReadGMSAPassword
- AllowedToDelegate, AllowedToAct, AddAllowedToAct
- DCSync, GetChanges, GetChangesAll
- AddKeyCredentialLink, WriteSPN, WriteAccountRestrictions
- SQLAdmin, HasSIDHistory
- ADCSESC1-13, GoldenCert, ManageCA, Enroll, PublishedTo

**We're missing abuse templates for:**
- `WriteAccountRestrictions` (RBCD prerequisite)
- `AddSelf` (self-add to group)
- Several ADCSESC variants (see Part 2)

---

## Part 6: Recommended Actions

### Immediate (Wire up existing templates)

```bash
# Files to modify - add print_abuse_info() calls:
hackles/queries/adcs/esc1_vulnerable.py          # Use ADCSESC1
hackles/queries/acl/gpo_abuse.py                 # Use GPOAbuse
hackles/queries/acl/owns_relationships.py        # Use WriteOwner
hackles/queries/delegation/constrained_delegation_dangerous.py  # Use ConstrainedDelegation
hackles/queries/domain/sid_history_same_domain.py  # Use HasSIDHistory
hackles/queries/owned/owned_rdp_access.py        # Use CanRDP
hackles/queries/owned/owned_to_dcsync.py         # Use DCSync
hackles/queries/owned/owned_to_kerberoastable.py # Use Kerberoasting
hackles/queries/owned/owned_to_unconstrained.py  # Use UnconstrainedDelegation
```

### Short-term (Create missing templates)

```bash
# New templates to create in hackles/abuse/templates/:
adcsesc2.yml      # Any Purpose EKU
adcsesc3.yml      # Certificate Request Agent
adcsesc5.yml      # PKI Object ACL
adcsesc6.yml      # EDITF_ATTRIBUTESUBJECTALTNAME2
adcsesc7.yml      # ManageCA + Issue combined
adcsesc8.yml      # Web Enrollment Relay
adcsesc9.yml      # GenericWrite + No Security Ext
adcsesc10.yml     # Weak Certificate Mapping
adcsesc13.yml     # Issuance Policy Bypass
adcsesc15.yml     # EKUwu CVE-2024-49019
ntlmrelay.yml     # NTLM relay attacks
plaintextpassword.yml  # userPassword attribute
writeaccountrestrictions.yml  # RBCD prereq
addself.yml       # Self-add to group
```

### Medium-term (New queries)

Priority order:
1. DA Sessions on Non-DCs (critical for cred theft)
2. Trust SID Filtering Analysis (cross-domain escalation)
3. Shadow Admin Detection (nested groups)
4. Cross-Domain Ownership (multi-domain attacks)
5. Busiest Path Analysis (prioritization)
6. AZUREADSSOACC Detection (Azure SSO key)

---

## Part 7: Tool Comparison

### What We Have vs. Community Tools

| Feature | Hackles | PlumHound | GoodHound | Max |
|---------|---------|-----------|-----------|-----|
| Query count | 97 | 100+ | N/A | N/A |
| Abuse templates | 42 | No | No | No |
| HTML reports | No | Yes | Yes | No |
| Path prioritization | No | No | Yes | No |
| Batch marking owned | No | No | No | Yes |
| Wave analysis | No | No | No | Yes |

### Unique Value Propositions
- **Hackles**: Only tool with integrated abuse command templates
- **PlumHound**: Best for batch reporting
- **GoodHound**: Best for remediation prioritization
- **Max**: Best for compromise tracking

---

## Sources

- [SpecterOps Query Library](https://queries.specterops.io/) - 170+ queries
- [hausec Cypher Cheatsheet](https://hausec.com/2019/09/09/bloodhound-cypher-cheatsheet/)
- [CompassSecurity BloodHound CE Queries](https://github.com/CompassSecurity/bloodhoundce-resources)
- [GOAD Lab Walkthroughs](https://mayfly277.github.io/categories/goad/)
- [BloodHound Edge Documentation](https://bloodhound.specterops.io/resources/edges/overview)
- [Certipy ADCS Wiki](https://github.com/ly4k/Certipy/wiki)
- [The Hacker Recipes - AD](https://www.thehacker.recipes/ad/)
- [HackTricks - AD Methodology](https://book.hacktricks.xyz/windows-hardening/active-directory-methodology)
