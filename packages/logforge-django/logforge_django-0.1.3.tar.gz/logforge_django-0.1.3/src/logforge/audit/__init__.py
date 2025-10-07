
# Default app config for Django
default_app_config = 'logforge.audit.apps.AuditConfig'

# Avoid importing Django models/mixins at module import time to prevent
# AppRegistryNotReady during Django setup. Expose symbols via lazy import.

import importlib  # noqa: E402

__all__ = [
    'LogsActivity',
    'ActivityLog',
    'AuditBatch',
    'DatabaseWriter',
    'QueueWriter',
    'LogWriter',
    'LogWriterContract',
]


def __getattr__(name):  # pragma: no cover - simple lazy import shim
    if name == 'LogsActivity':
        return importlib.import_module('logforge.audit.mixins.logs_activity').LogsActivity
    if name == 'ActivityLog':
        return importlib.import_module('logforge.audit.models.activity_log').ActivityLog
    if name == 'AuditBatch':
        return importlib.import_module('logforge.audit.support.audit_batch').AuditBatch
    if name in ('DatabaseWriter', 'QueueWriter', 'LogWriter'):
        module = importlib.import_module('logforge.audit.writers')
        return getattr(module, name)
    if name == 'LogWriterContract':
        return importlib.import_module('logforge.audit.contracts.log_writer').LogWriter
    raise AttributeError(f"module 'logforge.audit' has no attribute {name!r}")
