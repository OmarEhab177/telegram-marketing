# Generated by Django 3.2.20 on 2023-07-16 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0002_auto_20230716_0748'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramaccount',
            name='password',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]