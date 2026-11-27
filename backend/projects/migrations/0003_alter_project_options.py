from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_rename_projects_pr_created_idx_projects_pr_created_6b02e3_idx_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['-created_at', '-id']},
        ),
    ]
