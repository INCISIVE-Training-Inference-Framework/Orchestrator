import logging

from main.factory import Factory
from main.models import Execution

logger = logging.getLogger(__name__)


class Domain:

    def __init__(self):
        raise Exception('This static class can not be instantiated')

    @staticmethod
    def start_schema_execution(execution: Execution):
        container_manager = Factory.get_container_manager(execution.schema.implementation)
        container_manager.start_schema_execution(execution)
