#!/bin/bash
# Pre-push check script for Hackles
# Run this before pushing to catch CI issues locally
# Logs are saved to logs/check_YYYYMMDD_HHMMSS.log

set -e  # Exit on first error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Create logs directory if it doesn't exist
mkdir -p logs

# Generate timestamped log filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/check_${TIMESTAMP}.log"

# Colors (for terminal only)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log to both terminal and file
log() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
    # Strip color codes for log file
    echo "$message" | sed 's/\x1b\[[0-9;]*m//g' >> "$LOG_FILE"
}

# Function to log command output
log_output() {
    tee -a "$LOG_FILE"
}

# Initialize log file with header
{
    echo "========================================"
    echo "Hackles Pre-Push Check Log"
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Git Branch: $(git branch --show-current)"
    echo "Git Commit: $(git rev-parse --short HEAD)"
    echo "========================================"
    echo ""
} > "$LOG_FILE"

log "$BLUE" "========================================"
log "$BLUE" "  Hackles Pre-Push Checks"
log "$BLUE" "========================================"
log "$NC" "Log file: $LOG_FILE"
echo "" | log_output

# Track if we're in fix mode
FIX_MODE=false
if [[ "$1" == "--fix" || "$1" == "-f" ]]; then
    FIX_MODE=true
    log "$YELLOW" "Running in FIX mode - will auto-fix issues"
    echo "" | log_output
fi

FAILED=0

# 1. Black formatting
log "$BLUE" "[1/5] Code Formatting (black)"
echo "[1/5] Code Formatting (black)" >> "$LOG_FILE"
if $FIX_MODE; then
    black hackles/ tests/ 2>&1 | log_output
    log "$GREEN" "    ✓ Formatted"
else
    if black --check --diff hackles/ tests/ 2>&1 | head -20 | log_output; then
        log "$GREEN" "    ✓ Passed"
    else
        log "$RED" "    ✗ Failed - run with --fix to auto-format"
        ((FAILED++))
    fi
fi
echo "" | log_output

# 2. Import sorting
log "$BLUE" "[2/5] Import Sorting (isort)"
echo "[2/5] Import Sorting (isort)" >> "$LOG_FILE"
if $FIX_MODE; then
    isort hackles/ tests/ 2>&1 | log_output
    log "$GREEN" "    ✓ Sorted"
else
    if isort --check-only --diff hackles/ tests/ 2>&1 | head -20 | log_output; then
        log "$GREEN" "    ✓ Passed"
    else
        log "$RED" "    ✗ Failed - run with --fix to auto-sort"
        ((FAILED++))
    fi
fi
echo "" | log_output

# 3. Flake8 linting (critical errors only - matches CI)
log "$BLUE" "[3/5] Linting (flake8 - critical errors)"
echo "[3/5] Linting (flake8 - critical errors)" >> "$LOG_FILE"
if flake8 hackles/ tests/ --count --select=E9,F63,F7,F82,F824 --show-source --statistics 2>&1 | log_output; then
    log "$GREEN" "    ✓ Passed"
else
    log "$RED" "    ✗ Failed - fix errors above"
    ((FAILED++))
fi
echo "" | log_output

# 4. Ruff linting (optional but helpful)
log "$BLUE" "[4/5] Linting (ruff)"
echo "[4/5] Linting (ruff)" >> "$LOG_FILE"
if command -v ruff &> /dev/null; then
    if $FIX_MODE; then
        ruff check --fix hackles/ tests/ 2>&1 | tail -10 | log_output
        log "$GREEN" "    ✓ Fixed"
    else
        if ruff check hackles/ tests/ 2>&1 | tail -10 | log_output; then
            log "$GREEN" "    ✓ Passed"
        else
            log "$YELLOW" "    ! Warnings (non-blocking)"
        fi
    fi
else
    log "$YELLOW" "    ! Skipped (ruff not installed)"
    echo "    Skipped (ruff not installed)" >> "$LOG_FILE"
fi
echo "" | log_output

# 5. Tests
log "$BLUE" "[5/5] Tests (pytest)"
echo "[5/5] Tests (pytest)" >> "$LOG_FILE"
if pytest tests/ -q --tb=short 2>&1 | log_output; then
    log "$GREEN" "    ✓ Passed"
else
    log "$RED" "    ✗ Failed"
    ((FAILED++))
fi
echo "" | log_output

# Summary
{
    echo "========================================"
    echo "Summary"
    echo "========================================"
} >> "$LOG_FILE"

log "$BLUE" "========================================"
if [ $FAILED -eq 0 ]; then
    log "$GREEN" "  All checks passed! Safe to push."
    echo "Result: ALL PASSED" >> "$LOG_FILE"
    log "$BLUE" "========================================"
    log "$NC" "Log saved: $LOG_FILE"
    exit 0
else
    log "$RED" "  $FAILED check(s) failed"
    log "$YELLOW" "  Run: make fix"
    echo "Result: $FAILED FAILED" >> "$LOG_FILE"
    log "$BLUE" "========================================"
    log "$NC" "Log saved: $LOG_FILE"
    exit 1
fi
