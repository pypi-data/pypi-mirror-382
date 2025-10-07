from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(help_text='Type of event (create, update, delete, etc.)', max_length=255)),
                ('user_id', models.CharField(blank=True, help_text='ID of the user who performed the action', max_length=255, null=True)),
                ('resource_type', models.CharField(help_text='Type of the resource being audited', max_length=255)),
                ('resource_id', models.CharField(help_text='ID of the resource being audited', max_length=255)),
                ('batch_uuid', models.UUIDField(blank=True, help_text='UUID for batch operations', null=True)),
                ('data', models.JSONField(blank=True, help_text='Event data (diffs, snapshots, etc.)', null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text='IP address of the request', null=True)),
                ('context', models.JSONField(blank=True, help_text='Additional context (user_agent, etc.)', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When the audit log was created')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='When the audit log was last updated')),
            ],
            options={
                'verbose_name': 'Activity Log',
                'verbose_name_plural': 'Activity Logs',
                'db_table': 'audit_logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['resource_type', 'resource_id'], name='idx_audit_resource'),
        ),
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['user_id'], name='idx_audit_user'),
        ),
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['event_type'], name='idx_audit_event'),
        ),
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['created_at'], name='idx_audit_created_at'),
        ),
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['batch_uuid'], name='idx_audit_batch'),
        ),
    ]
