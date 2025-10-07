import json
from datetime import datetime

from django.db import connection
from django.db import models
from django.http import JsonResponse, Http404, HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.utils.timezone import make_aware
from django.conf import settings
import os
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.staticfiles import finders
from django.urls import reverse, NoReverseMatch

from .models.activity_log import ActivityLog
from .config import get_logforge_config
from importlib import import_module


def _dashboard_allowed(user) -> bool:
    cfg = get_logforge_config()
    allow_path = (cfg.get('dashboard') or {}).get('allow')
    if allow_path:
        try:
            module_name, func_name = allow_path.rsplit('.', 1)
            mod = import_module(module_name)
            fn = getattr(mod, func_name)
            return bool(fn(user))
        except Exception:
            pass
    return bool(user.is_authenticated and getattr(user, 'is_staff', False))


def logs_page(request):
    if not _dashboard_allowed(request.user):
        from django.contrib.auth.views import redirect_to_login
        cfg = get_logforge_config()
        if (cfg.get('dashboard') or {}).get('use_admin_login'):
            try:
                admin_login_url = reverse('admin:login')
            except NoReverseMatch:
                admin_login_url = '/admin/login/'
            return redirect_to_login(next=request.get_full_path(), login_url=admin_login_url)
        return redirect_to_login(next=request.get_full_path())
    return render(request, 'logforge/dashboard/logs.html')


def log_detail_page(request, id: int):
    if not _dashboard_allowed(request.user):
        from django.contrib.auth.views import redirect_to_login
        cfg = get_logforge_config()
        if (cfg.get('dashboard') or {}).get('use_admin_login'):
            try:
                admin_login_url = reverse('admin:login')
            except NoReverseMatch:
                admin_login_url = '/admin/login/'
            return redirect_to_login(next=request.get_full_path(), login_url=admin_login_url)
        return redirect_to_login(next=request.get_full_path())
    log = get_object_or_404(ActivityLog, pk=id)
    data_pretty = None
    context_pretty = None
    try:
        if log.data is not None:
            data_pretty = json.dumps(log.data, ensure_ascii=False, indent=2)
    except Exception:
        data_pretty = None
    try:
        if log.context is not None:
            context_pretty = json.dumps(log.context, ensure_ascii=False, indent=2)
    except Exception:
        context_pretty = None

    def event_badge(event_type: str) -> str:
        if event_type == 'create':
            return 'bg-green-100 text-green-800'
        if event_type == 'update':
            return 'bg-yellow-100 text-yellow-800'
        if event_type == 'delete':
            return 'bg-red-100 text-red-800'
        if event_type == 'restore':
            return 'bg-blue-100 text-blue-800'
        if event_type == 'force_delete':
            return 'bg-red-100 text-red-800'
        if event_type == 'bulk_operation':
            return 'bg-purple-100 text-purple-800'
        return 'bg-gray-100 text-gray-800'

    return render(request, 'logforge/dashboard/log-view.html', {
        'log': log,
        'data_pretty': data_pretty,
        'context_pretty': context_pretty,
        'event_badge_class': event_badge(log.event_type or ''),
    })


def api_logs(request):
    if not _dashboard_allowed(request.user):
        return JsonResponse({'detail': 'Authentication required'}, status=403)
    # Pagination params
    try:
        per_page = int(request.GET.get('per_page', '10'))
    except ValueError:
        per_page = 10
    per_page = per_page if 1 <= per_page <= 100 else 10
    try:
        page_num = int(request.GET.get('page', '1'))
    except ValueError:
        page_num = 1

    search = (request.GET.get('search') or '').strip()
    event_type = request.GET.get('event_type') or ''
    filter_user_id = (request.GET.get('user_id') or '').strip()
    filter_resource_type = (request.GET.get('resource_type') or '').strip()
    filter_batch_uuid = (request.GET.get('batch_uuid') or '').strip()
    filter_data_q = (request.GET.get('data_q') or '').strip()
    filter_date = (request.GET.get('date') or '').strip()

    qs = ActivityLog.objects.all()

    if search:
        def try_int(s):
            try:
                return int(s)
            except Exception:
                return None

        n = try_int(search)
        if n is not None:
            qs = qs.filter(models.Q(id=n) | models.Q(user_id=str(n)) | models.Q(resource_id=str(n)))

        like_term = search.lower()
        qs = qs.filter(
            models.Q(event_type__icontains=like_term) |
            models.Q(ip_address__icontains=like_term) |
            models.Q(resource_type__icontains=like_term) |
            models.Q(batch_uuid__icontains=like_term)
        )

        driver = connection.vendor
        needle = f"%{like_term}%"
        if driver == 'postgresql':
            qs = qs.extra(where=["data::text ILIKE %s"], params=[needle])
        elif driver == 'mysql':
            qs = qs.extra(where=["LOWER(CAST(data AS CHAR)) LIKE %s"], params=[needle])
        else:  # sqlite/other
            qs = qs.extra(where=["LOWER(CAST(data AS TEXT)) LIKE %s"], params=[needle])

        try:
            date_str = datetime.fromisoformat(search).date()
            qs = qs | ActivityLog.objects.filter(created_at__date=date_str)
        except Exception:
            pass

    if event_type:
        qs = qs.filter(event_type=event_type)

    if filter_user_id:
        if filter_user_id.isnumeric():
            qs = qs.filter(user_id=str(int(filter_user_id)))
        else:
            qs = qs.none()

    if filter_resource_type:
        qs = qs.filter(resource_type__icontains=filter_resource_type.lower())

    if filter_batch_uuid:
        qs = qs.filter(batch_uuid__icontains=filter_batch_uuid.lower())

    if filter_data_q:
        driver = connection.vendor
        term = f"%{filter_data_q.lower()}%"
        if driver == 'postgresql':
            qs = qs.extra(where=["data::text ILIKE %s"], params=[term])
        elif driver == 'mysql':
            qs = qs.extra(where=["LOWER(CAST(data AS CHAR)) LIKE %s"], params=[term])
        else:
            qs = qs.extra(where=["LOWER(CAST(data AS TEXT)) LIKE %s"], params=[term])

    if filter_date:
        try:
            date_only = datetime.fromisoformat(filter_date).date()
            qs = qs.filter(created_at__date=date_only)
        except Exception:
            pass

    qs = qs.order_by('-created_at')

    paginator = Paginator(qs, per_page)
    try:
        page = paginator.page(page_num)
    except EmptyPage:
        page = paginator.page(paginator.num_pages if paginator.num_pages else 1)

    items = list(page.object_list.values(
        'id', 'created_at', 'updated_at', 'event_type', 'user_id', 'resource_type', 'resource_id', 'batch_uuid', 'ip_address', 'data', 'context'
    ))

    def normalize(item):
        item['created_at'] = item['created_at'].isoformat() if item['created_at'] else None
        item['updated_at'] = item['updated_at'].isoformat() if item['updated_at'] else None
        return item

    payload = {
        'logs': [normalize(i) for i in items],
        'pagination': {
            'current_page': page.number,
            'per_page': page.paginator.per_page,
            'total_items': page.paginator.count,
            'total_pages': page.paginator.num_pages,
            'has_prev': page.has_previous(),
            'has_next': page.has_next(),
        }
    }

    return JsonResponse(payload)


def asset(request, file: str):
    allowed = ['app.css', 'app.js']
    if file not in allowed:
        return HttpResponseNotFound()

    base_dir = os.path.dirname(__file__)
    candidate = os.path.join(base_dir, 'static', 'logforge', file)
    path = candidate if os.path.isfile(candidate) else None

    if not path:
        try:
            storage_path = staticfiles_storage.path(f'logforge/{file}')
            if os.path.isfile(storage_path):
                path = storage_path
        except Exception:
            pass

    if not path:
        found = finders.find(f'logforge/{file}')
        if found and os.path.isfile(found):
            path = found

    if not path:
        return HttpResponseNotFound()

    try:
        with open(path, 'rb') as f:
            content = f.read()
    except Exception:
        return HttpResponseNotFound()

    content_type = 'text/css' if file == 'app.css' else 'application/javascript'
    response = HttpResponse(content, content_type=content_type)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


def favicon(request):
    return HttpResponse(status=204)


def api_stats_event_types(request):
    if not _dashboard_allowed(request.user):
        return JsonResponse({'detail': 'Authentication required'}, status=403)
    data = (
        ActivityLog.objects
        .values('event_type')
        .annotate(count=models.Count('id'))
        .order_by('event_type')
    )
    return JsonResponse({'data': list(data)})


def api_stats_resource_types(request):
    if not _dashboard_allowed(request.user):
        return JsonResponse({'detail': 'Authentication required'}, status=403)
    data = (
        ActivityLog.objects
        .values('resource_type')
        .annotate(count=models.Count('id'))
        .order_by('-count')
    )
    return JsonResponse({'data': list(data)})


def api_stats_top_users(request):
    if not _dashboard_allowed(request.user):
        return JsonResponse({'detail': 'Authentication required'}, status=403)
    data = (
        ActivityLog.objects
        .exclude(user_id__isnull=True)
        .exclude(user_id='')
        .values('user_id')
        .annotate(count=models.Count('id'))
        .order_by('-count')[:10]
    )
    return JsonResponse({'data': list(data)})


