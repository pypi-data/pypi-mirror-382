#!/usr/bin/env python3
"""
Enhanced Configuration Builder for MCP Proxy Adapter
Supports all configuration options and versions.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import json
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any


class Protocol(Enum):
    """Supported protocols."""
    HTTP = "http"
    HTTPS = "https"
    MTLS = "mtls"


class AuthMethod(Enum):
    """Authentication methods."""
    NONE = "none"
    TOKEN = "token"
    TOKEN_ROLES = "token_roles"
    CERTIFICATE = "certificate"
    BASIC = "basic"
    OAUTH2 = "oauth2"
    JWT = "jwt"


class ConfigBuilder:
    """Enhanced configuration builder with full feature support."""
    
    def __init__(self):
        """Initialize the configuration builder."""
        self._reset_to_defaults()
    
    def _reset_to_defaults(self):
        """Reset configuration to default values with all sections."""
        self.config = {
            "uuid": str(uuid.uuid4()),
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "protocol": "http",
                "debug": False,
                "log_level": "INFO"
            },
            "logging": {
                "level": "INFO",
                "file": None,
                "log_dir": "./logs",
                "log_file": "mcp_proxy_adapter.log",
                "error_log_file": "mcp_proxy_adapter_error.log",
                "access_log_file": "mcp_proxy_adapter_access.log",
                "max_file_size": "10MB",
                "backup_count": 5,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "date_format": "%Y-%m-%d %H:%M:%S",
                "console_output": True,
                "file_output": True,
                "json_format": False
            },
            "commands": {
                "auto_discovery": True,
                "commands_directory": "./commands",
                "catalog_directory": "./catalog",
                "plugin_servers": [],
                "auto_install_dependencies": True,
                "enabled_commands": ["health", "echo", "list", "help"],
                "disabled_commands": [],
                "custom_commands_path": "./commands"
            },
            "ssl": {
                "enabled": False,
                "mode": "https_only",
                "cert_file": None,
                "key_file": None,
                "ca_cert": None,
                "verify_client": False,
                "client_cert_required": False,
                "chk_hostname": False,
                "cipher_suites": [
                    "TLS_AES_256_GCM_SHA384",
                    "TLS_CHACHA20_POLY1305_SHA256"
                ],
                "min_tls_version": "TLSv1.2",
                "max_tls_version": None,
                "token_auth": {
                    "enabled": False,
                    "header_name": "Authorization",
                    "token_prefix": "Bearer",
                    "tokens_file": "tokens.json",
                    "token_expiry": 3600,
                    "jwt_secret": "",
                    "jwt_algorithm": "HS256"
                }
            },
            "transport": {
                "type": "http",
                "port": None,
                "ssl": {
                    "enabled": False,
                    "cert_file": None,
                    "key_file": None,
                    "ca_cert": None,
                    "verify_client": False,
                    "client_cert_required": False
                }
            },
            "proxy_registration": {
                "enabled": False,
                "proxy_url": "http://localhost:3004",
                "server_id": "mcp_proxy_adapter",
                "server_name": "MCP Proxy Adapter",
                "description": "JSON-RPC API for interacting with MCP Proxy",
                "version": "6.6.9",
                "registration_timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 5,
                "auto_register_on_startup": True,
                "auto_unregister_on_shutdown": True,
                "auth_method": "none",
                "server_url": None,
                "fallback_proxy_url": None,
                "public_host": None,
                "public_port": None,
                "protocol": None,
                "certificate": {
                    "cert_file": None,
                    "key_file": None
                },
                "token": {
                    "token": None
                },
                "api_key": {
                    "key": None
                },
                "ssl": {
                    "ca_cert": None,
                    "verify_mode": "CERT_REQUIRED"
                },
                "heartbeat": {
                    "enabled": True,
                    "interval": 30,
                    "timeout": 10,
                    "retry_attempts": 3,
                    "retry_delay": 5
                },
                "proxy_info": {
                    "name": "mcp_proxy_adapter",
                    "description": "MCP Proxy Adapter",
                    "version": "6.6.9",
                    "capabilities": ["jsonrpc", "rest", "security"],
                    "endpoints": {
                        "jsonrpc": "/api/jsonrpc",
                        "rest": "/cmd",
                        "health": "/health"
                    }
                }
            },
            "debug": {
                "enabled": False,
                "level": "WARNING",
                "log_level": "DEBUG",
                "trace_requests": False,
                "trace_responses": False
            },
            "security": {
                "framework": "mcp_security_framework",
                "enabled": False,
                "debug": False,
                "environment": "dev",
                "version": "1.0.0",
                "tokens": {
                    "admin": "admin-secret-key",
                    "user": "user-secret-key",
                    "readonly": "readonly-secret-key"
                },
                "roles": {
                    "admin": ["read", "write", "delete", "admin"],
                    "user": ["read", "write"],
                    "readonly": ["read"]
                },
                "roles_file": None,
                "auth": {
                    "enabled": False,
                    "methods": ["api_key"],
                    "api_keys": {},
                    "user_roles": {},
                    "jwt_secret": "",
                    "jwt_algorithm": "HS256",
                    "jwt_expiry_hours": 24,
                    "certificate_auth": False,
                    "certificate_roles_oid": "1.3.6.1.4.1.99999.1.1",
                    "certificate_permissions_oid": "1.3.6.1.4.1.99999.1.2",
                    "basic_auth": False,
                    "oauth2_config": None,
                    "public_paths": ["/health", "/docs", "/openapi.json"],
                    "security_headers": None
                },
                "ssl": {
                    "enabled": False,
                    "cert_file": None,
                    "key_file": None,
                    "ca_cert_file": None,
                    "client_cert_file": None,
                    "client_key_file": None,
                    "verify_mode": "CERT_NONE",
                    "min_tls_version": "TLSv1.2",
                    "max_tls_version": None,
                    "cipher_suite": None,
                    "check_hostname": True,
                    "check_expiry": True,
                    "expiry_warning_days": 30
                },
                "certificates": {
                    "enabled": False,
                    "ca_cert_path": None,
                    "ca_key_path": None,
                    "cert_storage_path": "./certs",
                    "key_storage_path": "./keys",
                    "default_validity_days": 365,
                    "key_size": 2048,
                    "hash_algorithm": "sha256",
                    "crl_enabled": False,
                    "crl_path": None,
                    "crl_url": None,
                    "crl_validity_days": 30,
                    "auto_renewal": False,
                    "renewal_threshold_days": 30
                },
                "permissions": {
                    "enabled": False,
                    "roles_file": None,
                    "default_role": "guest",
                    "admin_role": "admin",
                    "role_hierarchy": {},
                    "permission_cache_enabled": False,
                    "permission_cache_ttl": 300,
                    "wildcard_permissions": False,
                    "strict_mode": False,
                    "roles": None
                },
                "rate_limit": {
                    "enabled": False,
                    "default_requests_per_minute": 60,
                    "default_requests_per_hour": 1000,
                    "burst_limit": 2,
                    "window_size_seconds": 60,
                    "storage_backend": "memory",
                    "redis_config": None,
                    "cleanup_interval": 300,
                    "exempt_paths": ["/health", "/docs", "/openapi.json"],
                    "exempt_roles": ["admin"]
                },
                "logging": {
                    "enabled": True,
                    "level": "INFO",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "date_format": "%Y-%m-%d %H:%M:%S",
                    "file_path": None,
                    "max_file_size": 10,
                    "backup_count": 5,
                    "console_output": True,
                    "json_format": False,
                    "include_timestamp": True,
                    "include_level": True,
                    "include_module": True
                }
            },
            "roles": {
                "enabled": False,
                "config_file": None,
                "default_policy": {
                    "deny_by_default": False,
                    "require_role_match": False,
                    "case_sensitive": False,
                    "allow_wildcard": False
                },
                "auto_load": False,
                "validation_enabled": False
            },
            "protocols": {
                "enabled": True,
                "allowed_protocols": ["http", "jsonrpc"],
                "default_protocol": "http",
                "auto_discovery": True,
                "protocol_handlers": {
                    "http": {
                        "enabled": True,
                        "port": None,
                        "ssl": False
                    },
                    "https": {
                        "enabled": False,
                        "port": None,
                        "ssl": True
                    },
                    "mtls": {
                        "enabled": False,
                        "port": None,
                        "ssl": True,
                        "client_cert_required": True
                    }
                }
            }
        }
    
    def set_protocol(self, protocol: Protocol, cert_dir: str = "./certs", key_dir: str = "./keys"):
        """Set protocol configuration (HTTP, HTTPS, or mTLS)."""
        self.config["server"]["protocol"] = protocol.value
        
        # Set registration protocol to match server protocol
        self.config["proxy_registration"]["protocol"] = protocol.value
        
        # Update protocol handlers
        for handler_name in self.config["protocols"]["protocol_handlers"]:
            self.config["protocols"]["protocol_handlers"][handler_name]["enabled"] = False
        
        if protocol == Protocol.HTTP:
            # HTTP - no SSL, no client verification
            self.config["transport"]["ssl"]["verify_client"] = False
            self.config["transport"]["ssl"]["enabled"] = False
            self.config["ssl"]["enabled"] = False
            self.config["ssl"]["verify_client"] = False
            self.config["ssl"]["chk_hostname"] = False
            self.config["protocols"]["protocol_handlers"]["http"]["enabled"] = True
            self.config["protocols"]["allowed_protocols"] = ["http"]
            self.config["protocols"]["default_protocol"] = "http"
            
        elif protocol == Protocol.HTTPS:
            # HTTPS - SSL enabled, no client verification
            self.config["transport"]["ssl"]["verify_client"] = False
            self.config["transport"]["ssl"]["enabled"] = True
            self.config["ssl"]["enabled"] = True
            self.config["ssl"]["verify_client"] = False
            self.config["ssl"]["chk_hostname"] = True
            self.config["ssl"]["mode"] = "https_only"
            self.config["protocols"]["protocol_handlers"]["https"]["enabled"] = True
            self.config["protocols"]["allowed_protocols"] = ["https"]
            self.config["protocols"]["default_protocol"] = "https"
            
        elif protocol == Protocol.MTLS:
            # mTLS - SSL enabled, client verification required
            self.config["transport"]["ssl"]["verify_client"] = True
            self.config["transport"]["ssl"]["enabled"] = True
            self.config["ssl"]["enabled"] = True
            self.config["ssl"]["verify_client"] = True
            self.config["ssl"]["chk_hostname"] = True
            self.config["ssl"]["mode"] = "mtls"
            self.config["ssl"]["client_cert_required"] = True
            self.config["protocols"]["protocol_handlers"]["mtls"]["enabled"] = True
            self.config["protocols"]["allowed_protocols"] = ["mtls"]
            self.config["protocols"]["default_protocol"] = "mtls"
        
        return self
    
    def set_auth(self, auth_method: AuthMethod, api_keys: Optional[Dict[str, str]] = None, roles: Optional[Dict[str, List[str]]] = None):
        """Set authentication configuration."""
        if auth_method == AuthMethod.NONE:
            self.config["security"]["enabled"] = False
            self.config["security"]["auth"]["enabled"] = False
            self.config["security"]["auth"]["methods"] = []
            self.config["security"]["tokens"] = {}
            self.config["security"]["roles"] = {}
            self.config["security"]["roles_file"] = None
            
        elif auth_method == AuthMethod.TOKEN:
            self.config["security"]["enabled"] = True
            self.config["security"]["auth"]["enabled"] = True
            self.config["security"]["auth"]["methods"] = ["api_key"]
            self.config["security"]["tokens"] = api_keys or {
                "admin": "admin-secret-key",
                "user": "user-secret-key"
            }
            self.config["security"]["roles"] = roles or {
                "admin": ["read", "write", "delete", "admin"],
                "user": ["read", "write"]
            }
            self.config["security"]["roles_file"] = None
            
        elif auth_method == AuthMethod.TOKEN_ROLES:
            self.config["security"]["enabled"] = True
            self.config["security"]["auth"]["enabled"] = True
            self.config["security"]["auth"]["methods"] = ["api_key"]
            self.config["security"]["tokens"] = api_keys or {
                "admin": "admin-secret-key",
                "user": "user-secret-key",
                "readonly": "readonly-secret-key"
            }
            self.config["security"]["roles"] = roles or {
                "admin": ["read", "write", "delete", "admin"],
                "user": ["read", "write"],
                "readonly": ["read"]
            }
            self.config["security"]["roles_file"] = "configs/roles.json"
            self.config["roles"]["enabled"] = True
            self.config["roles"]["config_file"] = "configs/roles.json"
            
        elif auth_method == AuthMethod.CERTIFICATE:
            self.config["security"]["enabled"] = True
            self.config["security"]["auth"]["enabled"] = True
            self.config["security"]["auth"]["methods"] = ["certificate"]
            self.config["security"]["auth"]["certificate_auth"] = True
            self.config["security"]["ssl"]["enabled"] = True
            self.config["security"]["ssl"]["verify_mode"] = "CERT_REQUIRED"
            
        elif auth_method == AuthMethod.BASIC:
            self.config["security"]["enabled"] = True
            self.config["security"]["auth"]["enabled"] = True
            self.config["security"]["auth"]["methods"] = ["basic"]
            self.config["security"]["auth"]["basic_auth"] = True
            
        elif auth_method == AuthMethod.OAUTH2:
            self.config["security"]["enabled"] = True
            self.config["security"]["auth"]["enabled"] = True
            self.config["security"]["auth"]["methods"] = ["oauth2"]
            self.config["security"]["auth"]["oauth2_config"] = {}
            
        elif auth_method == AuthMethod.JWT:
            self.config["security"]["enabled"] = True
            self.config["security"]["auth"]["enabled"] = True
            self.config["security"]["auth"]["methods"] = ["jwt"]
            self.config["security"]["auth"]["jwt_secret"] = "your-jwt-secret"
            self.config["security"]["auth"]["jwt_algorithm"] = "HS256"
        
        return self
    
    def set_server(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False, log_level: str = "INFO"):
        """Set server configuration."""
        self.config["server"]["host"] = host
        self.config["server"]["port"] = port
        self.config["server"]["debug"] = debug
        self.config["server"]["log_level"] = log_level
        return self
    
    def set_logging(self, log_dir: str = "./logs", level: str = "INFO", console_output: bool = True, file_output: bool = True):
        """Set logging configuration."""
        self.config["logging"]["log_dir"] = log_dir
        self.config["logging"]["level"] = level
        self.config["logging"]["console_output"] = console_output
        self.config["logging"]["file_output"] = file_output
        return self
    
    def set_commands(self, enabled_commands: Optional[List[str]] = None, disabled_commands: Optional[List[str]] = None):
        """Set commands configuration."""
        if enabled_commands:
            self.config["commands"]["enabled_commands"] = enabled_commands
        if disabled_commands:
            self.config["commands"]["disabled_commands"] = disabled_commands
        return self
    
    def set_roles_file(self, roles_file: str):
        """Set roles file path."""
        self.config["security"]["roles_file"] = roles_file
        self.config["roles"]["config_file"] = roles_file
        self.config["roles"]["enabled"] = True
        return self
    
    def set_proxy_registration(self, enabled: bool = True, proxy_url: str = "http://localhost:3004", 
                               public_host: Optional[str] = None, public_port: Optional[int] = None,
                               server_id: str = "mcp_proxy_adapter", server_name: str = "MCP Proxy Adapter",
                               description: str = "JSON-RPC API for interacting with MCP Proxy",
                               auth_method: str = "none", cert_file: Optional[str] = None, key_file: Optional[str] = None):
        """Set proxy registration configuration."""
        self.config["proxy_registration"]["enabled"] = enabled
        self.config["proxy_registration"]["proxy_url"] = proxy_url
        self.config["proxy_registration"]["public_host"] = public_host
        self.config["proxy_registration"]["public_port"] = public_port
        self.config["proxy_registration"]["server_id"] = server_id
        self.config["proxy_registration"]["server_name"] = server_name
        self.config["proxy_registration"]["description"] = description
        self.config["proxy_registration"]["auth_method"] = auth_method
        
        if cert_file:
            self.config["proxy_registration"]["certificate"]["cert_file"] = cert_file
        if key_file:
            self.config["proxy_registration"]["certificate"]["key_file"] = key_file
        
        # Set protocol to match server protocol if not explicitly set
        if self.config["proxy_registration"]["protocol"] is None:
            self.config["proxy_registration"]["protocol"] = self.config["server"]["protocol"]
        
        return self
    
    def enable_auto_registration(self, proxy_url: str = "http://localhost:3004", 
                                server_id: str = "mcp_proxy_adapter", 
                                server_name: str = "MCP Proxy Adapter",
                                description: str = "JSON-RPC API for interacting with MCP Proxy",
                                auth_method: str = "none"):
        """
        Enable automatic proxy registration with auto-determined parameters.
        
        This method enables registration with automatic determination of:
        - public_host: from hostname (if server.host is 0.0.0.0/127.0.0.1) or server.host
        - public_port: from server.port
        - protocol: from server.protocol
        
        Args:
            proxy_url: URL of the proxy server
            server_id: Unique identifier for this server
            server_name: Human-readable name for this server
            description: Description of this server
            auth_method: Authentication method for proxy registration
        """
        self.config["proxy_registration"]["enabled"] = True
        self.config["proxy_registration"]["proxy_url"] = proxy_url
        self.config["proxy_registration"]["public_host"] = None  # Auto-determined
        self.config["proxy_registration"]["public_port"] = None  # Auto-determined
        self.config["proxy_registration"]["protocol"] = None     # Auto-determined
        self.config["proxy_registration"]["server_id"] = server_id
        self.config["proxy_registration"]["server_name"] = server_name
        self.config["proxy_registration"]["description"] = description
        self.config["proxy_registration"]["auth_method"] = auth_method
        
        return self
    
    def set_ssl_certificates(self, cert_file: str, key_file: str, ca_cert: Optional[str] = None):
        """Set SSL certificate paths."""
        self.config["ssl"]["cert_file"] = cert_file
        self.config["ssl"]["key_file"] = key_file
        if ca_cert:
            self.config["ssl"]["ca_cert"] = ca_cert
        return self
    
    def set_debug(self, enabled: bool = True, log_level: str = "DEBUG"):
        """Set debug configuration."""
        self.config["debug"]["enabled"] = enabled
        self.config["debug"]["log_level"] = log_level
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return the configuration."""
        return self.config.copy()
    
    def save(self, file_path: str) -> None:
        """Save configuration to file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)


class ConfigFactory:
    """Factory for creating common configurations."""
    
    @staticmethod
    def create_http_config(port: int = 8000) -> Dict[str, Any]:
        """Create HTTP configuration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.HTTP)
                .set_server(port=port)
                .build())
    
    @staticmethod
    def create_http_token_config(port: int = 8001) -> Dict[str, Any]:
        """Create HTTP with token authentication configuration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.HTTP)
                .set_auth(AuthMethod.TOKEN)
                .set_server(port=port)
                .build())
    
    @staticmethod
    def create_http_token_roles_config(port: int = 8002) -> Dict[str, Any]:
        """Create HTTP with token and roles configuration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.HTTP)
                .set_auth(AuthMethod.TOKEN_ROLES)
                .set_server(port=port)
                .build())
    
    @staticmethod
    def create_https_config(port: int = 8003) -> Dict[str, Any]:
        """Create HTTPS configuration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.HTTPS)
                .set_server(port=port)
                .build())
    
    @staticmethod
    def create_https_token_config(port: int = 8004) -> Dict[str, Any]:
        """Create HTTPS with token authentication configuration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.HTTPS)
                .set_auth(AuthMethod.TOKEN)
                .set_server(port=port)
                .build())
    
    @staticmethod
    def create_https_token_roles_config(port: int = 8005) -> Dict[str, Any]:
        """Create HTTPS with token and roles configuration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.HTTPS)
                .set_auth(AuthMethod.TOKEN_ROLES)
                .set_server(port=port)
                .build())
    
    @staticmethod
    def create_mtls_config(port: int = 8006) -> Dict[str, Any]:
        """Create mTLS configuration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.MTLS)
                .set_server(port=port)
                .build())
    
    @staticmethod
    def create_mtls_token_config(port: int = 8007) -> Dict[str, Any]:
        """Create mTLS with token authentication configuration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.MTLS)
                .set_auth(AuthMethod.TOKEN)
                .set_server(port=port)
                .build())

    @staticmethod
    def create_mtls_token_roles_config(port: int = 8008) -> Dict[str, Any]:
        """Create mTLS with token and roles configuration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.MTLS)
                .set_auth(AuthMethod.TOKEN_ROLES)
                .set_server(port=port)
                .build())
    
    @staticmethod
    def create_mtls_certificate_config(port: int = 8009) -> Dict[str, Any]:
        """Create mTLS with certificate authentication configuration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.MTLS)
                .set_auth(AuthMethod.CERTIFICATE)
                .set_server(port=port)
                .build())
    
    @staticmethod
    def create_http_with_proxy_config(port: int = 8010, proxy_url: str = "http://localhost:3004") -> Dict[str, Any]:
        """Create HTTP configuration with proxy registration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.HTTP)
                .set_server(port=port)
                .set_proxy_registration(proxy_url=proxy_url)
                .build())
    
    @staticmethod
    def create_https_with_proxy_config(port: int = 8011, proxy_url: str = "https://localhost:3004") -> Dict[str, Any]:
        """Create HTTPS configuration with proxy registration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.HTTPS)
                .set_server(port=port)
                .set_proxy_registration(proxy_url=proxy_url)
                .build())
    
    @staticmethod
    def create_mtls_with_proxy_config(port: int = 8012, proxy_url: str = "https://localhost:3004") -> Dict[str, Any]:
        """Create mTLS configuration with proxy registration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.MTLS)
                .set_server(port=port)
                .set_proxy_registration(proxy_url=proxy_url)
                .build())
    
    @staticmethod
    def create_http_with_auto_registration(port: int = 8013, proxy_url: str = "http://localhost:3004", 
                                         server_id: str = "mcp_proxy_adapter") -> Dict[str, Any]:
        """Create HTTP configuration with automatic proxy registration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.HTTP)
                .set_server(port=port)
                .enable_auto_registration(proxy_url=proxy_url, server_id=server_id)
                .build())
    
    @staticmethod
    def create_https_with_auto_registration(port: int = 8014, proxy_url: str = "https://localhost:3004", 
                                          server_id: str = "mcp_proxy_adapter") -> Dict[str, Any]:
        """Create HTTPS configuration with automatic proxy registration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.HTTPS)
                .set_server(port=port)
                .enable_auto_registration(proxy_url=proxy_url, server_id=server_id)
                .build())
    
    @staticmethod
    def create_mtls_with_auto_registration(port: int = 8015, proxy_url: str = "https://localhost:3004", 
                                         server_id: str = "mcp_proxy_adapter") -> Dict[str, Any]:
        """Create mTLS configuration with automatic proxy registration."""
        return (ConfigBuilder()
                .set_protocol(Protocol.MTLS)
                .set_server(port=port)
                .enable_auto_registration(proxy_url=proxy_url, server_id=server_id)
                .build())
    
    @staticmethod
    def create_full_featured_config(port: int = 8020) -> Dict[str, Any]:
        """Create full-featured configuration with all options enabled."""
        return (ConfigBuilder()
                .set_protocol(Protocol.MTLS)
                .set_auth(AuthMethod.TOKEN_ROLES)
                .set_server(port=port)
                .enable_auto_registration(
                    proxy_url="https://mcp-proxy:3004",
                    server_id="full-featured-server",
                    server_name="Full Featured Server",
                    description="Server with all features enabled"
                )
                .set_ssl_certificates(
                    cert_file="./certs/server.crt",
                    key_file="./keys/server.key",
                    ca_cert="./certs/ca.crt"
                )
                .set_debug(enabled=True)
                .build())


def create_config_from_flags(protocol: str, token: bool = False, roles: bool = False, port: int = 8000, 
                           proxy_registration: bool = False, proxy_url: str = "http://localhost:3004",
                           auto_registration: bool = False, server_id: str = "mcp_proxy_adapter") -> Dict[str, Any]:
    """
    Create configuration from command line flags.
    
    Args:
        protocol: Protocol type (http, https, mtls)
        token: Enable token authentication
        roles: Enable role-based access control
        port: Server port
        proxy_registration: Enable proxy registration with manual settings
        proxy_url: Proxy URL for registration
        auto_registration: Enable automatic proxy registration (auto-determined parameters)
        server_id: Server ID for registration
        
    Returns:
        Configuration dictionary
    """
    protocol_map = {
        "http": Protocol.HTTP,
        "https": Protocol.HTTPS,
        "mtls": Protocol.MTLS
    }
    
    if protocol not in protocol_map:
        raise ValueError(f"Unsupported protocol: {protocol}")
    
    builder = ConfigBuilder().set_protocol(protocol_map[protocol]).set_server(port=port)
    
    if roles:
        builder.set_auth(AuthMethod.TOKEN_ROLES)
    elif token:
        builder.set_auth(AuthMethod.TOKEN)
    else:
        builder.set_auth(AuthMethod.NONE)
    
    # Enable proxy registration if requested
    if auto_registration:
        # Use automatic registration with auto-determined parameters
        builder.enable_auto_registration(proxy_url=proxy_url, server_id=server_id)
    elif proxy_registration:
        # Use manual registration settings
        builder.set_proxy_registration(proxy_url=proxy_url)
    
    return builder.build()


if __name__ == "__main__":
    # Example usage
    config = create_config_from_flags("http", token=True, port=8001)
    print(json.dumps(config, indent=2))