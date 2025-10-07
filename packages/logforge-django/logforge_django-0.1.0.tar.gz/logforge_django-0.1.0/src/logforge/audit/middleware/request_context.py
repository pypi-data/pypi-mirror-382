"""
Request Context Middleware for LogForge Django

Captures client IP and user agent from each request and stores them in
thread-local storage so audit logging can read them without tight coupling
to Django's request objects.
"""

import threading
from typing import Optional, Dict, Any

from django.http import HttpRequest


_thread_local = threading.local()


def _set_context(context: Dict[str, Any]) -> None:
	_thread_local.logforge_context = context
	# Also preserve request if already set
	if not hasattr(_thread_local, 'logforge_request'):
		_thread_local.logforge_request = None


def _clear_context() -> None:
	_thread_local.logforge_context = {}
	_thread_local.logforge_request = None


def _set_request(request: HttpRequest) -> None:
	_thread_local.logforge_request = request


def _get_request() -> Optional[HttpRequest]:
	return getattr(_thread_local, 'logforge_request', None)


def get_current_request_context() -> Dict[str, Any]:
	"""Return the current request context captured by the middleware."""
	return getattr(_thread_local, 'logforge_context', {}) or {}


def get_current_ip() -> Optional[str]:
	request = _get_request()
	if request is not None:
		# Prefer X-Forwarded-For (first IP) when present
		xff = request.META.get('HTTP_X_FORWARDED_FOR')
		if xff:
			parts = [p.strip() for p in xff.split(',') if p.strip()]
			if parts:
				return parts[0]
		return request.META.get('REMOTE_ADDR')
	return get_current_request_context().get('ip')


def get_current_user_agent() -> Optional[str]:
	request = _get_request()
	if request is not None:
		return request.META.get('HTTP_USER_AGENT')
	return get_current_request_context().get('user_agent')


def get_current_user_id() -> Optional[str]:
	request = _get_request()
	if request is not None:
		try:
			user = getattr(request, 'user', None)
			if user is not None and getattr(user, 'is_authenticated', False):
				return str(getattr(user, 'pk', None))
		except Exception:
			pass
	return get_current_request_context().get('user_id')


class RequestContextMiddleware:
	"""
	Simple middleware that captures client IP and user agent.

	Add to settings.MIDDLEWARE:
		'logforge.audit.middleware.request_context.RequestContextMiddleware'
	"""

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request: HttpRequest):
		try:
			_set_request(request)
			_set_context({
				# Keep initial snapshot, but user_id may be filled later by DRF auth
				'ip': self._extract_ip(request),
				'user_agent': self._extract_user_agent(request),
				'user_id': self._extract_user_id(request),
			})
			response = self.get_response(request)
			return response
		finally:
			_clear_context()

	@staticmethod
	def _extract_ip(request: HttpRequest) -> Optional[str]:
		# Prefer X-Forwarded-For (first IP) when present
		xff = request.META.get('HTTP_X_FORWARDED_FOR')
		if xff:
			# e.g., 'client, proxy1, proxy2' → take leftmost
			parts = [p.strip() for p in xff.split(',') if p.strip()]
			if parts:
				return parts[0]
		# Fallback to REMOTE_ADDR
		return request.META.get('REMOTE_ADDR')

	@staticmethod
	def _extract_user_agent(request: HttpRequest) -> Optional[str]:
		return request.META.get('HTTP_USER_AGENT')

	@staticmethod
	def _extract_user_id(request: HttpRequest) -> Optional[str]:
		try:
			user = getattr(request, 'user', None)
			if user is not None and getattr(user, 'is_authenticated', False):
				return str(getattr(user, 'pk', None))
			return None
		except Exception:
			return None
