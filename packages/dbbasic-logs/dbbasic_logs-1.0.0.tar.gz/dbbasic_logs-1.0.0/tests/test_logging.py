"""
Tests for dbbasic-logs core logging functionality
"""

import os
import time
import json
import tempfile
import shutil
from datetime import datetime, timedelta
import pytest

from dbbasic_logs import DBBasicLogger


class TestBasicLogging:
    """Test basic logging operations"""

    @pytest.fixture
    def logger(self, tmp_path):
        """Create a logger with temporary directory"""
        log_dir = str(tmp_path / "logs")
        return DBBasicLogger(log_dir=log_dir)

    def test_directory_creation(self, logger):
        """Test that log directories are created"""
        assert os.path.exists(f'{logger.log_dir}/app')
        assert os.path.exists(f'{logger.log_dir}/errors')
        assert os.path.exists(f'{logger.log_dir}/access')

    def test_info_logging(self, logger):
        """Test info level logging"""
        logger.info("Test message", user_id=42)

        today = time.strftime('%Y-%m-%d')
        log_file = f'{logger.log_dir}/app/{today}.tsv'

        assert os.path.exists(log_file)

        with open(log_file) as f:
            line = f.read().strip()

        parts = line.split('\t')
        assert len(parts) == 4
        assert int(parts[0]) > 0  # timestamp
        assert parts[1] == 'INFO'
        assert parts[2] == 'Test message'

        context = json.loads(parts[3])
        assert context['user_id'] == 42

    def test_warning_logging(self, logger):
        """Test warning level logging"""
        logger.warning("Rate limit approaching", count=95)

        today = time.strftime('%Y-%m-%d')
        log_file = f'{logger.log_dir}/app/{today}.tsv'

        with open(log_file) as f:
            line = f.read().strip()

        parts = line.split('\t')
        assert parts[1] == 'WARNING'
        assert parts[2] == 'Rate limit approaching'

    def test_error_logging(self, logger):
        """Test error level logging"""
        logger.error("Database connection failed", error="Timeout")

        today = time.strftime('%Y-%m-%d')
        log_file = f'{logger.log_dir}/app/{today}.tsv'

        with open(log_file) as f:
            line = f.read().strip()

        parts = line.split('\t')
        assert parts[1] == 'ERROR'
        assert parts[2] == 'Database connection failed'

        context = json.loads(parts[3])
        assert context['error'] == 'Timeout'

    def test_debug_logging(self, logger):
        """Test debug level logging"""
        logger.debug("Cache miss", key="user:42")

        today = time.strftime('%Y-%m-%d')
        log_file = f'{logger.log_dir}/app/{today}.tsv'

        with open(log_file) as f:
            line = f.read().strip()

        parts = line.split('\t')
        assert parts[1] == 'DEBUG'

    def test_multiple_context_fields(self, logger):
        """Test logging with multiple context fields"""
        logger.info(
            "User action",
            user_id=42,
            action="update_profile",
            ip="192.168.1.1",
            duration=0.123
        )

        today = time.strftime('%Y-%m-%d')
        log_file = f'{logger.log_dir}/app/{today}.tsv'

        with open(log_file) as f:
            line = f.read().strip()

        parts = line.split('\t')
        context = json.loads(parts[3])

        assert context['user_id'] == 42
        assert context['action'] == 'update_profile'
        assert context['ip'] == '192.168.1.1'
        assert context['duration'] == 0.123

    def test_empty_context(self, logger):
        """Test logging without context"""
        logger.info("Simple message")

        today = time.strftime('%Y-%m-%d')
        log_file = f'{logger.log_dir}/app/{today}.tsv'

        with open(log_file) as f:
            line = f.read().strip()

        parts = line.split('\t')
        assert parts[3] == '{}'


class TestExceptionLogging:
    """Test exception and stack trace logging"""

    @pytest.fixture
    def logger(self, tmp_path):
        """Create a logger with temporary directory"""
        log_dir = str(tmp_path / "logs")
        return DBBasicLogger(log_dir=log_dir)

    def test_exception_logging(self, logger):
        """Test exception logging with stack trace"""
        try:
            result = 1 / 0
        except ZeroDivisionError:
            logger.exception("Division error", operation="calculate")

        today = time.strftime('%Y-%m-%d')
        log_file = f'{logger.log_dir}/errors/{today}.tsv'

        assert os.path.exists(log_file)

        with open(log_file) as f:
            line = f.read().strip()

        parts = line.split('\t')
        assert parts[1] == 'ERROR'
        assert parts[2] == 'Division error'

        context = json.loads(parts[3])
        assert context['operation'] == 'calculate'
        assert 'trace' in context
        assert 'ZeroDivisionError' in context['trace']
        assert 'Traceback' in context['trace']

    def test_exception_with_nested_calls(self, logger):
        """Test exception logging from nested function calls"""
        def inner_function():
            raise ValueError("Invalid value")

        def outer_function():
            inner_function()

        try:
            outer_function()
        except ValueError:
            logger.exception("Nested exception", context="testing")

        today = time.strftime('%Y-%m-%d')
        log_file = f'{logger.log_dir}/errors/{today}.tsv'

        with open(log_file) as f:
            line = f.read().strip()

        parts = line.split('\t')
        context = json.loads(parts[3])

        # Check that stack trace includes nested calls
        assert 'inner_function' in context['trace']
        assert 'outer_function' in context['trace']
        assert 'ValueError' in context['trace']


class TestAccessLogging:
    """Test HTTP access logging"""

    @pytest.fixture
    def logger(self, tmp_path):
        """Create a logger with temporary directory"""
        log_dir = str(tmp_path / "logs")
        return DBBasicLogger(log_dir=log_dir)

    def test_access_logging(self, logger):
        """Test access log entry"""
        logger.access(
            method="GET",
            path="/api/users",
            status=200,
            duration=0.05,
            ip="192.168.1.1"
        )

        today = time.strftime('%Y-%m-%d')
        log_file = f'{logger.log_dir}/access/{today}.tsv'

        assert os.path.exists(log_file)

        with open(log_file) as f:
            line = f.read().strip()

        parts = line.split('\t')
        assert parts[1] == 'INFO'
        assert parts[2] == 'GET /api/users 200'

        context = json.loads(parts[3])
        assert context['duration'] == 0.05
        assert context['ip'] == '192.168.1.1'

    def test_access_logging_post_request(self, logger):
        """Test POST request access logging"""
        logger.access(
            method="POST",
            path="/login",
            status=401,
            duration=0.02,
            ip="192.168.1.2",
            user_agent="Mozilla/5.0"
        )

        today = time.strftime('%Y-%m-%d')
        log_file = f'{logger.log_dir}/access/{today}.tsv'

        with open(log_file) as f:
            line = f.read().strip()

        parts = line.split('\t')
        assert parts[2] == 'POST /login 401'

        context = json.loads(parts[3])
        assert context['user_agent'] == 'Mozilla/5.0'


class TestLogSearching:
    """Test log search functionality"""

    @pytest.fixture
    def logger(self, tmp_path):
        """Create a logger with temporary directory"""
        log_dir = str(tmp_path / "logs")
        return DBBasicLogger(log_dir=log_dir)

    def test_search_single_log(self, logger):
        """Test searching within a single log file"""
        logger.info("User logged in", user_id=42)
        logger.info("User updated profile", user_id=42)
        logger.info("User logged out", user_id=42)

        results = logger.search("logged in", log_type='app', days=1)

        assert len(results) == 1
        assert results[0]['message'] == 'User logged in'
        assert results[0]['level'] == 'INFO'
        assert results[0]['context']['user_id'] == 42

    def test_search_multiple_matches(self, logger):
        """Test searching with multiple matches"""
        logger.info("User logged in", user_id=42)
        logger.info("User logged in", user_id=43)
        logger.info("User logged in", user_id=44)

        results = logger.search("User logged in", log_type='app', days=1)

        assert len(results) == 3

    def test_search_with_regex(self, logger):
        """Test searching with regex pattern"""
        logger.info("Request completed", duration=0.1)
        logger.info("Request completed", duration=1.5)
        logger.info("Request completed", duration=0.05)

        # Search for duration greater than 1 second
        results = logger.search(r'duration.*[1-9]\.', log_type='app', days=1)

        assert len(results) == 1
        assert results[0]['context']['duration'] == 1.5

    def test_search_errors(self, logger):
        """Test searching error logs"""
        logger.error("Payment failed", order_id=123)
        logger.error("Database timeout", query="SELECT")

        results = logger.search("ERROR", log_type='app', days=1)

        assert len(results) == 2
        assert all(r['level'] == 'ERROR' for r in results)

    def test_search_all_log_types(self, logger):
        """Test searching across all log types"""
        logger.info("App log", user_id=42)
        logger.access("GET", "/api", 200, 0.1)

        try:
            raise Exception("Test error")
        except:
            logger.exception("Error log")

        results = logger.search(".*", log_type='all', days=1)

        # Should find entries from app, access, and errors
        log_types = set(r['log_type'] for r in results)
        assert 'app' in log_types
        assert 'access' in log_types
        assert 'errors' in log_types

    def test_search_no_matches(self, logger):
        """Test search with no matching results"""
        logger.info("Test message")

        results = logger.search("nonexistent", log_type='app', days=1)

        assert len(results) == 0

    def test_search_missing_log_file(self, logger):
        """Test search when log file doesn't exist"""
        # Don't create any logs
        results = logger.search("anything", log_type='app', days=1)

        assert len(results) == 0


class TestLogTailing:
    """Test log tailing functionality"""

    @pytest.fixture
    def logger(self, tmp_path):
        """Create a logger with temporary directory"""
        log_dir = str(tmp_path / "logs")
        return DBBasicLogger(log_dir=log_dir)

    def test_tail_recent_logs(self, logger):
        """Test getting recent log entries"""
        for i in range(10):
            logger.info(f"Message {i}", count=i)

        results = logger.tail('app', lines=5)

        assert len(results) == 5
        assert results[0]['message'] == 'Message 5'
        assert results[-1]['message'] == 'Message 9'

    def test_tail_all_logs(self, logger):
        """Test tailing when fewer logs than requested"""
        logger.info("Message 1")
        logger.info("Message 2")

        results = logger.tail('app', lines=100)

        assert len(results) == 2

    def test_tail_errors(self, logger):
        """Test tailing error logs"""
        try:
            raise ValueError("Test error 1")
        except:
            logger.exception("Error 1")

        try:
            raise ValueError("Test error 2")
        except:
            logger.exception("Error 2")

        results = logger.tail('errors', lines=10)

        assert len(results) == 2
        assert all(r['level'] == 'ERROR' for r in results)

    def test_tail_empty_log(self, logger):
        """Test tailing when log file doesn't exist"""
        results = logger.tail('app', lines=100)

        assert len(results) == 0

    def test_tail_access_logs(self, logger):
        """Test tailing access logs"""
        logger.access("GET", "/api/users", 200, 0.1)
        logger.access("POST", "/api/users", 201, 0.2)

        results = logger.tail('access', lines=10)

        assert len(results) == 2


class TestLogCompression:
    """Test log compression scenarios"""

    @pytest.fixture
    def logger(self, tmp_path):
        """Create a logger with temporary directory"""
        log_dir = str(tmp_path / "logs")
        return DBBasicLogger(log_dir=log_dir)

    def test_search_compressed_logs(self, logger):
        """Test searching compressed log files"""
        # Create a log file and compress it
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        log_file = f'{logger.log_dir}/app/{yesterday}.tsv'

        # Write some logs
        timestamp = int(time.time())
        with open(log_file, 'w') as f:
            f.write(f'{timestamp}\tINFO\tOld message\t{{"user_id":42}}\n')

        # Compress it
        import subprocess
        subprocess.run(['gzip', log_file], check=True)

        # Search should find it in compressed file
        results = logger.search("Old message", log_type='app', days=2)

        assert len(results) == 1
        assert results[0]['message'] == 'Old message'


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def logger(self, tmp_path):
        """Create a logger with temporary directory"""
        log_dir = str(tmp_path / "logs")
        return DBBasicLogger(log_dir=log_dir)

    def test_special_characters_in_message(self, logger):
        """Test logging messages with special characters"""
        logger.info("Message with special chars", data="test")

        today = time.strftime('%Y-%m-%d')
        log_file = f'{logger.log_dir}/app/{today}.tsv'

        with open(log_file) as f:
            line = f.read().strip()

        # Should still parse correctly
        parts = line.split('\t')
        assert len(parts) == 4
        assert parts[2] == "Message with special chars"

    def test_unicode_in_context(self, logger):
        """Test logging with unicode characters"""
        logger.info("Unicode test", name="José", emoji="🎉")

        today = time.strftime('%Y-%m-%d')
        log_file = f'{logger.log_dir}/app/{today}.tsv'

        with open(log_file, encoding='utf-8') as f:
            line = f.read().strip()

        parts = line.split('\t')
        context = json.loads(parts[3])

        assert context['name'] == 'José'
        assert context['emoji'] == '🎉'

    def test_large_context(self, logger):
        """Test logging with large context data"""
        large_data = {"data": "x" * 10000}
        logger.info("Large context", **large_data)

        today = time.strftime('%Y-%m-%d')
        log_file = f'{logger.log_dir}/app/{today}.tsv'

        assert os.path.exists(log_file)

        with open(log_file) as f:
            line = f.read().strip()

        parts = line.split('\t')
        context = json.loads(parts[3])

        assert len(context['data']) == 10000

    def test_nested_context_objects(self, logger):
        """Test logging with nested context objects"""
        logger.info(
            "Nested context",
            user={"id": 42, "name": "John"},
            metadata={"tags": ["a", "b", "c"]}
        )

        today = time.strftime('%Y-%m-%d')
        log_file = f'{logger.log_dir}/app/{today}.tsv'

        with open(log_file) as f:
            line = f.read().strip()

        parts = line.split('\t')
        context = json.loads(parts[3])

        assert context['user']['id'] == 42
        assert context['user']['name'] == 'John'
        assert context['metadata']['tags'] == ['a', 'b', 'c']


class TestGlobalLoggerInstance:
    """Test the global logger instance"""

    def test_global_log_import(self):
        """Test that global log instance can be imported"""
        from dbbasic_logs import log

        assert log is not None
        assert isinstance(log, DBBasicLogger)

    def test_global_log_usage(self, tmp_path):
        """Test using the global log instance"""
        from dbbasic_logs import log

        # Override log directory for testing
        log.log_dir = str(tmp_path / "logs")
        log._ensure_directories()

        log.info("Test with global logger", test=True)

        today = time.strftime('%Y-%m-%d')
        log_file = f'{log.log_dir}/app/{today}.tsv'

        assert os.path.exists(log_file)
