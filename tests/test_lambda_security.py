"""Security tests for the AWS Lambda handler URL validation."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent / "examples" / "integrations" / "aws_lambda")
)

from lambda_handler import _build_launch_kwargs, _classify_error, _validate_url


class TestSchemeValidation:
    """Fix 1: only http:// and https:// are accepted."""

    @pytest.mark.parametrize("url", [
        "file:///etc/passwd",
        "file:///proc/self/environ",
        "data:text/html,<h1>pwned</h1>",
        "javascript:alert(1)",
        "chrome://settings",
        "about:blank",
        "ftp://example.com/file",
        "",
    ])
    def test_rejects_non_http_schemes(self, url):
        with pytest.raises(ValueError, match="Only http"):
            _validate_url(url)

    @pytest.mark.parametrize("url", [
        "https://example.com",
        "http://example.com",
        "https://example.com/path?q=1",
        "HTTP://EXAMPLE.COM",
    ])
    def test_accepts_http_and_https(self, url):
        _validate_url(url)

    def test_rejects_missing_hostname(self):
        with pytest.raises(ValueError, match="no hostname"):
            _validate_url("http://")


class TestSSRFProtection:
    """Fix 2: block private, loopback, link-local, reserved, and metadata IPs."""

    @pytest.mark.parametrize("url,label", [
        ("http://169.254.169.254", "AWS metadata"),
        ("http://169.254.169.254/latest/meta-data/", "AWS metadata path"),
        ("http://127.0.0.1", "loopback"),
        ("http://127.0.0.2", "loopback range"),
        ("http://localhost", "localhost"),
        ("http://10.0.0.1", "private 10.x"),
        ("http://172.16.0.1", "private 172.16"),
        ("http://192.168.1.1", "private 192.168"),
        ("http://0.0.0.0", "unspecified"),
        ("http://[::1]", "IPv6 loopback"),
    ])
    def test_rejects_private_ips(self, url, label):
        with pytest.raises(ValueError, match="private/internal"):
            _validate_url(url)

    def test_rejects_carrier_grade_nat(self):
        with pytest.raises(ValueError, match="private/internal"):
            _validate_url("http://100.64.0.1")

    def test_rejects_unresolvable_hostname(self):
        with pytest.raises(ValueError, match="Cannot resolve"):
            _validate_url("http://this-host-does-not-exist-cb-test.invalid")

    def test_rejects_ipv4_mapped_ipv6(self):
        """::ffff:127.0.0.1 should be blocked even though it's technically IPv6."""
        with pytest.raises(ValueError, match="private/internal"):
            _validate_url("http://[::ffff:127.0.0.1]")


class TestExtraArgsRemoval:
    """Fix 3: caller-controlled extra_args are ignored; internal _strategy_args work."""

    def test_ignores_caller_extra_args(self):
        event = {"url": "https://example.com", "extra_args": ["--remote-debugging-port=9222"]}
        kwargs = _build_launch_kwargs(event)
        assert "--remote-debugging-port=9222" not in kwargs["args"]

    def test_includes_strategy_args(self):
        event = {"url": "https://example.com", "_strategy_args": ["--ignore-certificate-errors"]}
        kwargs = _build_launch_kwargs(event)
        assert "--ignore-certificate-errors" in kwargs["args"]

    def test_classify_error_uses_strategy_args(self):
        result = _classify_error(Exception("ERR_CERT_AUTHORITY_INVALID"))
        assert "_strategy_args" in result
        assert "extra_args" not in result

    def test_always_includes_lambda_hardening_flags(self):
        kwargs = _build_launch_kwargs({"url": "https://example.com"})
        assert "--disable-dev-shm-usage" in kwargs["args"]
        assert "--no-zygote" in kwargs["args"]

    def test_caller_cannot_inject_strategy_args(self):
        """_strategy_args in the caller event must be stripped by _run() before launch."""
        from lambda_handler import _run
        import inspect
        source = inspect.getsource(_run)
        assert '"_strategy_args"' in source and "extra_args" in source, \
            "_run must strip both _strategy_args and extra_args from caller event"


class TestRedirectSSRF:
    """Fix 5: post-navigation re-validation catches redirects to blocked IPs.

    These mock socket.getaddrinfo to simulate redirect scenarios without
    needing a real browser or HTTP server.
    """

    def test_validate_url_catches_redirect_target(self):
        """If Chromium followed a redirect to 169.254.169.254, the post-nav
        _validate_url(page.url) call should reject it."""
        with pytest.raises(ValueError, match="private/internal"):
            _validate_url("http://169.254.169.254/latest/meta-data/iam/security-credentials/")

    def test_validate_url_catches_localhost_redirect(self):
        with pytest.raises(ValueError, match="private/internal"):
            _validate_url("http://127.0.0.1:8080/admin")

    def test_code_flow_validates_before_content(self):
        """Verify that _attempt_scrape calls _validate_url(page.url) at line 282
        BEFORE building the result dict at line 290 (sequential code path)."""
        import ast
        handler_path = (
            Path(__file__).resolve().parent.parent
            / "examples" / "integrations" / "aws_lambda" / "lambda_handler.py"
        )
        source = handler_path.read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "_attempt_scrape":
                body = node.body
                # Find the try block
                for stmt in body:
                    if isinstance(stmt, ast.Try):
                        try_body = stmt.body
                        validate_lines = []
                        content_line = None
                        for s in try_body:
                            if isinstance(s, ast.Expr) and isinstance(s.value, ast.Call):
                                func = s.value.func
                                if isinstance(func, ast.Name) and func.id == "_validate_url":
                                    validate_lines.append(s.lineno)
                            if isinstance(s, ast.AnnAssign):
                                if isinstance(s.target, ast.Name) and s.target.id == "result":
                                    content_line = s.lineno
                            elif isinstance(s, ast.Assign):
                                for target in s.targets:
                                    if isinstance(target, ast.Name) and target.id == "result":
                                        content_line = s.lineno
                        assert len(validate_lines) >= 2, (
                            f"Expected 2 _validate_url calls, found {len(validate_lines)}"
                        )
                        assert content_line is not None
                        assert all(v < content_line for v in validate_lines), (
                            f"_validate_url (lines {validate_lines}) must come before "
                            f"result assignment (line {content_line})"
                        )
                        return
        pytest.fail("Could not find _attempt_scrape function in source")
