#!/bin/bash
# Comprehensive Hackles Feature Test Script
# All commands use --debug and tee output to Output.txt

# Configuration - EDIT THESE VALUES
USERNAME="neo4j"       # Your Neo4j username
PASSWORD="${NEO4J_PASSWORD:-bloodhound}"  # Your Neo4j password (or set NEO4J_PASSWORD env var)
OUTPUT="${OUTPUT_FILE:-./Output.txt}"
BOLT="bolt://127.0.0.1:7687"

# Create/clear output file
echo "=== Hackles Feature Test - $(date) ===" > "$OUTPUT"

# Helper function to run commands with debug and logging
run_test() {
    local desc="$1"
    shift
    echo "" | tee -a "$OUTPUT"
    echo "========================================" | tee -a "$OUTPUT"
    echo "TEST: $desc" | tee -a "$OUTPUT"
    echo "CMD: python3 -m hackles -u $USERNAME $@" | tee -a "$OUTPUT"
    echo "========================================" | tee -a "$OUTPUT"
    python3 -m hackles -u "$USERNAME" "$@" 2>&1 | tee -a "$OUTPUT"
    echo "" | tee -a "$OUTPUT"
}

cd "$(dirname "$0")"

# ===========================================================
# SECTION 1: BASIC CONNECTION & DOMAIN INFO
# ===========================================================
echo "=== SECTION 1: BASIC CONNECTION ===" | tee -a "$OUTPUT"

run_test "List Domains" \
    -p "$PASSWORD" -b "$BOLT" --debug -l

run_test "Domain Statistics" \
    -p "$PASSWORD" -b "$BOLT" --debug --stats

# ===========================================================
# SECTION 2: NODE SEARCH & INFO
# ===========================================================
echo "=== SECTION 2: NODE SEARCH & INFO ===" | tee -a "$OUTPUT"

run_test "Search for Admin users" \
    -p "$PASSWORD" -b "$BOLT" --debug --search '*ADMIN*'

run_test "Search for Domain Controllers" \
    -p "$PASSWORD" -b "$BOLT" --debug --search '*DC*'

run_test "Search for Service Accounts" \
    -p "$PASSWORD" -b "$BOLT" --debug --search '*SVC*'

run_test "Search for SQL" \
    -p "$PASSWORD" -b "$BOLT" --debug --search '*SQL*'

# Get a sample user for further tests (will need manual adjustment)
run_test "Search all users" \
    -p "$PASSWORD" -b "$BOLT" --debug --search '*@*'

# ===========================================================
# SECTION 3: QUICK FILTERS (standalone queries)
# ===========================================================
echo "=== SECTION 3: QUICK FILTERS ===" | tee -a "$OUTPUT"

run_test "Kerberoastable Users" \
    -p "$PASSWORD" -b "$BOLT" --debug --kerberoastable

run_test "AS-REP Roastable Users" \
    -p "$PASSWORD" -b "$BOLT" --debug --asrep

run_test "Unconstrained Delegation" \
    -p "$PASSWORD" -b "$BOLT" --debug --unconstrained

run_test "Computers Without LAPS" \
    -p "$PASSWORD" -b "$BOLT" --debug --no-laps

# ===========================================================
# SECTION 4: QUERY CATEGORIES (individual)
# ===========================================================
echo "=== SECTION 4: QUERY CATEGORIES ===" | tee -a "$OUTPUT"

run_test "ACL Abuse Queries" \
    -p "$PASSWORD" -b "$BOLT" --debug --acl

run_test "ADCS Queries" \
    -p "$PASSWORD" -b "$BOLT" --debug --adcs

run_test "Privilege Escalation Queries" \
    -p "$PASSWORD" -b "$BOLT" --debug --privesc

run_test "Delegation Queries" \
    -p "$PASSWORD" -b "$BOLT" --debug --delegation

run_test "Lateral Movement Queries" \
    -p "$PASSWORD" -b "$BOLT" --debug --lateral

run_test "Security Hygiene Queries" \
    -p "$PASSWORD" -b "$BOLT" --debug --hygiene

run_test "Dangerous Groups Queries" \
    -p "$PASSWORD" -b "$BOLT" --debug --groups

run_test "Basic Info Queries" \
    -p "$PASSWORD" -b "$BOLT" --debug --basic

run_test "Attack Paths Queries" \
    -p "$PASSWORD" -b "$BOLT" --debug --attack-paths

run_test "Owned Queries" \
    -p "$PASSWORD" -b "$BOLT" --debug --owned-queries

run_test "Azure/Hybrid Queries" \
    -p "$PASSWORD" -b "$BOLT" --debug --azure

run_test "Exchange Queries" \
    -p "$PASSWORD" -b "$BOLT" --debug --exchange

run_test "Miscellaneous Queries" \
    -p "$PASSWORD" -b "$BOLT" --debug --misc

# ===========================================================
# SECTION 5: COMBINED CATEGORIES
# ===========================================================
echo "=== SECTION 5: COMBINED CATEGORIES ===" | tee -a "$OUTPUT"

run_test "ACL + ADCS Combined" \
    -p "$PASSWORD" -b "$BOLT" --debug --acl --adcs

run_test "PrivEsc + Delegation + Lateral" \
    -p "$PASSWORD" -b "$BOLT" --debug --privesc --delegation --lateral

# ===========================================================
# SECTION 6: ALL QUERIES WITH OPTIONS
# ===========================================================
echo "=== SECTION 6: ALL QUERIES ===" | tee -a "$OUTPUT"

run_test "All Queries (default)" \
    -p "$PASSWORD" -b "$BOLT" --debug -a

run_test "All Queries with Abuse Info" \
    -p "$PASSWORD" -b "$BOLT" --debug -a --abuse

run_test "All Queries Quiet Mode" \
    -p "$PASSWORD" -b "$BOLT" --debug -a -q

run_test "All Queries with Progress Bar" \
    -p "$PASSWORD" -b "$BOLT" --debug -a --progress

# ===========================================================
# SECTION 7: SEVERITY FILTERING
# ===========================================================
echo "=== SECTION 7: SEVERITY FILTERING ===" | tee -a "$OUTPUT"

run_test "Critical Severity Only" \
    -p "$PASSWORD" -b "$BOLT" --debug -a --severity CRITICAL

run_test "Critical + High Severity" \
    -p "$PASSWORD" -b "$BOLT" --debug -a --severity CRITICAL,HIGH

run_test "Medium + Low Severity" \
    -p "$PASSWORD" -b "$BOLT" --debug -a --severity MEDIUM,LOW

run_test "Info Severity Only" \
    -p "$PASSWORD" -b "$BOLT" --debug -a --severity INFO

# ===========================================================
# SECTION 8: OUTPUT FORMATS
# ===========================================================
echo "=== SECTION 8: OUTPUT FORMATS ===" | tee -a "$OUTPUT"

run_test "JSON Output (subset)" \
    -p "$PASSWORD" -b "$BOLT" --debug --json --acl

run_test "CSV Output (subset)" \
    -p "$PASSWORD" -b "$BOLT" --debug --csv --acl

run_test "HTML Report Generation" \
    -p "$PASSWORD" -b "$BOLT" --debug --html /tmp/hackles_test_report.html -a

echo "HTML report saved to /tmp/hackles_test_report.html" | tee -a "$OUTPUT"

run_test "No Color Output" \
    -p "$PASSWORD" -b "$BOLT" --debug --no-color --acl

# ===========================================================
# SECTION 9: GROUP & MEMBERSHIP
# ===========================================================
echo "=== SECTION 9: GROUP & MEMBERSHIP ===" | tee -a "$OUTPUT"

run_test "Domain Admins Members" \
    -p "$PASSWORD" -b "$BOLT" --debug --members 'DOMAIN ADMINS@BUILDINGMAGIC.LOCAL'

run_test "Administrators Members" \
    -p "$PASSWORD" -b "$BOLT" --debug --members 'ADMINISTRATORS@BUILDINGMAGIC.LOCAL'

run_test "User Group Memberships (R.HAGGARD)" \
    -p "$PASSWORD" -b "$BOLT" --debug --memberof 'R.HAGGARD@BUILDINGMAGIC.LOCAL'

run_test "User Group Memberships (A.FLATCH - Admin)" \
    -p "$PASSWORD" -b "$BOLT" --debug --memberof 'A.FLATCH@BUILDINGMAGIC.LOCAL'

# ===========================================================
# SECTION 10: ADMIN RIGHTS
# ===========================================================
echo "=== SECTION 10: ADMIN RIGHTS ===" | tee -a "$OUTPUT"

run_test "Admins To DC" \
    -p "$PASSWORD" -b "$BOLT" --debug --adminto 'DC01.BUILDINGMAGIC.LOCAL'

run_test "Admin Of (A.FLATCH - Domain Admin)" \
    -p "$PASSWORD" -b "$BOLT" --debug --adminof 'A.FLATCH@BUILDINGMAGIC.LOCAL'

run_test "Admin Of (ADMINISTRATOR)" \
    -p "$PASSWORD" -b "$BOLT" --debug --adminof 'ADMINISTRATOR@BUILDINGMAGIC.LOCAL'

run_test "Sessions On DC" \
    -p "$PASSWORD" -b "$BOLT" --debug --sessions 'DC01.BUILDINGMAGIC.LOCAL'

# ===========================================================
# SECTION 11: EDGE EXPLORATION
# ===========================================================
echo "=== SECTION 11: EDGE EXPLORATION ===" | tee -a "$OUTPUT"

run_test "Edges From R.HAGGARD (has ForceChangePassword)" \
    -p "$PASSWORD" -b "$BOLT" --debug --edges-from 'R.HAGGARD@BUILDINGMAGIC.LOCAL'

run_test "Edges From A.FLATCH (Domain Admin)" \
    -p "$PASSWORD" -b "$BOLT" --debug --edges-from 'A.FLATCH@BUILDINGMAGIC.LOCAL'

run_test "Edges To DC01" \
    -p "$PASSWORD" -b "$BOLT" --debug --edges-to 'DC01.BUILDINGMAGIC.LOCAL'

run_test "Edges To H.POTCH (target of ForceChangePassword)" \
    -p "$PASSWORD" -b "$BOLT" --debug --edges-to 'H.POTCH@BUILDINGMAGIC.LOCAL'

# ===========================================================
# SECTION 12: PATH FINDING
# ===========================================================
echo "=== SECTION 12: PATH FINDING ===" | tee -a "$OUTPUT"

run_test "Path R.HAGGARD to DC01" \
    -p "$PASSWORD" -b "$BOLT" --debug --path 'R.HAGGARD@BUILDINGMAGIC.LOCAL' 'DC01.BUILDINGMAGIC.LOCAL'

run_test "Path R.HAGGARD to H.POTCH" \
    -p "$PASSWORD" -b "$BOLT" --debug --path 'R.HAGGARD@BUILDINGMAGIC.LOCAL' 'H.POTCH@BUILDINGMAGIC.LOCAL'

run_test "Path To Domain Admin (R.HAGGARD)" \
    -p "$PASSWORD" -b "$BOLT" --debug --path-to-da 'R.HAGGARD@BUILDINGMAGIC.LOCAL'

run_test "Path To Domain Admin (R.WIDDLETON)" \
    -p "$PASSWORD" -b "$BOLT" --debug --path-to-da 'R.WIDDLETON@BUILDINGMAGIC.LOCAL'

run_test "Path To Domain Controller (R.HAGGARD)" \
    -p "$PASSWORD" -b "$BOLT" --debug --path-to-dc 'R.HAGGARD@BUILDINGMAGIC.LOCAL'

# ===========================================================
# SECTION 13: NODE INFO
# ===========================================================
echo "=== SECTION 13: NODE INFO ===" | tee -a "$OUTPUT"

run_test "Node Info - R.HAGGARD (Kerberoastable, Owned)" \
    -p "$PASSWORD" -b "$BOLT" --debug --info 'R.HAGGARD@BUILDINGMAGIC.LOCAL'

run_test "Node Info - A.FLATCH (Domain Admin, PASSWD_NOTREQD)" \
    -p "$PASSWORD" -b "$BOLT" --debug --info 'A.FLATCH@BUILDINGMAGIC.LOCAL'

run_test "Node Info - DC01" \
    -p "$PASSWORD" -b "$BOLT" --debug --info 'DC01.BUILDINGMAGIC.LOCAL'

run_test "Node Info - Domain Admins Group" \
    -p "$PASSWORD" -b "$BOLT" --debug --info 'DOMAIN ADMINS@BUILDINGMAGIC.LOCAL'

# ===========================================================
# SECTION 14: OWNED MANAGEMENT
# ===========================================================
echo "=== SECTION 14: OWNED MANAGEMENT ===" | tee -a "$OUTPUT"

# Mark H.GRANGON as owned (not currently owned)
run_test "Mark H.GRANGON as Owned" \
    -p "$PASSWORD" -b "$BOLT" --debug -o 'H.GRANGON@BUILDINGMAGIC.LOCAL'

# Show owned principals
run_test "Show Owned Principals After Mark" \
    -p "$PASSWORD" -b "$BOLT" --debug --owned-queries

# Unmark H.GRANGON
run_test "Unmark H.GRANGON" \
    -p "$PASSWORD" -b "$BOLT" --debug --unown 'H.GRANGON@BUILDINGMAGIC.LOCAL'

# Show owned principals again
run_test "Show Owned Principals After Unmark" \
    -p "$PASSWORD" -b "$BOLT" --debug --owned-queries

# Note: Skipping --clear-owned to preserve existing owned markers

# ===========================================================
# SECTION 15: TIER ZERO MANAGEMENT
# ===========================================================
echo "=== SECTION 15: TIER ZERO MANAGEMENT ===" | tee -a "$OUTPUT"

# Mark R.HAGGARD as Tier Zero (Kerberoastable user - testing)
run_test "Mark R.HAGGARD as Tier Zero" \
    -p "$PASSWORD" -b "$BOLT" --debug --tier-zero 'R.HAGGARD@BUILDINGMAGIC.LOCAL'

# Show High Value Targets (should include R.HAGGARD now)
run_test "Show High Value Targets After Mark" \
    -p "$PASSWORD" -b "$BOLT" --debug --basic

# Unmark R.HAGGARD from Tier Zero
run_test "Unmark R.HAGGARD from Tier Zero" \
    -p "$PASSWORD" -b "$BOLT" --debug --untier-zero 'R.HAGGARD@BUILDINGMAGIC.LOCAL'

# ===========================================================
# SECTION 16: DOMAIN FILTERING
# ===========================================================
echo "=== SECTION 16: DOMAIN FILTERING ===" | tee -a "$OUTPUT"

run_test "Filter by Domain (subset of queries)" \
    -p "$PASSWORD" -b "$BOLT" --debug -d 'BUILDINGMAGIC.LOCAL' --privesc

# ===========================================================
# SECTION 17: CUSTOM QUERIES
# ===========================================================
echo "=== SECTION 17: CUSTOM QUERIES ===" | tee -a "$OUTPUT"

# Create a sample custom query
mkdir -p /tmp/custom_queries
cat > /tmp/custom_queries/test_query.cypher << 'EOF'
# Test Custom Query - Find enabled users
# severity: INFO
MATCH (u:User {enabled: true})
RETURN u.name AS username, u.description AS description
LIMIT 10
EOF

run_test "Custom Query from File" \
    -p "$PASSWORD" -b "$BOLT" --debug -c /tmp/custom_queries/test_query.cypher

run_test "Custom Query Directory" \
    -p "$PASSWORD" -b "$BOLT" --debug -c /tmp/custom_queries/

# ===========================================================
# SUMMARY
# ===========================================================
echo "" | tee -a "$OUTPUT"
echo "========================================" | tee -a "$OUTPUT"
echo "TEST COMPLETE - $(date)" | tee -a "$OUTPUT"
echo "Output saved to: $OUTPUT" | tee -a "$OUTPUT"
echo "========================================" | tee -a "$OUTPUT"

echo ""
echo "To run tests with actual node names, edit this script and uncomment"
echo "the sections that require specific node names from your environment."
echo ""
echo "Run individual commands manually like:"
echo "  python3 -m hackles -u '$USERNAME' -p '$PASSWORD' --debug --info 'USER@DOMAIN.LOCAL' 2>&1 | tee -a '$OUTPUT'"
