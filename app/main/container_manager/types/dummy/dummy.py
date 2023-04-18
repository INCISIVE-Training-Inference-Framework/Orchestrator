import logging

from main.communication_adapter.communication_adapter_interface import CommunicationAdapterInterface
from main.container_manager.container_manager_interface import ContainerManagerInterface
from main.models import Execution

logger = logging.getLogger(__name__)


class ContainerManagerDummy(ContainerManagerInterface):

    def __init__(self):
        super().__init__()

    # ---> Main methods

    @staticmethod
    def start_schema_execution(execution: Execution, communication_adapter: CommunicationAdapterInterface.__class__) -> None:
        logger.debug('start_schema_execution method called')

    @staticmethod
    def end_schema_execution(execution: Execution, communication_adapter: CommunicationAdapterInterface.__class__) -> None:
        logger.debug('end_schema_execution method called')
