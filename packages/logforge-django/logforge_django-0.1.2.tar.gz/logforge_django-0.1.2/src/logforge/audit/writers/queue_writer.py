"""
Queue Writer for LogForge Django

Asynchronous audit log writer using Celery with database fallback.
"""

import logging
import importlib
from typing import Dict, Any

from .database_writer import DatabaseWriter
from ..config import get_logforge_config
from ..contracts import LogWriter

logger = logging.getLogger(__name__)


class QueueWriter(LogWriter):
    """Queue-backed writer using Celery with database fallback."""

    def write(self, record: Dict[str, Any]) -> None:
        try:
            from ..support import AuditBatch
            if AuditBatch.is_open():
                record['batch_uuid'] = AuditBatch.get_uuid()
                batch_context = AuditBatch.get_context()
                if batch_context:
                    existing_context = record.get('context', {})
                    if isinstance(existing_context, dict):
                        record['context'] = {**batch_context, **existing_context}
                    else:
                        record['context'] = batch_context
        except Exception:
            pass

        config = get_logforge_config()
        task = None
        try:
            tasks_module = importlib.import_module('logforge.audit.tasks')
            task = getattr(tasks_module, 'write_audit_log', None)
        except Exception as e:
            task = None

        if task is not None:
            try:
                queue_cfg = config.get('queue', {}) or {}
                queue_name = queue_cfg.get('queue')
                delay_seconds = queue_cfg.get('delay', 0)

                apply_kwargs: Dict[str, Any] = {}
                if queue_name:
                    apply_kwargs['queue'] = queue_name
                if delay_seconds and isinstance(delay_seconds, (int, float)) and delay_seconds > 0:
                    apply_kwargs['countdown'] = int(delay_seconds)

                task.apply_async(args=[record], **apply_kwargs)
                return
            except Exception as e:
                logger.warning(
                    'LogForge queue writer failed to enqueue, falling back to DB',
                    extra={
                        'exception': type(e).__name__,
                        'message': str(e),
                        'event_type': record.get('event_type'),
                        'resource_type': record.get('resource_type'),
                        'resource_id': record.get('resource_id'),
                    }
                )

        DatabaseWriter().write(record)


