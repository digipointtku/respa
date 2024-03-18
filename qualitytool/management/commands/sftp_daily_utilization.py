from django.core.management.base import BaseCommand
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.conf import settings
from datetime import datetime
from qualitytool.models import ResourceQualityTool
from qualitytool.manager import qt_manager
import os.path as _
import logging
import paramiko


logger = logging.getLogger()

class Command(BaseCommand):
    help = "Uploads daily utilization to a sftp server."

    def add_arguments(self, parser):
        parser.add_argument('path')
        parser.add_argument('--date', action='store')

    def handle(self, *args, **options):
        path = options.get('path')
        date = options.get('date', None)

        if not settings.QUALITYTOOL_SFTP_HOST:
            raise ImproperlyConfigured('Missing env setting: QUALITYTOOL_SFTP_HOST')

        if date:
            date = timezone.make_aware(datetime.strptime(date, '%Y-%m-%d'))
        else:
            date = timezone.now()

    
        daily_utilizations = [
            qt_manager.get_daily_utilization(qualitytool, date) 
            for qualitytool in ResourceQualityTool.objects.all()
        ]

        if not daily_utilizations:
            return
        

        transport = paramiko.Transport((settings.QUALITYTOOL_SFTP_HOST, settings.QUALITYTOOL_SFTP_PORT))

        transport.connect(
            username=settings.QUALITYTOOL_SFTP_USERNAME, 
            password=settings.QUALITYTOOL_SFTP_PASSWORD)

        sftp = paramiko.SFTPClient.from_transport(transport)




        with sftp.open(path, 'w') as csv_file:
            for daily_utilization in daily_utilizations:
                csv_file.write('%(row)s\n' % ({
                    'row': ','.join(str(val) for val in daily_utilization.values())
                }))
        logging.info(f'Generated new daily utilization csv file with {len(daily_utilizations)} entries.')