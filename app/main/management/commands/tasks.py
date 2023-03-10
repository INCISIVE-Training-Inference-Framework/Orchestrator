import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from main.domain import Domain

logger = logging.getLogger(__name__)


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = 'Runs APScheduler'

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), 'default')

        scheduler.add_job(
            Domain.update_jobs_status,
            trigger=CronTrigger(minute=f'*/{settings.UPDATE_STATUS_SECONDS_TIMER}'),
            id='update_executions_status',
            max_instances=1,
            replace_existing=True,
        )
        logger.info('Added job update_executions_status')

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week='mon', hour='00', minute='00'
            ),  # midnight on Monday, before start of the next work week.
            id='delete_old_job_executions',
            max_instances=1,
            replace_existing=True,
        )
        logger.info('Added job delete_old_job_executions')

        logger.info('Starting scheduler')
        scheduler.start()
