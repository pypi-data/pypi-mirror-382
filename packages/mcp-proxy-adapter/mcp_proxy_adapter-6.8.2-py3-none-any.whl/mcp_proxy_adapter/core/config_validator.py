"""
Configuration validation utilities.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

This module provides strict configuration validation with support for two modes:
- startup (strict): fail-fast with SystemExit on invalid config
- reload  (soft): log errors and keep previous config
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from mcp_proxy_adapter.core.logging import logger


@dataclass
class ConfigValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]

    @staticmethod
    def ok() -> "ConfigValidationResult":
        return ConfigValidationResult(True, [], [])


class ConfigValidator:
    """
    Unified configuration validator supporting both result-based and boolean APIs.
    """

    def __init__(self, _config: Optional[Dict[str, Any]] = None) -> None:
        # Optional stored config for validate_all() compatibility
        self._config: Optional[Dict[str, Any]] = _config
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self, config: Optional[Dict[str, Any]] = None) -> ConfigValidationResult:
        """
        Validate configuration and return detailed result.

        Args:
            config: Configuration dict. If None, uses self._config.
        """
        cfg = config if config is not None else (self._config or {})
        self.errors = []
        self.warnings = []

        # Top-level basics
        self._validate_uuid(cfg)
        self._validate_server(cfg)
        self._validate_protocols(cfg)

        # SSL/mTLS
        self._validate_ssl(cfg)

        # Security framework sections
        self._validate_security_auth(cfg)
        self._validate_permissions(cfg)
        self._validate_rate_limit(cfg)

        return ConfigValidationResult(
            is_valid=len(self.errors) == 0,
            errors=list(self.errors),
            warnings=list(self.warnings),
        )

    # Boolean API for backward compatibility (used in main.py)
    def validate_all(self) -> bool:
        result = self.validate(self._config)
        return result.is_valid

    def get_errors(self) -> List[str]:
        return list(self.errors)

    def get_warnings(self) -> List[str]:
        return list(self.warnings)

    # ------------- Section validators -------------

    def _validate_uuid(self, config: Dict[str, Any]) -> None:
        uuid_value = config.get("uuid")
        if not uuid_value or not isinstance(uuid_value, str) or len(uuid_value) < 8:
            self.errors.append(
                "UUID is required in configuration. Add 'uuid' field with a valid UUID4 value."
            )

    def _validate_server(self, config: Dict[str, Any]) -> None:
        server = config.get("server", {})
        port = server.get("port")
        if port is None or not isinstance(port, int) or not (1 <= port <= 65535):
            self.errors.append("Server.port must be an integer between 1 and 65535")

        host = server.get("host")
        if not host or not isinstance(host, str):
            self.errors.append("Server.host must be a non-empty string")

    def _validate_protocols(self, config: Dict[str, Any]) -> None:
        protocols = config.get("protocols", {})
        if not isinstance(protocols, dict):
            self.warnings.append("'protocols' must be a dictionary; ignoring")
            return

        enabled = protocols.get("enabled", True)
        if not enabled:
            return  # Disabled => allow all (manager bypassed)

        allowed = protocols.get("allowed_protocols", [])
        default_protocol = protocols.get("default_protocol")
        if not isinstance(allowed, list) or not all(isinstance(x, str) for x in allowed):
            self.errors.append("protocols.allowed_protocols must be a list of strings")
        if default_protocol and default_protocol not in allowed:
            self.errors.append(
                "protocols.default_protocol must be present in allowed_protocols"
            )

    def _validate_ssl(self, config: Dict[str, Any]) -> None:
        # Prefer security.ssl if enabled; otherwise fallback to root ssl
        sec = config.get("security", {}) if isinstance(config.get("security"), dict) else {}
        security_ssl = sec.get("ssl", {}) if isinstance(sec.get("ssl"), dict) else {}
        root_ssl = config.get("ssl", {}) if isinstance(config.get("ssl"), dict) else {}

        effective_ssl = security_ssl if security_ssl.get("enabled", False) else root_ssl
        if not isinstance(effective_ssl, dict):
            return

        if effective_ssl.get("enabled", False):
            cert_file = effective_ssl.get("cert_file")
            key_file = effective_ssl.get("key_file")
            if not cert_file or not key_file:
                self.errors.append(
                    "SSL enabled but 'cert_file' or 'key_file' is missing"
                )
            else:
                if not Path(cert_file).exists():
                    self.errors.append(f"SSL certificate file not found: {cert_file}")
                if not Path(key_file).exists():
                    self.errors.append(f"SSL private key file not found: {key_file}")

            # mTLS
            verify_client = effective_ssl.get("verify_client", False)
            ca_candidates = [
                effective_ssl.get("ca_cert_file"),  # security.ssl
                effective_ssl.get("ca_cert"),  # legacy root.ssl
            ]
            ca_cert = next((c for c in ca_candidates if isinstance(c, str) and c), None)

            if verify_client:
                if not ca_cert:
                    self.errors.append(
                        "mTLS requires a CA certificate (security.ssl.ca_cert_file or ssl.ca_cert)"
                    )
                elif not Path(ca_cert).exists():
                    self.errors.append(f"CA certificate file not found: {ca_cert}")

            # TLS versions
            min_tls = str(effective_ssl.get("min_tls_version", "TLSv1.2"))
            valid_min = {"TLSv1.2", "1.2", "TLSv1.3", "1.3"}
            if min_tls not in valid_min:
                self.warnings.append(
                    f"Unknown min_tls_version '{min_tls}', expected one of {sorted(valid_min)}"
                )

        # Conflict check
        if security_ssl.get("enabled") and root_ssl.get("enabled"):
            self.warnings.append(
                "SSL configured in both security.ssl and root ssl; security.ssl is preferred"
            )

    def _validate_security_auth(self, config: Dict[str, Any]) -> None:
        sec = config.get("security", {}) if isinstance(config.get("security"), dict) else {}
        auth = sec.get("auth", {}) if isinstance(sec.get("auth"), dict) else {}

        if not sec.get("enabled", False) or not auth.get("enabled", False):
            return

        methods = auth.get("methods", [])
        if not isinstance(methods, list):
            self.errors.append("security.auth.methods must be a list")
            return

        if "jwt" in methods and not auth.get("jwt_secret"):
            self.warnings.append("JWT method enabled but jwt_secret is empty")

        if "certificate" in methods:
            # Ensure SSL is enabled for certificate auth
            ssl_enabled = (
                (sec.get("ssl", {}) or {}).get("enabled", False)
                or (config.get("ssl", {}) or {}).get("enabled", False)
            )
            if not ssl_enabled:
                self.errors.append(
                    "Certificate auth enabled but SSL is disabled (enable security.ssl or root ssl)"
                )

    def _validate_permissions(self, config: Dict[str, Any]) -> None:
        sec = config.get("security", {}) if isinstance(config.get("security"), dict) else {}
        perm = sec.get("permissions", {}) if isinstance(sec.get("permissions"), dict) else {}
        roles = perm.get("roles_file")
        if perm.get("enabled", False) and roles:
            if not Path(roles).exists():
                self.errors.append(f"Permissions enabled but roles file not found: {roles}")

    def _validate_rate_limit(self, config: Dict[str, Any]) -> None:
        sec = config.get("security", {}) if isinstance(config.get("security"), dict) else {}
        rl = sec.get("rate_limit", {}) if isinstance(sec.get("rate_limit"), dict) else {}
        if rl.get("enabled", False):
            rpm = rl.get("default_requests_per_minute") or rl.get("requests_per_minute")
            if rpm is None or not isinstance(rpm, int) or rpm <= 0:
                self.errors.append(
                    "Rate limit enabled but requests_per_minute is not a positive integer"
                )
