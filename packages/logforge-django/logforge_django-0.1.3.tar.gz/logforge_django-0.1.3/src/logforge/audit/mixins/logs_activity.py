"""
LogsActivity Mixin for Django Models

Provides automatic audit logging for Django models.
"""

import uuid
import time
import json
import logging
import datetime
import decimal
import uuid as uuid_lib
import base64
from collections.abc import Mapping, Sequence
from typing import Dict, Any, Optional, List
from django.db import models
from django.db.models.signals import post_save, post_delete, class_prepared, pre_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import ActivityLog
from ..config import get_logforge_config, validate_config

logger = logging.getLogger(__name__)


class LogsActivity:
    """
    Mixin class that provides automatic audit logging for Django models.
    """
    
    # Class-level configuration
    _logforge_config = None
    _previous_state_cache: Dict[str, Dict[str, Any]] = {}
    
    def __init_subclass__(cls, **kwargs):
        """Set up signal handlers when the class is subclassed."""
        super().__init_subclass__(**kwargs)
        
        # Get configuration
        config = get_logforge_config()
        validate_config(config)
        cls._logforge_config = config
        
        # Set up signal handlers
        cls._setup_signal_handlers()
    
    @classmethod
    def _on_pre_save(cls, sender, instance, **kwargs):
        if not isinstance(instance, sender) or not issubclass(sender, LogsActivity):
            return
        try:
            if getattr(instance, 'pk', None):
                model_class = instance.__class__
                prev = model_class.objects.filter(pk=instance.pk).first()
                if prev is not None:
                    cls._previous_state_cache[str(instance.pk)] = cls._serialize_model(prev)
        except Exception:
            pass

    @classmethod
    def _on_post_save(cls, sender, instance, created, **kwargs):
        if not isinstance(instance, sender) or not issubclass(sender, LogsActivity):
            return
        if not cls._should_log():
            return
        event_type = 'create' if created else 'update'
        try:
            from ..soft_delete import SoftDeleteDetector
            if not created and SoftDeleteDetector.has_soft_delete(cls):
                prev = cls._previous_state_cache.get(str(getattr(instance, 'pk', '')), {})
                if hasattr(instance, 'is_deleted'):
                    prev_flag = prev.get('is_deleted')
                    curr_flag = getattr(instance, 'is_deleted', False)
                    if prev_flag is False and curr_flag is True:
                        event_type = 'delete'
                    elif prev_flag is True and curr_flag is False:
                        event_type = 'restore'
                if hasattr(instance, 'deleted_at'):
                    prev_dt = prev.get('deleted_at')
                    curr_dt = getattr(instance, 'deleted_at', None)
                    if (prev_dt is None) and (curr_dt is not None):
                        event_type = 'delete'
                    elif (prev_dt is not None) and (curr_dt is None):
                        event_type = 'restore'
        except Exception:
            pass
        if not cls._should_log_event(event_type):
            return
        cls._record_audit(event_type, instance)
    
    @classmethod
    def _on_post_delete(cls, sender, instance, **kwargs):
        if not isinstance(instance, sender) or not issubclass(sender, LogsActivity):
            return
        if not cls._should_log():
            return
        event = 'delete'
        try:
            from ..soft_delete import SoftDeleteDetector
            if SoftDeleteDetector.has_soft_delete(cls):
                event = 'force_delete'
        except Exception:
            pass
        if not cls._should_log_event(event):
            return
        cls._record_audit(event, instance)
    
    @classmethod
    def _on_pre_delete(cls, sender, instance, **kwargs):
        # No-op to avoid duplicate delete logs; use post_delete only
            return
    
    @classmethod
    def _setup_signal_handlers(cls):
        """Set up Django signal handlers for audit logging."""
        try:
            post_save.disconnect(receiver=None, sender=cls)
        except Exception:
            pass
        try:
            post_delete.disconnect(receiver=None, sender=cls)
        except Exception:
            pass
        try:
            pre_save.disconnect(receiver=None, sender=cls)
        except Exception:
            pass
        pre_save.connect(cls._on_pre_save, sender=cls, weak=False, dispatch_uid=(cls, '_on_pre_save'))
        # Only log deletions on post_delete to avoid duplicates
        post_save.connect(cls._on_post_save, sender=cls, weak=False, dispatch_uid=(cls, '_on_post_save'))
        post_delete.connect(cls._on_post_delete, sender=cls, weak=False, dispatch_uid=(cls, '_on_post_delete'))
        cls._setup_soft_delete_support()
    
    @classmethod
    def _setup_soft_delete_support(cls):
        """Set up soft delete support for the model."""
        from ..soft_delete import setup_soft_delete_support
        
        setup_soft_delete_support(cls, cls._record_audit)
    
    @classmethod
    def _should_log(cls) -> bool:
        """Check if logging is enabled."""
        return cls._logforge_config.get('enabled', True)
    
    @classmethod
    def _should_log_event(cls, event_type: str) -> bool:
        """Check if a specific event type should be logged."""
        events = cls._logforge_config.get('events', [])
        if isinstance(events, list):
            return event_type in events
        elif isinstance(events, dict):
            return events.get(event_type, True)
        return True
    
    @classmethod
    def _record_audit(cls, event_type: str, instance: models.Model):
        """Record an audit log entry - unified approach matching Laravel."""
        config = cls._logforge_config
        
        # 1. Check if enabled
        if not config.get('enabled', True):
            return
        
        # 2. Performance monitoring setup
        perf_enabled = config.get('performance', {}).get('enabled', False)
        perf_sample = config.get('performance', {}).get('sample_rate', 1.0)
        perf_threshold = config.get('performance', {}).get('slow_threshold_ms', 100)
        perf_sample_hit = perf_enabled and (time.time() % 1.0) <= max(0.0, min(1.0, perf_sample))
        start_time = time.time() if perf_sample_hit else None
        
        # 3. Event filtering
        events = config.get('events', [])
        if isinstance(events, list):
            should_log = event_type in events
        elif isinstance(events, dict):
            should_log = events.get(event_type, True)
        else:
            should_log = True
        
        if not should_log:
            return
        
        # 4. Get resource info
        resource_type = cls.__name__
        resource_id = str(instance.pk)
        
        # 5. Build event data
        build_start = time.time() if perf_sample_hit else None
        
        if event_type == 'create':
            data = {'new': cls._serialize_model(instance)}
        elif event_type == 'update':
            data = cls._compute_diff(instance, config)
        elif event_type == 'delete':
            data = {'deleted': cls._serialize_model(instance)}
        elif event_type == 'restore':
            data = {'restored': cls._serialize_model(instance)}
        elif event_type == 'force_delete':
            data = {'deleted': cls._serialize_model(instance)}
        else:
            data = {}
        
        # 6. Apply data processing pipeline (matching Laravel exactly)
        data = cls._apply_model_attribute_filters(instance, data, config)
        # If update produced no fields after filtering, skip logging
        if event_type == 'update':
            old_part = data.get('old') or {}
            new_part = data.get('new') or {}
            changed_part = data.get('changed') or []
            if not old_part and not new_part and not changed_part:
                return
        redact_attributes = cls._get_redact_attributes(instance, config)
        data = cls._apply_redaction(data, redact_attributes)
        payload_max_bytes = config.get('payload_max_bytes', 65536)
        data = cls._apply_payload_cap(data, payload_max_bytes)
        data = cls._sanitize_payload(data)
        
        build_time = (time.time() - build_start) * 1000 if build_start else None
        
        # 7. Build record
        record = {
            'event_type': event_type,
            'user_id': cls._resolve_actor(config),
            'resource_type': resource_type,
            'resource_id': resource_id,
            'data': data,
            'ip_address': cls._resolve_ip(config),
            'context': cls._resolve_context(config),
        }
        
        # 8. Normalize and validate record prior to write
        record = cls._normalize_record(record)
        record = cls._ensure_encodable(record)
        
        # 9. Final validation gate
        if not cls._validate_record(record, config):
            logger.warning('LogForge skipped invalid audit record', extra={
                'event_type': event_type,
                'model_class': cls.__name__,
                'model_key': resource_id,
            })
            return
        
        # 10. Write record
        write_start = time.time() if perf_sample_hit else None
        
        try:
            writer = config.get('writer', 'db')
            if writer == 'db':
                cls._write_to_database(record)
            elif writer == 'queue':
                cls._write_to_queue(record, config)
            else:
                raise ValueError(f"Invalid writer: {writer}")
        except Exception as e:
            if config.get('suppress_exceptions', True):
                logger.warning('LogForge writer failed', extra={
                    'exception': type(e).__name__,
                    'message': str(e),
                    'event_type': event_type,
                    'model_class': cls.__name__,
                    'model_key': resource_id,
                    'user_id': record.get('user_id'),
                    'ip_address': record.get('ip_address'),
                    'context_keys': list(record.get('context', {}).keys()) if record.get('context') else None,
                })
                return
            raise e
        
        write_time = (time.time() - write_start) * 1000 if write_start else None
        
        # 11. Performance monitoring
        if perf_sample_hit and start_time:
            total_time = (time.time() - start_time) * 1000
            if total_time >= perf_threshold:
                logger.warning('LogForge slow audit operation', extra={
                    'event_type': event_type,
                    'model_class': cls.__name__,
                    'model_key': resource_id,
                    'total_ms': int(total_time),
                    'build_ms': int(build_time) if build_time else None,
                    'write_ms': int(write_time) if write_time else None,
                })
    
    @classmethod
    def _validate_record(cls, record: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Validate audit record before writing."""
        events = config.get('events', ['create', 'update', 'delete', 'restore', 'force_delete'])
        if isinstance(events, dict):
            allowed = [k for k, v in events.items() if v]
        else:
            allowed = events
        
        if record['event_type'] not in allowed:
            return False
        
        if record['user_id'] and len(str(record['user_id'])) > 255:
            return False
        
        if len(str(record['resource_type'])) > 255 or len(str(record['resource_id'])) > 255:
            return False
        
        return True
    
    
    @classmethod
    def _serialize_model(cls, instance: models.Model) -> Dict[str, Any]:
        """Serialize model instance to dictionary."""
        def make_json_safe(value):
            # Primitive fast path
            if value is None or isinstance(value, (str, int, float, bool)):
                return value
            # Datetime/date/time
            if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
                try:
                    return value.isoformat()
                except Exception:
                    return str(value)
            # Decimal
            if isinstance(value, decimal.Decimal):
                try:
                    return float(value)
                except Exception:
                    return str(value)
            # UUID
            if isinstance(value, (uuid_lib.UUID,)):
                return str(value)
            # Bytes
            if isinstance(value, (bytes, bytearray, memoryview)):
                try:
                    return base64.b64encode(bytes(value)).decode('ascii')
                except Exception:
                    return str(value)
            # Mapping (dict-like)
            if isinstance(value, Mapping):
                return {str(k): make_json_safe(v) for k, v in value.items()}
            # Sequences (list/tuple/set), but not strings/bytes handled above
            if isinstance(value, (list, tuple, set)):
                return [make_json_safe(v) for v in list(value)]
            # Django model instances or other objects
            if hasattr(value, '_meta') and hasattr(value, 'pk'):
                return str(getattr(value, 'pk', None) or value)
            # Fallback
            try:
                json.dumps(value)
                return value
            except Exception:
                return str(value)

        data: Dict[str, Any] = {}
        for field in instance._meta.fields:
            if field.primary_key:
                continue
            try:
                raw_value = field.value_from_object(instance)
            except Exception:
                raw_value = getattr(instance, field.name, None)
            data[field.name] = make_json_safe(raw_value)
        return data
    
    @classmethod
    def _compute_diff(cls, instance: models.Model, config: Dict[str, Any]) -> Dict[str, Any]:
        """Compute diff for update operations."""
        ignore_columns = set(config.get('ignore_columns', ['updated_at']))
        snapshot_on_update = bool(config.get('snapshot_on_update', False))
        current_data = cls._serialize_model(instance)
        previous_data = {}
        prev_key = str(getattr(instance, 'pk', ''))
        if prev_key and prev_key in cls._previous_state_cache:
            previous_data = cls._previous_state_cache.pop(prev_key, {})
        elif getattr(instance, 'pk', None):
            try:
                prev = instance.__class__.objects.filter(pk=instance.pk).first()
                if prev is not None:
                    previous_data = cls._serialize_model(prev)
            except Exception:
                previous_data = {}
        changed_keys: List[str] = []
        for key in current_data.keys():
            if key in ignore_columns:
                continue
            if previous_data.get(key) != current_data.get(key):
                changed_keys.append(key)
        if snapshot_on_update:
            return {
                'old': previous_data or {},
                'new': current_data or {},
                'changed': changed_keys or [],
            }
        old_subset = {k: previous_data.get(k) for k in changed_keys}
        new_subset = {k: current_data.get(k) for k in changed_keys}
        return {
            'old': old_subset or {},
            'new': new_subset or {},
            'changed': changed_keys or [],
        }
    
    @classmethod
    def _apply_model_attribute_filters(cls, instance: models.Model, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply include/exclude filters per model."""
        model_class = instance.__class__
        module_key = f'{model_class.__module__}.{model_class.__name__}'
        app_label_key = f'{instance._meta.app_label}.{model_class.__name__}'
        per_model_all = config.get('per_model', {})
        per_model_config = per_model_all.get(module_key, per_model_all.get(app_label_key, {}))
        
        include = per_model_config.get('include', config.get('include', []))
        exclude = per_model_config.get('exclude', config.get('exclude', []))
        
        def filter_keys(keys: List[str]) -> List[str]:
            if include:
                return [k for k in keys if k in include]
            if exclude:
                return [k for k in keys if k not in exclude]
            return keys

        def filter_data(data_dict):
            if include:
                return {k: v for k, v in data_dict.items() if k in include}
            if exclude:
                return {k: v for k, v in data_dict.items() if k not in exclude}
            return data_dict
        
        for section, values in data.items():
            if isinstance(values, dict):
                data[section] = filter_data(values)
            elif section == 'changed' and isinstance(values, list):
                data[section] = filter_keys(values)
        
        return data
    
    @classmethod
    def _get_redact_attributes(cls, instance: models.Model, config: Dict[str, Any]) -> List[str]:
        """Get redaction attributes for the model."""
        model_class = instance.__class__
        module_key = f'{model_class.__module__}.{model_class.__name__}'
        app_label_key = f'{instance._meta.app_label}.{model_class.__name__}'
        per_model_all = config.get('per_model', {})
        per_model_config = per_model_all.get(module_key, per_model_all.get(app_label_key, {}))
        
        return per_model_config.get('redact', config.get('redact', []))
    
    @classmethod
    def _apply_redaction(cls, data: Dict[str, Any], redact_keys: List[str]) -> Dict[str, Any]:
        """Apply redaction to sensitive fields with dot notation support."""
        if not redact_keys:
            return data
        
        dot_paths = [k for k in redact_keys if isinstance(k, str) and '.' in k]
        simple_keys = [k for k in redact_keys if isinstance(k, str) and '.' not in k]
        
        def redact_value(value):
            if isinstance(value, (list, tuple)):
                return ['********'] * len(value)
            return '********'
        
        def redact_dict(data_dict):
            """Apply redaction by exact key name at any depth."""
            result = {}
            for key, value in data_dict.items():
                if key in simple_keys:
                    result[key] = redact_value(value)
                elif isinstance(value, dict):
                    result[key] = redact_dict(value)
                else:
                    result[key] = value
            return result
        
        result = redact_dict(data)
        
        for path in dot_paths:
            if cls._has_nested_key(result, path):
                value = cls._get_nested_key(result, path)
                cls._set_nested_key(result, path, redact_value(value))
        
        return result
    
    @classmethod
    def _has_nested_key(cls, data: Dict[str, Any], path: str) -> bool:
        """Check if nested key exists using dot notation."""
        keys = path.split('.')
        current = data
        
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return False
            current = current[key]
        return True
    
    @classmethod
    def _get_nested_key(cls, data: Dict[str, Any], path: str) -> Any:
        """Get nested key value using dot notation."""
        keys = path.split('.')
        current = data
        
        for key in keys:
            current = current[key]
        return current
    
    @classmethod
    def _set_nested_key(cls, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set nested key value using dot notation."""
        keys = path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    @classmethod
    def _apply_payload_cap(cls, data: Dict[str, Any], max_bytes: int) -> Dict[str, Any]:
        """Apply payload size cap with intelligent truncation matching Laravel."""
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            if len(json_str.encode('utf-8')) <= max_bytes:
                return data
            
            max_items_per_section = 25
            max_string_length = 500
            max_depth = 2
            
            def truncate_value(value: Any, depth: int = 0) -> Any:
                """Recursively truncate values while preserving structure."""
                if depth > max_depth:
                    return '[...]'
                
                if isinstance(value, str):
                    if len(value) > max_string_length:
                        return value[:max_string_length] + '…'
                    return value
                
                if isinstance(value, (list, tuple)):
                    limited = []
                    for i, item in enumerate(value):
                        if i >= max_items_per_section:
                            limited.append('__more: truncated')
                            break
                        limited.append(truncate_value(item, depth + 1))
                    return limited
                
                if isinstance(value, dict):
                    limited = {}
                    counter = 0
                    for key, val in value.items():
                        limited[key] = truncate_value(val, depth + 1)
                        counter += 1
                        if counter >= max_items_per_section:
                            limited['__more'] = 'truncated'
                            break
                    return limited
                
                return value
            
            limited_payload = {}
            for key, value in data.items():
                limited_payload[key] = truncate_value(value, 0)
            
            limited_payload['_truncated'] = True
            return limited_payload
            
        except (TypeError, ValueError):
            return data
    
    @classmethod
    def _truncate_payload(cls, data: Dict[str, Any], max_bytes: int) -> Dict[str, Any]:
        """Truncate payload to fit within size limit."""
        truncated = {}
        current_size = 0
        
        for key, value in data.items():
            key_str = f'"{key}":'
            value_str = json.dumps(value, ensure_ascii=False)
            item_str = key_str + value_str + ','
            
            if current_size + len(item_str.encode('utf-8')) > max_bytes:
                truncated['_truncated'] = True
                break
                
            truncated[key] = value
            current_size += len(item_str.encode('utf-8'))
        
        return truncated
    
    @classmethod
    def _sanitize_payload(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize payload data."""
        def sanitize_value(value):
            if isinstance(value, str):
                import re
                value = re.sub(r'<[^>]+>', '', value)
                if len(value) > 4000:
                    value = value[:4000] + ''
                return value
            elif isinstance(value, dict):
                return {k: sanitize_value(v) for k, v in value.items()}
            elif isinstance(value, (list, tuple)):
                return [sanitize_value(v) for v in value]
            elif hasattr(value, '__dict__'):
                return '[object]'
            return value
        
        return sanitize_value(data)
    
    @classmethod
    def _resolve_actor(cls, config: Dict[str, Any]) -> Optional[str]:
        """Resolve the actor (user) for the audit log."""
        resolver = config.get('actor', {}).get('resolver')
        if resolver:
            try:
                if callable(resolver):
                    return str(resolver())
                elif isinstance(resolver, str) and '.' in resolver:
                    module_name, func_name = resolver.rsplit('.', 1)
                    module = __import__(module_name, fromlist=[func_name])
                    func = getattr(module, func_name)
                    return str(func())
            except Exception:
                pass
        
        # Fallback: pull user id from request context middleware
        try:
            from ..middleware.request_context import get_current_user_id
            uid = get_current_user_id()
            if uid:
                return str(uid)
        except Exception:
            pass
        
        # Return default
        return config.get('actor', {}).get('default')
    
    @classmethod
    def _resolve_ip(cls, config: Dict[str, Any]) -> Optional[str]:
        """Resolve IP address from request context."""
        capture_ip = config.get('context', {}).get('capture_ip', True)
        if not capture_ip:
            return None
        try:
            from ..middleware.request_context import get_current_ip
            return get_current_ip()
        except Exception:
            return None
    
    @classmethod
    def _resolve_context(cls, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Resolve additional context."""
        context = {}
        capture_ua = config.get('context', {}).get('capture_user_agent', True)
        if capture_ua:
            try:
                from ..middleware.request_context import get_current_user_agent
                ua = get_current_user_agent()
                if ua:
                    context['user_agent'] = ua
            except Exception:
                pass
        return context if context else None
    
    @classmethod
    def _normalize_record(cls, record: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize record fields."""
        record['event_type'] = str(record['event_type'])
        record['user_id'] = str(record['user_id'])[:255] if record['user_id'] else None
        record['resource_type'] = str(record['resource_type'])[:255]
        record['resource_id'] = str(record['resource_id'])[:255]
        
        return record
    
    @classmethod
    def _ensure_encodable(cls, record: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure record is JSON encodable."""
        try:
            json.dumps(record['data'])
        except (TypeError, ValueError):
            # Attempt a best-effort conversion before giving up
            def to_safe(v):
                if v is None or isinstance(v, (str, int, float, bool)):
                    return v
                if isinstance(v, (datetime.datetime, datetime.date, datetime.time)):
                    return v.isoformat()
                if isinstance(v, decimal.Decimal):
                    try:
                        return float(v)
                    except Exception:
                        return str(v)
                if isinstance(v, (uuid_lib.UUID,)):
                    return str(v)
                if isinstance(v, (bytes, bytearray, memoryview)):
                    try:
                        return base64.b64encode(bytes(v)).decode('ascii')
                    except Exception:
                        return str(v)
                if isinstance(v, Mapping):
                    return {str(k): to_safe(val) for k, val in v.items()}
                if isinstance(v, (list, tuple, set)):
                    return [to_safe(val) for val in list(v)]
                if hasattr(v, '_meta') and hasattr(v, 'pk'):
                    return str(getattr(v, 'pk', None) or v)
                try:
                    json.dumps(v)
                    return v
                except Exception:
                    return str(v)
            safe_data = to_safe(record.get('data'))
            try:
                json.dumps(safe_data)
                record['data'] = safe_data
            except Exception:
                record['data'] = {'_error': 'payload_not_json_serializable'}
        
        if record['context']:
            try:
                json.dumps(record['context'])
            except (TypeError, ValueError):
                record['context'] = {'_error': 'context_not_json_serializable'}
        
        return record
    
    @classmethod
    def _write_to_database(cls, record: Dict[str, Any]):
        """Write audit record via DatabaseWriter to support batching/context injection."""
        from ..writers import DatabaseWriter
        DatabaseWriter().write(record)
    
    @classmethod
    def _write_to_queue(cls, record: Dict[str, Any], config: Dict[str, Any]):
        """Write audit record to queue using QueueWriter."""
        from ..writers import QueueWriter
        
        writer = QueueWriter()
        writer.write(record)

    def delete(self, using=None, keep_parents=False):
        # Do not log here; post_delete signal handles logging to prevent duplicates
        return super().delete(using=using, keep_parents=keep_parents)

    def force_delete(self, using=None, keep_parents=False):
        # Do not log here; if you implement true force delete semantics,
        # wire it to post_delete appropriately.
        return super().delete(using=using, keep_parents=keep_parents)


def _class_prepared_receiver(sender, **kwargs):
    try:
        if isinstance(sender, type) and issubclass(sender, LogsActivity):
            cfg = get_logforge_config()
            try:
                validate_config(cfg)
            except Exception:
                pass
            sender._logforge_config = cfg
            sender._setup_signal_handlers()
    except Exception:
        pass

class_prepared.connect(_class_prepared_receiver, weak=False)
