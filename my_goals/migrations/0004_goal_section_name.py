# Generated by Django 4.2.16 on 2024-09-15 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_goals', '0003_rename_is_completed_subtask_completed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='section_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
