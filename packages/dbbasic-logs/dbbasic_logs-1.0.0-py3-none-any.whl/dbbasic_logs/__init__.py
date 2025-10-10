"""
dbbasic-logs: Structured logging with TSV storage and compression

Philosophy: "Log everything. Query anything. Compress the rest."

Usage:
    from dbbasic_logs import log

    log.info("User logged in", user_id=42)
    log.error("Payment failed", order_id=123, error="Timeout")
    log.exception("Unexpected error", context="processing_payment")
"""

import os
import time
import json
import traceback
import subprocess
from datetime import datetime, timedelta

__version__ = "1.0.0"

LOG_DIR = os.getenv('LOG_DIR', 'data/logs')


class DBBasicLogger:
    """Structured logger with TSV storage and compression support"""

    def __init__(self, log_dir=None):
        """Initialize logger with directory structure

        Args:
            log_dir: Base directory for logs (default: data/logs)
        """
        self.log_dir = log_dir or LOG_DIR
        self._ensure_directories()

    def _ensure_directories(self):
        """Create log directory structure"""
        for log_type in ['app', 'errors', 'access']:
            os.makedirs(f'{self.log_dir}/{log_type}', exist_ok=True)

    def _write(self, log_type, level, message, context):
        """Write log entry to appropriate file

        Args:
            log_type: Log category (app, errors, access)
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Log message
            context: Additional context dictionary
        """
        today = time.strftime('%Y-%m-%d')
        log_file = f'{self.log_dir}/{log_type}/{today}.tsv'

        timestamp = int(time.time())
        context_json = json.dumps(context) if context else '{}'

        with open(log_file, 'a') as f:
            f.write(f'{timestamp}\t{level}\t{message}\t{context_json}\n')

    def info(self, message, **context):
        """Log informational message

        Args:
            message: Log message
            **context: Additional context as keyword arguments

        Example:
            log.info("User logged in", user_id=42, ip="192.168.1.1")
        """
        self._write('app', 'INFO', message, context)

    def warning(self, message, **context):
        """Log warning message

        Args:
            message: Warning message
            **context: Additional context as keyword arguments
        """
        self._write('app', 'WARNING', message, context)

    def error(self, message, **context):
        """Log error message

        Args:
            message: Error message
            **context: Additional context as keyword arguments

        Example:
            log.error("Payment failed", order_id=123, error="Timeout")
        """
        self._write('app', 'ERROR', message, context)

    def debug(self, message, **context):
        """Log debug message

        Args:
            message: Debug message
            **context: Additional context as keyword arguments
        """
        self._write('app', 'DEBUG', message, context)

    def exception(self, message, **context):
        """Log exception with automatic stack trace capture

        Should be called from within an exception handler.

        Args:
            message: Error description
            **context: Additional context as keyword arguments

        Example:
            try:
                process_payment(order)
            except Exception as e:
                log.exception("Payment failed", order_id=order.id)
                raise
        """
        context['trace'] = traceback.format_exc()
        self._write('errors', 'ERROR', message, context)

    def access(self, method, path, status, duration, **context):
        """Log HTTP access

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            status: Response status code
            duration: Request duration in seconds
            **context: Additional context (ip, user_id, etc.)

        Example:
            log.access("GET", "/api/users", 200, 0.05, ip=request.remote_addr)
        """
        msg = f'{method} {path} {status}'
        context['duration'] = duration
        self._write('access', 'INFO', msg, context)

    def search(self, pattern, log_type='app', days=7):
        """Search logs using grep/zgrep

        Searches both compressed (.tsv.gz) and uncompressed (.tsv) log files.

        Args:
            pattern: Regex pattern to search for
            log_type: Log category to search ('app', 'errors', 'access', 'all')
            days: Number of days back to search

        Returns:
            List of matching log entries as dictionaries

        Example:
            errors = log.search("ERROR", log_type='errors', days=7)
            user_logs = log.search("user_id.*42", log_type='all', days=30)
        """
        results = []
        log_types = ['app', 'errors', 'access'] if log_type == 'all' else [log_type]

        for lt in log_types:
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')

                # Try uncompressed first
                log_file = f'{self.log_dir}/{lt}/{date}.tsv'
                if os.path.exists(log_file):
                    cmd = ['grep', pattern, log_file]
                else:
                    # Try compressed
                    log_file_gz = f'{log_file}.gz'
                    if os.path.exists(log_file_gz):
                        cmd = ['zgrep', pattern, log_file_gz]
                    else:
                        continue

                try:
                    output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
                    for line in output.strip().split('\n'):
                        if line:
                            parts = line.split('\t')
                            if len(parts) >= 3:
                                results.append({
                                    'timestamp': int(parts[0]),
                                    'level': parts[1],
                                    'message': parts[2],
                                    'context': json.loads(parts[3]) if len(parts) > 3 else {},
                                    'log_type': lt
                                })
                except subprocess.CalledProcessError:
                    pass  # No matches
                except (ValueError, json.JSONDecodeError):
                    pass  # Skip malformed lines

        return results

    def tail(self, log_type='app', lines=100):
        """Get recent log entries

        Args:
            log_type: Log category to tail
            lines: Number of recent lines to retrieve

        Returns:
            List of recent log entries as dictionaries

        Example:
            recent = log.tail('app', lines=100)
            recent_errors = log.tail('errors', lines=50)
        """
        today = time.strftime('%Y-%m-%d')
        log_file = f'{self.log_dir}/{log_type}/{today}.tsv'

        if not os.path.exists(log_file):
            return []

        # Read last N lines
        with open(log_file) as f:
            all_lines = f.readlines()
            recent = all_lines[-lines:] if len(all_lines) > lines else all_lines

        results = []
        for line in recent:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                try:
                    results.append({
                        'timestamp': int(parts[0]),
                        'level': parts[1],
                        'message': parts[2],
                        'context': json.loads(parts[3]) if len(parts) > 3 else {}
                    })
                except (ValueError, json.JSONDecodeError):
                    pass  # Skip malformed lines

        return results


# Global logger instance
log = DBBasicLogger()


# Export public API
__all__ = ['log', 'DBBasicLogger', '__version__']
