from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0002_rename_comments_co_issue_idx_comments_co_issue_i_25b7b6_idx_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['created_at', 'id']},
        ),
    ]
