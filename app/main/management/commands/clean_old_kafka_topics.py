from django.core.management.base import BaseCommand

from main.communication_adapter.types.kafka import CommunicationAdapterKafka


class Command(BaseCommand):
    help = 'Cleans old kafka topics'

    def handle(self, *args, **options):
        CommunicationAdapterKafka.clean_old_topics()
