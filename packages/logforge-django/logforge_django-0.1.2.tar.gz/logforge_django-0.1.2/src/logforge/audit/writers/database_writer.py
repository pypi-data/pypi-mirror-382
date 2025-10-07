"""
Database Writer for LogForge Django

Synchronous audit log writer that writes directly to the database.
"""

import logging
from typing import Dict, Any
from django.db import transaction

from ..models import ActivityLog
from ..contracts import LogWriter

logger = logging.getLogger(__name__)


class DatabaseWriter(LogWriter):
    """Database writer for synchronous audit log writing."""
    
    def write(self, record: Dict[str, Any]) -> None:
        """Write an audit log record to the database."""
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
            
            with transaction.atomic():
                ActivityLog.objects.create(**record)
        except Exception as e:
            logger.error(
                'LogForge database writer failed',
                extra={
                    'exception': type(e).__name__,
                    'error_message': str(e),
                    'event_type': record.get('event_type'),
                    'user_id': record.get('user_id'),
                    'resource_type': record.get('resource_type'),
                    'resource_id': record.get('resource_id'),
                }
            )
            raise
