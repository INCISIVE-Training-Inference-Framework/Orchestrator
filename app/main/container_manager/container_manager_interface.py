import abc

from main.communication_adapter.communication_adapter_interface import CommunicationAdapterInterface
from main.models import Execution


class ContainerManagerInterface(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):  # to check that the subclasses follow the interface
        return (hasattr(subclass, 'start_schema_execution') and
                callable(subclass.start_schema_execution) or
                NotImplemented)

    def __init__(self):
        raise Exception('This static class can not be instantiated')

    # ---> Main methods

    @staticmethod
    def start_schema_execution(execution: Execution, communication_adapter: CommunicationAdapterInterface.__class__) -> None:
        raise NotImplementedError('Method not implemented in interface class')

    @staticmethod
    def end_schema_execution(execution: Execution, communication_adapter: CommunicationAdapterInterface.__class__) -> None:
        raise NotImplementedError('Method not implemented in interface class')
