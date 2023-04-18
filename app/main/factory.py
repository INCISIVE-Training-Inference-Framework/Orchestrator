from main.communication_adapter.communication_adapter_interface import CommunicationAdapterInterface
from main.communication_adapter.types.kafka import CommunicationAdapterKafka
from main.container_manager.container_manager_interface import ContainerManagerInterface
from main.container_manager.types.argo_workflows.argo_workflows import ContainerManagerArgoWorkflows
from main.container_manager.types.dummy.dummy import ContainerManagerDummy


class Factory:

    def __init__(self):
        raise Exception('This static class can not be instantiated')

    @staticmethod
    def get_container_manager(implementation_type: str) -> ContainerManagerInterface.__class__:
        if implementation_type == 'argo_workflows':
            return ContainerManagerArgoWorkflows
        elif implementation_type == 'dummy':
            return ContainerManagerDummy
        else:
            raise Exception(f'Container manager implementation {implementation_type} does not exist')

    @staticmethod
    def get_communication_adapter(implementation_type: str) -> CommunicationAdapterInterface.__class__:
        if implementation_type == 'kafka':
            return CommunicationAdapterKafka
        else:
            raise Exception(f'Communication adapter implementation {implementation_type} does not exist')
