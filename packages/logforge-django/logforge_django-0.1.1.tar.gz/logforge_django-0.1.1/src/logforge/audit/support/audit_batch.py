"""
AuditBatch Support for LogForge Django

This module provides batch operation support for audit logging,
equivalent to Laravel's AuditBatch class. It allows correlating
multiple audit log entries with a single batch UUID.
"""

import uuid
import threading
from typing import Dict, Any, Optional, Callable, ContextManager
from contextlib import contextmanager

from ..models import ActivityLog

# Thread-local storage for batch state
_local = threading.local()


class AuditBatch:
    """
    Django implementation of Laravel's AuditBatch class.
    
    Provides batch operation support with UUID correlation for audit logs.
    All operations within a batch context will be tagged with the same batch_uuid.
    """
    
    @staticmethod
    def run(
        callback: Callable[[str], None], 
        context: Optional[Dict[str, Any]] = None, 
        summary: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Run a callback within a batch context.
        
        Args:
            callback: Function to execute with batch UUID as parameter
            context: Additional context to merge into all audit logs
            summary: Optional summary record to create after batch completion
        """
        batch_uuid = str(uuid.uuid4())
        context = context or {}
        failed = False
        
        # Set batch state
        _local.current_uuid = batch_uuid
        _local.context = context
        
        try:
            callback(batch_uuid)
        except Exception as e:
            failed = True
            raise e
        finally:
            # Create summary record if provided
            if summary is not None:
                AuditBatch._create_summary_record(batch_uuid, context, summary, failed)
            
            # Clear batch state
            _local.current_uuid = None
            _local.context = {}
    
    @staticmethod
    @contextmanager
    def run_context(
        context: Optional[Dict[str, Any]] = None, 
        summary: Optional[Dict[str, Any]] = None
    ) -> ContextManager[str]:
        """
        Context manager version of run() for use with 'with' statement.
        
        Args:
            context: Additional context to merge into all audit logs
            summary: Optional summary record to create after batch completion
            
        Yields:
            str: The batch UUID
            
        Example:
            with AuditBatch.run_context({'source': 'import'}) as batch_uuid:
                # Operations here will be correlated
                pass
        """
        batch_uuid = str(uuid.uuid4())
        context = context or {}
        failed = False
        
        # Set batch state
        _local.current_uuid = batch_uuid
        _local.context = context
        
        try:
            yield batch_uuid
        except Exception as e:
            failed = True
            raise e
        finally:
            # Create summary record if provided
            if summary is not None:
                AuditBatch._create_summary_record(batch_uuid, context, summary, failed)
            
            # Clear batch state
            _local.current_uuid = None
            _local.context = {}
    
    @staticmethod
    def is_open() -> bool:
        """
        Check if a batch is currently open.
        
        Returns:
            bool: True if a batch is open, False otherwise
        """
        return getattr(_local, 'current_uuid', None) is not None
    
    @staticmethod
    def get_uuid() -> Optional[str]:
        """
        Get the current batch UUID.
        
        Returns:
            Optional[str]: Current batch UUID or None if no batch is open
        """
        return getattr(_local, 'current_uuid', None)
    
    @staticmethod
    def get_context() -> Dict[str, Any]:
        """
        Get the current batch context.
        
        Returns:
            Dict[str, Any]: Current batch context or empty dict if no batch is open
        """
        return getattr(_local, 'context', {})
    
    @staticmethod
    def _create_summary_record(
        batch_uuid: str, 
        context: Dict[str, Any], 
        summary: Dict[str, Any], 
        failed: bool
    ) -> None:
        """
        Create a summary record for the batch.
        
        Args:
            batch_uuid: The batch UUID
            context: Batch context
            summary: Summary data
            failed: Whether the batch failed
        """
        record = {
            'event_type': summary.get('event_type', 'bulk_operation'),
            'user_id': summary.get('user_id'),
            'resource_type': summary.get('resource_type', 'Unknown'),
            'resource_id': str(summary.get('resource_id', 'bulk')),
            'batch_uuid': batch_uuid,
            'data': {
                **summary,
                'status': 'failed' if failed else 'success'
            },
            'ip_address': None,
            'context': context if context else None,
        }
        
        # Write directly to avoid recursion
        ActivityLog.objects.create(**record)
