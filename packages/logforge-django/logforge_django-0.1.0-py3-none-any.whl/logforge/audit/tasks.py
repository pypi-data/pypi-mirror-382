"""
Celery tasks for LogForge Django

This module contains Celery tasks for asynchronous audit log processing.
"""

import logging
from typing import Dict, Any
from celery import shared_task
from celery.exceptions import Retry

from .models import ActivityLog

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, time_limit=30)
def write_audit_log(self, record: Dict[str, Any]) -> None:
    """
    Celery task to write audit log record to database.
    
    This task handles the actual database write operation in a separate
    process, equivalent to Laravel's WriteAuditLogJob::handle().
    
    Args:
        record: Dictionary containing audit log data
        
    Raises:
        Retry: If the task should be retried
        Exception: If the task fails permanently
    """
    try:
        ActivityLog.objects.create(**record)
        
    except Exception as e:
        logger.error(
            'LogForge queue job failed to write audit log',
            extra={
                'exception': type(e).__name__,
                'message': str(e),
                'event_type': record.get('event_type'),
                'user_id': record.get('user_id'),
                'resource_type': record.get('resource_type'),
                'resource_id': record.get('resource_id'),
                'attempt': self.request.retries + 1,
            }
        )
        
        # Retry the task if we haven't exceeded max retries
        if self.request.retries < self.max_retries:
            logger.info(
                'Retrying audit log write',
                extra={
                    'event_type': record.get('event_type'),
                    'attempt': self.request.retries + 1,
                    'max_retries': self.max_retries,
                }
            )
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        # If we've exceeded max retries, log the permanent failure
        logger.error(
            'LogForge queue job permanently failed',
            extra={
                'exception': type(e).__name__,
                'message': str(e),
                'event_type': record.get('event_type'),
                'user_id': record.get('user_id'),
                'resource_type': record.get('resource_type'),
                'resource_id': record.get('resource_id'),
                'attempts': self.request.retries + 1,
            }
        )
        
        # Re-raise the exception to mark the task as failed
        raise


@shared_task(bind=True, max_retries=3, time_limit=60)
def batch_write_audit_logs(self, records: list[Dict[str, Any]]) -> None:
    """
    Celery task to write multiple audit log records in batch.
    
    This task handles bulk database writes for better performance
    when processing multiple audit logs.
    
    Args:
        records: List of dictionaries containing audit log data
    """
    try:
        # Use bulk_create for better performance
        audit_logs = [ActivityLog(**record) for record in records]
        ActivityLog.objects.bulk_create(audit_logs)
        
        logger.info(
            'Successfully wrote batch audit logs',
            extra={'count': len(records)}
        )
        
    except Exception as e:
        logger.error(
            'LogForge batch queue job failed',
            extra={
                'exception': type(e).__name__,
                'message': str(e),
                'count': len(records),
                'attempt': self.request.retries + 1,
            }
        )
        
        # Retry the task if we haven't exceeded max retries
        if self.request.retries < self.max_retries:
            logger.info(
                'Retrying batch audit log write',
                extra={
                    'count': len(records),
                    'attempt': self.request.retries + 1,
                    'max_retries': self.max_retries,
                }
            )
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        # Re-raise the exception to mark the task as failed
        raise
