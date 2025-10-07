"""
Django App Configuration for LogForge Audit

This module provides the Django app configuration for the LogForge audit package.
It handles initialization, configuration validation, and service registration.
"""

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
import logging

logger = logging.getLogger(__name__)


class AuditConfig(AppConfig):
    """
    Django app configuration for LogForge Audit.
    
    This class handles the initialization and configuration of the LogForge
    audit logging package when Django starts up.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logforge.audit'
    verbose_name = 'LogForge Audit Logging'
    
    def ready(self):
        """
        Initialize the LogForge audit package.
        
        This method is called when Django starts up and the app is ready.
        It validates configuration and sets up any required services.
        """
        try:
            # Import here to avoid circular imports
            from .config import validate_config, get_logforge_config
            
            # Get and validate configuration
            config = get_logforge_config()
            validate_config(config)
            
            # Log successful initialization
            logger.info(
                'LogForge Audit initialized successfully',
                extra={
                    'writer': config.get('writer', 'db'),
                    'events': config.get('events', []),
                    'enabled': config.get('enabled', True),
                }
            )
            
            # Set up any additional services if needed
            self._setup_services(config)
            
        except Exception as e:
            logger.error(
                'LogForge Audit initialization failed',
                extra={
                    'exception': type(e).__name__,
                    'error_message': str(e),
                }
            )
            # Don't raise the exception to avoid breaking Django startup
            # Just log the error and continue
    
    def _setup_services(self, config):
        """
        Set up additional services based on configuration.
        
        Args:
            config: Validated LogForge configuration
        """
        # Set up queue writer if configured
        if config.get('writer') == 'queue':
            self._setup_queue_writer(config)
        
        # Set up performance monitoring if enabled
        if config.get('performance', {}).get('enabled', False):
            self._setup_performance_monitoring(config)
    
    def _setup_queue_writer(self, config):
        """
        Set up queue writer services.
        
        Args:
            config: LogForge configuration
        """
        try:
            # Check if Celery is available
            import celery  # noqa: F401
            logger.info('LogForge queue writer enabled with Celery')
        except ImportError:
            logger.warning(
                'LogForge queue writer configured but Celery not available. '
                'Will fallback to database writer.'
            )
    
    def _setup_performance_monitoring(self, config):
        """
        Set up performance monitoring.
        
        Args:
            config: LogForge configuration
        """
        perf_config = config.get('performance', {})
        logger.info(
            'LogForge performance monitoring enabled',
            extra={
                'slow_threshold_ms': perf_config.get('slow_threshold_ms', 100),
                'sample_rate': perf_config.get('sample_rate', 1.0),
            }
        )
