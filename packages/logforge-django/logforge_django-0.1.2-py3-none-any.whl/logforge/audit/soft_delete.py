"""
Soft Delete Support for LogForge Django

This module provides support for soft delete operations in Django,
equivalent to Laravel's restored and forceDeleted events.
"""

import logging
from typing import Type, Any, Optional
from django.db import models
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.core.exceptions import FieldDoesNotExist

logger = logging.getLogger(__name__)


class SoftDeleteDetector:
    """
    Detects if a Django model uses soft delete functionality.
    
    Supports common soft delete patterns:
    - django-model-utils SoftDeletableModel
    - django-softdelete
    - Custom is_deleted fields
    - Custom deleted_at fields
    """
    
    @staticmethod
    def has_soft_delete(model_class: Type[models.Model]) -> bool:
        """
        Check if a model uses soft delete functionality.
        
        Args:
            model_class: The Django model class to check
            
        Returns:
            bool: True if the model uses soft delete, False otherwise
        """
        # Check for django-model-utils SoftDeletableModel
        if hasattr(model_class, '_meta') and hasattr(model_class._meta, 'get_field'):
            try:
                # Check for is_deleted field (common pattern)
                if model_class._meta.get_field('is_deleted'):
                    return True
            except FieldDoesNotExist:
                pass
            
            try:
                # Check for deleted_at field (common pattern)
                if model_class._meta.get_field('deleted_at'):
                    return True
            except FieldDoesNotExist:
                pass
        
        # Check for django-model-utils SoftDeletableModel inheritance
        if hasattr(model_class, '__bases__'):
            for base in model_class.__bases__:
                if 'SoftDeletableModel' in str(base):
                    return True
        
        # Check for django-softdelete
        if hasattr(model_class, 'objects') and hasattr(model_class.objects, 'all_with_deleted'):
            return True
        
        # Check for custom soft delete methods
        if hasattr(model_class, 'delete') and hasattr(model_class, 'restore'):
            return True
        
        return False
    
    @staticmethod
    def get_soft_delete_field(model_class: Type[models.Model]) -> Optional[str]:
        """
        Get the name of the soft delete field if it exists.
        
        Args:
            model_class: The Django model class to check
            
        Returns:
            Optional[str]: Name of the soft delete field or None
        """
        if hasattr(model_class, '_meta') and hasattr(model_class._meta, 'get_field'):
            # Check for is_deleted field
            try:
                if model_class._meta.get_field('is_deleted'):
                    return 'is_deleted'
            except FieldDoesNotExist:
                pass
            
            # Check for deleted_at field
            try:
                if model_class._meta.get_field('deleted_at'):
                    return 'deleted_at'
            except FieldDoesNotExist:
                pass
        
        return None


class SoftDeleteSignalHandler:
    """
    Handles soft delete signals for Django models.
    
    This class provides signal handlers for restore and force_delete
    operations, equivalent to Laravel's restored and forceDeleted events.
    """
    
    # Store original field values for comparison
    _original_values = {}
    
    @staticmethod
    def setup_soft_delete_signals(model_class: Type[models.Model], audit_handler):
        """
        Set up soft delete signals for a model.
        
        Args:
            model_class: The Django model class
            audit_handler: The audit logging handler function
        """
        if not SoftDeleteDetector.has_soft_delete(model_class):
            return
        
        # Set up pre_delete signal to capture original values
        @receiver(pre_delete, sender=model_class)
        def capture_pre_delete(sender, instance, **kwargs):
            """Capture original values before delete."""
            SoftDeleteSignalHandler._original_values[instance.pk] = {
                'is_deleted': getattr(instance, 'is_deleted', None),
                'deleted_at': getattr(instance, 'deleted_at', None),
            }
        
        # Set up post_save signal for restore operations
        @receiver(post_save, sender=model_class)
        def handle_restore(sender, instance, created, **kwargs):
            """Handle restore operations."""
            if created:
                return  # Skip create operations
            
            # Check if this is a restore operation
            if SoftDeleteSignalHandler._is_restore_operation(instance):
                audit_handler('restore', instance)
        
        # Set up post_delete signal for force delete operations
        @receiver(post_delete, sender=model_class)
        def handle_force_delete(sender, instance, **kwargs):
            """Handle force delete operations."""
            # Check if this is a force delete operation
            if SoftDeleteSignalHandler._is_force_delete_operation(instance):
                audit_handler('force_delete', instance)
            
            # Clean up stored values
            if instance.pk in SoftDeleteSignalHandler._original_values:
                del SoftDeleteSignalHandler._original_values[instance.pk]
    
    @staticmethod
    def _is_restore_operation(instance: models.Model) -> bool:
        """
        Check if an operation is a restore operation.
        
        Args:
            instance: The model instance
            
        Returns:
            bool: True if this is a restore operation
        """
        # Check if the instance was previously soft deleted
        if hasattr(instance, 'is_deleted'):
            # If is_deleted is False and we have a pk, it might be a restore
            return not getattr(instance, 'is_deleted', True) and instance.pk is not None
        
        if hasattr(instance, 'deleted_at'):
            # If deleted_at is None and we have a pk, it might be a restore
            return getattr(instance, 'deleted_at', None) is None and instance.pk is not None
        
        return False
    
    @staticmethod
    def _is_force_delete_operation(instance: models.Model) -> bool:
        """
        Check if an operation is a force delete operation.
        
        Args:
            instance: The model instance
            
        Returns:
            bool: True if this is a force delete operation
        """
        # Check if we have stored values for this instance
        if instance.pk in SoftDeleteSignalHandler._original_values:
            original = SoftDeleteSignalHandler._original_values[instance.pk]
            
            # If the instance was soft deleted (is_deleted=True or deleted_at not None)
            # and it's being deleted, it's a force delete
            if original.get('is_deleted') is True or original.get('deleted_at') is not None:
                return True
        
        return False


def setup_soft_delete_support(model_class: Type[models.Model], audit_handler):
    """
    Set up soft delete support for a Django model.
    
    Args:
        model_class: The Django model class
        audit_handler: The audit logging handler function
    """
    try:
        SoftDeleteSignalHandler.setup_soft_delete_signals(model_class, audit_handler)
        logger.debug(f"Soft delete support enabled for {model_class.__name__}")
    except Exception as e:
        logger.warning(
            f"Failed to set up soft delete support for {model_class.__name__}: {e}"
        )
