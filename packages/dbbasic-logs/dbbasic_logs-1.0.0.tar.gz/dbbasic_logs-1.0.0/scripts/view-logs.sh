#!/bin/bash
#
# Utility script for viewing and searching logs
#
# Usage:
#   ./view-logs.sh tail [app|errors|access] [lines]
#   ./view-logs.sh search "pattern" [log_type] [days]
#   ./view-logs.sh today [app|errors|access]
#   ./view-logs.sh errors [days]
#

set -e

LOG_DIR="${LOG_DIR:-data/logs}"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

usage() {
    echo "DBBasic Logs Viewer"
    echo ""
    echo "Usage:"
    echo "  $0 tail [log_type] [lines]     - View recent logs"
    echo "  $0 search <pattern> [type] [days] - Search logs"
    echo "  $0 today [log_type]            - View today's logs"
    echo "  $0 errors [days]               - View recent errors"
    echo "  $0 stats                       - Show log statistics"
    echo ""
    echo "Log types: app, errors, access, all"
    echo ""
    echo "Examples:"
    echo "  $0 tail app 100                - Last 100 app logs"
    echo "  $0 search ERROR app 7          - Search for errors in last 7 days"
    echo "  $0 today errors                - View today's error logs"
    echo "  $0 errors 1                    - View last day of errors"
    exit 1
}

# Tail logs
tail_logs() {
    local log_type=${1:-app}
    local lines=${2:-100}
    local today=$(date +%Y-%m-%d)
    local log_file="${LOG_DIR}/${log_type}/${today}.tsv"

    if [ ! -f "$log_file" ]; then
        echo -e "${YELLOW}No logs found for today: ${log_type}${NC}"
        exit 1
    fi

    echo -e "${BLUE}=== Last ${lines} lines from ${log_type} ===${NC}"
    tail -n "$lines" "$log_file" | while IFS=$'\t' read -r timestamp level message context; do
        local date_str=$(date -d "@${timestamp}" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -r "${timestamp}" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)

        case "$level" in
            ERROR)
                echo -e "${RED}[${date_str}] ${level} ${message}${NC}"
                ;;
            WARNING)
                echo -e "${YELLOW}[${date_str}] ${level} ${message}${NC}"
                ;;
            *)
                echo -e "${GREEN}[${date_str}]${NC} ${level} ${message}"
                ;;
        esac

        if [ "$context" != "{}" ]; then
            echo "  Context: $context"
        fi
    done
}

# Search logs
search_logs() {
    local pattern=$1
    local log_type=${2:-app}
    local days=${3:-7}

    echo -e "${BLUE}=== Searching for '${pattern}' in ${log_type} (last ${days} days) ===${NC}"

    for ((i=0; i<days; i++)); do
        local date=$(date -d "${i} days ago" +%Y-%m-%d 2>/dev/null || date -v-${i}d +%Y-%m-%d 2>/dev/null)

        if [ "$log_type" = "all" ]; then
            types="app errors access"
        else
            types="$log_type"
        fi

        for type in $types; do
            local log_file="${LOG_DIR}/${type}/${date}.tsv"
            local log_file_gz="${log_file}.gz"

            if [ -f "$log_file" ]; then
                grep -i "$pattern" "$log_file" 2>/dev/null | while IFS=$'\t' read -r timestamp level message context; do
                    local date_str=$(date -d "@${timestamp}" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -r "${timestamp}" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
                    echo -e "${GREEN}[${type}]${NC} [${date_str}] ${level} ${message}"
                    if [ "$context" != "{}" ]; then
                        echo "  $context"
                    fi
                done
            elif [ -f "$log_file_gz" ]; then
                zgrep -i "$pattern" "$log_file_gz" 2>/dev/null | while IFS=$'\t' read -r timestamp level message context; do
                    local date_str=$(date -d "@${timestamp}" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -r "${timestamp}" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
                    echo -e "${GREEN}[${type}]${NC} [${date_str}] ${level} ${message}"
                    if [ "$context" != "{}" ]; then
                        echo "  $context"
                    fi
                done
            fi
        done
    done
}

# View today's logs
today_logs() {
    local log_type=${1:-app}
    local today=$(date +%Y-%m-%d)
    local log_file="${LOG_DIR}/${log_type}/${today}.tsv"

    echo -e "${BLUE}=== Today's ${log_type} logs ===${NC}"

    if [ ! -f "$log_file" ]; then
        echo -e "${YELLOW}No logs found for today${NC}"
        exit 1
    fi

    cat "$log_file" | while IFS=$'\t' read -r timestamp level message context; do
        local date_str=$(date -d "@${timestamp}" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -r "${timestamp}" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)

        case "$level" in
            ERROR)
                echo -e "${RED}[${date_str}] ${level} ${message}${NC}"
                ;;
            WARNING)
                echo -e "${YELLOW}[${date_str}] ${level} ${message}${NC}"
                ;;
            *)
                echo -e "[${date_str}] ${level} ${message}"
                ;;
        esac

        if [ "$context" != "{}" ]; then
            echo "  Context: $context"
        fi
    done
}

# View recent errors
view_errors() {
    local days=${1:-1}
    search_logs "ERROR" "all" "$days"
}

# Show statistics
show_stats() {
    echo -e "${BLUE}=== Log Statistics ===${NC}"
    echo ""

    for log_type in app errors access; do
        local dir="${LOG_DIR}/${log_type}"
        if [ -d "$dir" ]; then
            local file_count=$(find "$dir" -type f | wc -l)
            local size=$(du -sh "$dir" | cut -f1)
            echo -e "${GREEN}${log_type}:${NC}"
            echo "  Files: $file_count"
            echo "  Size: $size"

            # Today's stats
            local today=$(date +%Y-%m-%d)
            local log_file="${dir}/${today}.tsv"
            if [ -f "$log_file" ]; then
                local lines=$(wc -l < "$log_file")
                echo "  Today's entries: $lines"
            fi
            echo ""
        fi
    done
}

# Main command dispatcher
case "${1:-}" in
    tail)
        tail_logs "$2" "$3"
        ;;
    search)
        if [ -z "$2" ]; then
            usage
        fi
        search_logs "$2" "$3" "$4"
        ;;
    today)
        today_logs "$2"
        ;;
    errors)
        view_errors "$2"
        ;;
    stats)
        show_stats
        ;;
    *)
        usage
        ;;
esac
