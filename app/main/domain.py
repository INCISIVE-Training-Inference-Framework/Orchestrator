import logging

from django.conf import settings

from main.factory import Factory
from main.models import Execution

logger = logging.getLogger(__name__)


class Domain:

    def __init__(self):
        raise Exception('This static class can not be instantiated')

    @staticmethod
    def start_schema_execution(execution: Execution):
        container_manager = Factory.get_container_manager(execution.schema.implementation)
        communication_adapter = Factory.get_communication_adapter(settings.COMMUNICATION_ADAPTER)
        container_manager.start_schema_execution(execution, communication_adapter)

    @staticmethod
    def end_schema_execution(execution: Execution):
        container_manager = Factory.get_container_manager(execution.schema.implementation)
        communication_adapter = Factory.get_communication_adapter(settings.COMMUNICATION_ADAPTER)
        container_manager.end_schema_execution(execution, communication_adapter)
