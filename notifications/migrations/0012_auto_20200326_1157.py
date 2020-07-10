# Generated by Django 2.2.11 on 2020-03-26 09:57

from django.db import migrations
import django.db.models.deletion
import parler.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0011_auto_20191126_1326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationtemplatetranslation',
            name='master',
            field=parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='notifications.NotificationTemplate'),
        ),
    ]
