# Generated by Django 3.2.20 on 2023-10-10 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0150_add_field_send_sms_notifications'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservationreminder',
            name='action_by_official',
        ),
        migrations.RemoveField(
            model_name='reservationreminder',
            name='notification_type',
        ),
        migrations.RemoveField(
            model_name='reservationreminder',
            name='user',
        ),
    ]
