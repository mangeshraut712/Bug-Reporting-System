from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0003_issue_status_priority_checks'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issue',
            options={'ordering': ['-created_at', '-id']},
        ),
    ]
