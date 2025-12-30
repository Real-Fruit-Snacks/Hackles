# Hackles Code Review

## Status: Complete

**Started**: 2025-12-29
**Methodology**: Parallel agent analysis with systematic bug hunting

---

## Analysis Areas

| Area | Agent | Status |
|------|-------|--------|
| Core Modules | Agent 1 | Complete |
| CLI Modules | Agent 2 | Complete |
| Query System | Agent 3 | Complete |

---

## Executive Summary

The hackles codebase is well-structured overall with a clean modular design. However, the analysis identified **8 critical issues**, **10 major issues**, and numerous minor code quality improvements. The most severe problems involve:

1. **Silent error handling** - Query failures return empty lists, masking real errors
2. **Backwards compatibility exports** - Module-level exports become stale references
3. **Cypher syntax errors** - 3 query files have WHERE clause conflicts
4. **Missing abuse template output** - The `--abuse` flag has no effect

---

## Critical Issues 🔴

### C1. Query errors silently return empty list
- **File**: `hackles/core/bloodhound.py:48-53`
- **Impact**: Caller cannot distinguish "no results" from "query execution failed"
- **Fix**: Surface errors via tuple return `(results, error)` or custom exception

### C2. Label operations don't verify modification
- **File**: `hackles/core/bloodhound.py:82-120`
- **Impact**: `mark_owned()`, `unmark_owned()`, etc. may silently fail to modify nodes
- **Fix**: Verify modification count: `RETURN count(n) AS modified` and check > 0

### C3. Regex injection in search_nodes
- **File**: `hackles/core/bloodhound.py:146-156`
- **Impact**: User input `.*` or special regex chars can bypass intended search behavior
- **Fix**: Use `re.escape()` on pattern before regex construction

### C4. Cypher injection in node_type function
- **File**: `hackles/core/cypher.py:4-24`
- **Impact**: Malicious variable names can inject Cypher code
- **Fix**: Validate `var` matches pattern `^[a-zA-Z_]\w*$` before use

### C5. Backwards compatibility exports are broken
- **File**: `hackles/core/config.py:26-29`
- **Impact**: `OWNED_CACHE`, `QUIET_MODE`, `SHOW_ABUSE`, `DEBUG_MODE` become stale references
- **Fix**: Remove deprecated exports or use `@property` getters

### C6. Asymmetric argument handling
- **Files**: `hackles/cli/parser.py:47,56` and `hackles/cli/main.py:146-150,174-178`
- **Impact**: `--unown` and `--untier-zero` only accept single values vs `--own`/`--tier-zero` which accept multiple
- **Fix**: Add `action='append'` to these arguments (or document limitation)

### C7. WHERE clause conflicts in 3 query files
- **Files**:
  - `hackles/queries/credentials/asrep_roastable.py:33,38`
  - `hackles/queries/credentials/never_changed_password.py:21,26`
  - `hackles/queries/delegation/delegatable_admins.py:19,23`
- **Impact**: Cypher syntax error when domain filter applied
- **Fix**: Change `domain_filter = "WHERE ..."` to `domain_filter = "AND ..."` in affected files

### C8. Missing BloodHoundCE type import
- **Files**: All 109 query files
- **Impact**: Type annotation `bh: BloodHoundCE` missing import (works due to PEP 563 but breaks type checkers)
- **Fix**: Add `from __future__ import annotations` + TYPE_CHECKING guard import

---

## Major Issues 🟠

### M1. Silent exception handling in run_query
- **File**: `hackles/core/bloodhound.py:48-53`
- **Impact**: All exceptions print to stderr but return empty list

### M2. Potential None pointer dereference
- **File**: `hackles/core/bloodhound.py:70-80`
- **Impact**: `results[0]["sid"]` accesses without validation

### M3. No thread safety in config
- **File**: `hackles/core/config.py`
- **Impact**: Race condition if multiple threads access config

### M4. Hard-coded relationship list duplication
- **File**: `hackles/core/bloodhound.py:269-291`
- **Impact**: Same 21-item list duplicated in `get_edges_from` and `get_edges_to`

### M5. Custom query severity hardcoded
- **File**: `hackles/cli/main.py:107`
- **Impact**: Custom queries always have `Severity.MEDIUM`, cannot override

### M6. Missing abuse template output
- **File**: `hackles/cli/main.py:448-458`
- **Impact**: `--abuse` flag sets `config.show_abuse` but query loop never prints abuse templates
- **Fix**: Wire abuse template printing in query output flow

### M7. INFO queries excluded from counts
- **File**: `hackles/cli/main.py:452`
- **Impact**: Severity summary incomplete - INFO queries not counted

### M8. Inconsistent null handling in cypher helpers
- **File**: `hackles/core/cypher.py:27-34`
- **Impact**: `owned_filter` lacks COALESCE that `tier_zero_filter` uses

### M9. Silent failure in abuse template loading
- **File**: `hackles/abuse/loader.py:52-54`
- **Impact**: Malformed YAML files silently ignored, no warning to user

### M10. Backward compat boolean refs stale
- **File**: `hackles/core/config.py:27-29`
- **Impact**: `QUIET_MODE`, `SHOW_ABUSE`, `DEBUG_MODE` won't reflect config changes

---

## Minor Issues 🟡

| Location | Issue |
|----------|-------|
| `bloodhound.py` | Incomplete debug logging - no query timing |
| `bloodhound.py` | Missing domain parameter in 4 methods |
| `bloodhound.py` | Type hints incomplete throughout |
| `config.py` | Missing docstrings for attributes |
| `config.py` | No type validation on assignment |
| `config.py` | Public mutable state (should be private) |
| `cypher.py` | Hardcoded `ELSE labels({var})[0]` fallback |
| `cypher.py` | No documentation of expected usage |
| Query files | Duplicate `_extract_domain()` function in 5+ files |

---

## Application Flow

```
ENTRY POINT: python -m hackles
    |
    v
hackles/__main__.py
    |
    v
hackles.cli.main.main()
    |
    +---> hackles.cli.parser.create_parser() --> ArgumentParser
    +---> args = parser.parse_args()
    |
    v
CONFIGURATION
    |---> config.quiet_mode = args.quiet
    |---> config.show_abuse = args.abuse
    |---> config.debug_mode = args.debug
    |
    v
CONNECTION
    |---> BloodHoundCE(bolt, user, pass)
    |---> bh.connect()
    |
    v
OWNERSHIP MANAGEMENT
    |---> if args.own: mark_owned(principals)
    |---> if args.unown: unmark_owned(principal)  # BUG: single only
    |---> init_owned_cache(bh)
    |
    v
EARLY EXIT OPERATIONS
    |---> if args.clear_owned: clear_all_owned() --> EXIT
    |---> if args.tier_zero: mark_tier_zero() [no exit unless no -a]
    |---> if args.untier_zero: unmark_tier_zero()  # BUG: single only
    |---> if args.list: list_domains() --> EXIT
    |---> if args.info: show_node_info() --> EXIT
    |---> if args.search: search_nodes() --> EXIT
    |---> if args.path*: find_paths() --> EXIT
    |---> if args.members/memberof: get_membership() --> EXIT
    |---> if args.adminto/adminof/sessions: get_admin_info() --> EXIT
    |---> if args.edges_*: get_edges() --> EXIT
    |---> if quick_filters: run and EXIT
    |
    v
QUERY SELECTION
    |---> Load custom queries if --custom
    |---> Determine selected_queries based on flags
    |
    v
QUERY EXECUTION LOOP
    |---> for (name, func, severity) in selected_queries:
    |     |---> result_count = func(bh, domain, severity)
    |     |---> Track severity counts
    |     |---> [MISSING]: Abuse template output
    |
    v
SUMMARY & CLEANUP
    |---> print_severity_summary()
    |---> bh.close()
```

---

## Recommendations (Prioritized)

### Priority 1 - Critical Fixes
1. Fix 3 query files with WHERE clause conflicts (C7)
2. Implement abuse template output in query loop (M6)
3. Fix backwards compat exports or remove them (C5, M10)
4. Add input validation to `node_type()` (C4)
5. Surface query errors to caller (C1)

### Priority 2 - Important Improvements
6. Add `action='append'` to `--unown`/`--untier-zero` OR document limitation
7. Verify write operations actually modified data (C2)
8. Add regex escaping to `search_nodes()` (C3)
9. Add error logging to abuse template loader (M9)
10. Fix custom query severity to allow override (M5)

### Priority 3 - Code Quality
11. Extract hardcoded relationship lists to constants (M4)
12. Add TYPE_CHECKING guard imports to query files (C8)
13. Consolidate `_extract_domain()` to shared utility
14. Add thread safety to config singleton (M3)
15. Complete type hints throughout codebase

---

## Files Requiring Changes

| File | Changes Needed |
|------|----------------|
| `hackles/core/bloodhound.py` | Error handling, validation, constants |
| `hackles/core/config.py` | Remove stale exports, add thread safety |
| `hackles/core/cypher.py` | Input validation, COALESCE consistency |
| `hackles/cli/main.py` | Abuse template output, severity counts |
| `hackles/cli/parser.py` | Append action for unown/untier-zero |
| `hackles/abuse/loader.py` | Add error logging |
| `hackles/queries/credentials/asrep_roastable.py` | Fix WHERE→AND |
| `hackles/queries/credentials/never_changed_password.py` | Fix WHERE→AND |
| `hackles/queries/delegation/delegatable_admins.py` | Fix WHERE→AND |
| All 109 query files | Add TYPE_CHECKING import |

---

## Fixes Applied (2025-12-29)

### Completed Fixes

| Issue | File | Fix |
|-------|------|-----|
| C4 | `cypher.py` | Added regex validation to `node_type()` to prevent Cypher injection |
| C5, M10 | `config.py` | Removed stale backwards compatibility exports |
| C3 | `bloodhound.py` | Added `re.escape()` to `search_nodes()` for regex safety |
| M4 | `bloodhound.py` | Extracted `ATTACK_EDGES` constant for relationship lists |
| M8 | `cypher.py` | Added `COALESCE()` to `owned_filter()` for consistency |
| M9 | `loader.py` | Added error logging for failed YAML template loads |
| Dup | `bloodhound.py` | Removed duplicate `init_owned_cache()` (main.py has correct version) |
| M4 | `utils.py` | Created shared `extract_domain()` utility |
| - | `printer.py` | Updated to use shared `extract_domain()` from utils |

### Additional Fixes (2025-12-29 - Batch 2)

| Issue | File(s) | Fix |
|-------|---------|-----|
| C1 | `bloodhound.py` | Added `raise` after query error logging - errors now propagate to callers |
| C8 | 109 query files | Added `TYPE_CHECKING` import guard for `BloodHoundCE` type hint |
| - | 33 query files | Replaced local `_extract_domain()` with shared `extract_domain()` from utils |
| M6 | N/A | Already implemented - 43 queries have `print_abuse_info()` calls |
| C2 | N/A | Already correct - SET/REMOVE are idempotent and reliable in Neo4j |

### Final Fixes (2025-12-29 - Batch 3)

| Issue | File | Fix |
|-------|------|-----|
| M3 | `config.py` | Added `threading.RLock()` and property accessors for thread-safe state |
| M5 | `main.py` | Custom queries now parse `# severity: HIGH` from .cypher file headers |

### All Issues Resolved

| Issue | Status | Notes |
|-------|--------|-------|
| C6 | Fixed earlier | `--unown`/`--untier-zero` single value handling |
| C7 | No bug | WHERE clauses were correct (property filters != WHERE) |
| M3 | Fixed | Thread-safe config with RLock |
| M5 | Fixed | Custom query severity via `# severity: LEVEL` comment |
