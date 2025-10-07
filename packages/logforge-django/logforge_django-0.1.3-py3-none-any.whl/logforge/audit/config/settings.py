"""
LogForge Django Configuration

Configuration management for the LogForge Django package.
"""

import os
from typing import Dict, Any, List, Optional


def get_logforge_config() -> Dict[str, Any]:
    """
    Get LogForge configuration from Django settings.
    """
    from django.conf import settings
    
    default_config = {
        'enabled': True,
        'events': ['create', 'update', 'delete', 'restore', 'force_delete'],
        'snapshot_on_update': False,
        'ignore_columns': ['updated_at'],
        'include': [],
        'exclude': [],
        'redact': ['password', 'password_confirmation', 'secret', 'token'],
        'per_model': {},
        'context': {
            'capture_ip': True,
            'capture_user_agent': True,
        },
        'payload_max_bytes': 65536,
        'suppress_exceptions': True,
        'actor': {
            'resolver': None,
            'default': None,
        },
        'retention_days': None,
        'archive': {
            'enabled': False,
            'path': None,
            'format': 'json',
        },
        'performance': {
            'enabled': False,
            'slow_threshold_ms': 100,
            'sample_rate': 1.0,
        },
        'writer': 'db',
        'queue': {
            'connection': 'default',
            'queue': 'audit-logs',
            'delay': 0,
        },
        # Dashboard access control
        'dashboard': {
            # Dotted path to a callable like 'myproject.auth.can_view_logforge(user)'.
            # Defaults to allowing staff users only when None.
            'allow': None,
            # When True, unauthenticated users are redirected to the Django admin login
            # instead of the project LOGIN_URL.
            'use_admin_login': False,
        },
    }
    
    user_config = getattr(settings, 'LOGFORGE', {})
    
    config = _deep_merge(default_config, user_config)
    
    config = _apply_env_overrides(config)
    
    if config['archive']['path'] is None:
        config['archive']['path'] = os.path.join(settings.MEDIA_ROOT, 'logforge')
    
    return config


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to configuration."""
    env_mappings = {
        'LOGFORGE_ENABLED': ('enabled', bool),
        'LOGFORGE_SNAPSHOT_ON_UPDATE': ('snapshot_on_update', bool),
        'LOGFORGE_PAYLOAD_MAX_BYTES': ('payload_max_bytes', int),
        'LOGFORGE_SUPPRESS_EXCEPTIONS': ('suppress_exceptions', bool),
        'LOGFORGE_RETENTION_DAYS': ('retention_days', int),
        'LOGFORGE_ARCHIVE_ENABLED': ('archive', 'enabled', bool),
        'LOGFORGE_ARCHIVE_PATH': ('archive', 'path', str),
        'LOGFORGE_WRITER': ('writer', str),
        'LOGFORGE_QUEUE_CONNECTION': ('queue', 'connection', str),
        'LOGFORGE_QUEUE_NAME': ('queue', 'queue', str),
        'LOGFORGE_QUEUE_DELAY': ('queue', 'delay', int),
        'LOGFORGE_PERF_ENABLED': ('performance', 'enabled', bool),
        'LOGFORGE_PERF_SLOW_MS': ('performance', 'slow_threshold_ms', int),
        'LOGFORGE_PERF_SAMPLE': ('performance', 'sample_rate', float),
        'LOGFORGE_CAPTURE_IP': ('context', 'capture_ip', bool),
        'LOGFORGE_CAPTURE_USER_AGENT': ('context', 'capture_user_agent', bool),
        'LOGFORGE_ACTOR_DEFAULT': ('actor', 'default', str),
        # Optional: dashboard access function dotted path
        'LOGFORGE_DASHBOARD_ALLOW': ('dashboard', 'allow', str),
    }
    
    for env_var, path in env_mappings.items():
        value = os.environ.get(env_var)
        if value is not None:
            _set_nested_value(config, path, value)
    
    return config


def _set_nested_value(config: Dict[str, Any], path: tuple, value: str) -> None:
    """Set a nested value in the configuration dictionary."""
    if len(path) == 2:
        key, type_func = path
        config[key] = type_func(value)
    elif len(path) == 3:
        key1, key2, type_func = path
        if key1 not in config:
            config[key1] = {}
        config[key1][key2] = type_func(value)


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate LogForge configuration.
    
    Raises ValueError if configuration is invalid.
    """
    # Validate events
    if not isinstance(config.get('events'), list):
        raise ValueError("LOGFORGE: events must be a list")
    
    valid_events = ['create', 'update', 'delete', 'restore', 'force_delete']
    invalid_events = [e for e in config['events'] if e not in valid_events]
    if invalid_events:
        raise ValueError(f"LOGFORGE: Invalid events: {invalid_events}. Valid events: {valid_events}")
    
    # Validate payload_max_bytes
    if not isinstance(config.get('payload_max_bytes'), int) or config['payload_max_bytes'] < 100:
        raise ValueError("LOGFORGE: payload_max_bytes must be an integer >= 100")
    
    # Validate retention_days
    if config.get('retention_days') is not None:
        if not isinstance(config['retention_days'], int) or config['retention_days'] < 1:
            raise ValueError("LOGFORGE: retention_days must be an integer >= 1")
    
    # Validate performance settings
    perf = config.get('performance', {})
    if not isinstance(perf.get('enabled'), bool):
        raise ValueError("LOGFORGE: performance.enabled must be a boolean")
    
    if not isinstance(perf.get('slow_threshold_ms'), int) or perf['slow_threshold_ms'] < 1:
        raise ValueError("LOGFORGE: performance.slow_threshold_ms must be an integer >= 1")
    
    if not isinstance(perf.get('sample_rate'), (int, float)) or not (0 <= perf['sample_rate'] <= 1):
        raise ValueError("LOGFORGE: performance.sample_rate must be a number between 0 and 1")
    
    # Validate writer
    valid_writers = ['db', 'queue']
    if config.get('writer') not in valid_writers:
        raise ValueError(f"LOGFORGE: writer must be one of: {valid_writers}")
    
    # Validate archive settings
    archive = config.get('archive', {})
    if not isinstance(archive.get('enabled'), bool):
        raise ValueError("LOGFORGE: archive.enabled must be a boolean")
    
    # Validate actor resolver
    actor = config.get('actor', {})
    if actor.get('resolver') is not None:
        resolver = actor['resolver']
        if not callable(resolver) and not isinstance(resolver, str):
            raise ValueError("LOGFORGE: actor.resolver must be a callable or string")
    
    # Validate queue settings
    if config.get('writer') == 'queue':
        queue = config.get('queue', {})
        if not isinstance(queue.get('delay'), int) or queue['delay'] < 0:
            raise ValueError("LOGFORGE: queue.delay must be an integer >= 0")
