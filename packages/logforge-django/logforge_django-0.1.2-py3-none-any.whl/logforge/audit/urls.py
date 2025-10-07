from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'logforge'

urlpatterns = [
    path('', lambda request: redirect('logforge:logs'), name='dashboard'),
    path('logs', views.logs_page, name='logs'),
    path('logs/<int:id>', views.log_detail_page, name='logs_show'),
    path('api/logs', views.api_logs, name='api_logs'),
    path('api/stats/event-types', views.api_stats_event_types, name='api_stats_event_types'),
    path('api/stats/resource-types', views.api_stats_resource_types, name='api_stats_resource_types'),
    path('api/stats/top-users', views.api_stats_top_users, name='api_stats_top_users'),
    path('assets/<str:file>', views.asset, name='assets'),
]

