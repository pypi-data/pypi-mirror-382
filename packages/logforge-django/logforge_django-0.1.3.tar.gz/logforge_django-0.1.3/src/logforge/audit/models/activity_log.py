from django.db import models
from django.utils import timezone
import uuid


class ActivityLog(models.Model):
    """
    Django audit log model for tracking model operations.
    """
    
    event_type = models.CharField(max_length=255, help_text="Type of event (create, update, delete, etc.)")
    user_id = models.CharField(max_length=255, null=True, blank=True, help_text="ID of the user who performed the action")
    resource_type = models.CharField(max_length=255, help_text="Type of the resource being audited")
    resource_id = models.CharField(max_length=255, help_text="ID of the resource being audited")
    batch_uuid = models.UUIDField(null=True, blank=True, help_text="UUID for batch operations")
    data = models.JSONField(null=True, blank=True, help_text="Event data (diffs, snapshots, etc.)")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of the request")
    context = models.JSONField(null=True, blank=True, help_text="Additional context (user_agent, etc.)")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the audit log was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the audit log was last updated")
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['resource_type', 'resource_id'], name='idx_audit_resource'),
            models.Index(fields=['user_id'], name='idx_audit_user'),
            models.Index(fields=['event_type'], name='idx_audit_event'),
            models.Index(fields=['created_at'], name='idx_audit_created_at'),
            models.Index(fields=['batch_uuid'], name='idx_audit_batch'),
        ]
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
    
    def __str__(self):
        return f"{self.event_type} on {self.resource_type}#{self.resource_id} by {self.user_id or 'system'}"
    
    @classmethod
    def for_batch(cls, batch_uuid):
        """Filter logs by batch UUID."""
        return cls.objects.filter(batch_uuid=batch_uuid)
    
    @classmethod
    def for_resource(cls, resource_type, resource_id):
        """Filter logs by resource type and ID."""
        return cls.objects.filter(resource_type=resource_type, resource_id=resource_id)
    
    @classmethod
    def for_user(cls, user_id):
        """Filter logs by user ID."""
        return cls.objects.filter(user_id=user_id)
    
    @classmethod
    def for_event_type(cls, event_type):
        """Filter logs by event type."""
        return cls.objects.filter(event_type=event_type)
