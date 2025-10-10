#!/bin/bash
#
# Log rotation script for dbbasic-logs
#
# Install to cron for automatic rotation:
#   sudo cp rotate-logs.sh /etc/cron.daily/dbbasic-logs-rotate
#   sudo chmod +x /etc/cron.daily/dbbasic-logs-rotate
#
# Or run manually:
#   ./rotate-logs.sh
#

set -e

# Configuration
LOG_DIR="${LOG_DIR:-data/logs}"
APP_RETENTION_DAYS="${APP_RETENTION_DAYS:-30}"
ACCESS_RETENTION_DAYS="${ACCESS_RETENTION_DAYS:-30}"
ERROR_RETENTION_DAYS="${ERROR_RETENTION_DAYS:-90}"

# Get yesterday's date
YESTERDAY=$(date -d yesterday +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

echo "DBBasic Logs Rotation - $(date)"
echo "Log directory: $LOG_DIR"
echo "Yesterday: $YESTERDAY"
echo ""

# Function to compress logs
compress_logs() {
    local log_type=$1
    local log_file="${LOG_DIR}/${log_type}/${YESTERDAY}.tsv"

    if [ -f "$log_file" ]; then
        echo "Compressing ${log_type}/${YESTERDAY}.tsv..."
        gzip "$log_file"
        echo "  ✓ Compressed to ${log_file}.gz"
    else
        echo "  ℹ No log file found: ${log_type}/${YESTERDAY}.tsv"
    fi
}

# Function to delete old logs
delete_old_logs() {
    local log_type=$1
    local retention_days=$2
    local count=0

    echo "Deleting ${log_type} logs older than ${retention_days} days..."

    if [ -d "${LOG_DIR}/${log_type}" ]; then
        # Find and delete old compressed logs
        count=$(find "${LOG_DIR}/${log_type}" -name "*.tsv.gz" -mtime +${retention_days} -type f | wc -l)
        find "${LOG_DIR}/${log_type}" -name "*.tsv.gz" -mtime +${retention_days} -type f -delete

        if [ $count -gt 0 ]; then
            echo "  ✓ Deleted $count old ${log_type} log files"
        else
            echo "  ℹ No old ${log_type} logs to delete"
        fi
    fi
}

# Compress yesterday's logs
echo "=== Compressing Yesterday's Logs ==="
compress_logs "app"
compress_logs "errors"
compress_logs "access"
echo ""

# Delete old logs based on retention policy
echo "=== Cleaning Old Logs ==="
delete_old_logs "app" "$APP_RETENTION_DAYS"
delete_old_logs "access" "$ACCESS_RETENTION_DAYS"
delete_old_logs "errors" "$ERROR_RETENTION_DAYS"
echo ""

# Show disk usage
if [ -d "$LOG_DIR" ]; then
    echo "=== Log Directory Size ==="
    du -sh "$LOG_DIR"
    echo ""
    echo "Breakdown by type:"
    for log_type in app errors access; do
        if [ -d "${LOG_DIR}/${log_type}" ]; then
            size=$(du -sh "${LOG_DIR}/${log_type}" | cut -f1)
            files=$(find "${LOG_DIR}/${log_type}" -type f | wc -l)
            echo "  ${log_type}: ${size} (${files} files)"
        fi
    done
fi

echo ""
echo "Rotation complete: $(date)"
