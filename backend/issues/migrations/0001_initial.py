# Generated migration file

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('open', 'Open'), ('in_progress', 'In Progress'), ('closed', 'Closed')], default='open', max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='medium', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assignee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_issues', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issues', to='projects.project')),
                ('reporter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reported_issues', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='issue',
            index=models.Index(fields=['status'], name='issues_issu_status_idx'),
        ),
        migrations.AddIndex(
            model_name='issue',
            index=models.Index(fields=['priority'], name='issues_issu_priority_idx'),
        ),
        migrations.AddIndex(
            model_name='issue',
            index=models.Index(fields=['project'], name='issues_issu_project_idx'),
        ),
        migrations.AddIndex(
            model_name='issue',
            index=models.Index(fields=['reporter'], name='issues_issu_reporter_idx'),
        ),
        migrations.AddIndex(
            model_name='issue',
            index=models.Index(fields=['assignee'], name='issues_issu_assignee_idx'),
        ),
    ]
