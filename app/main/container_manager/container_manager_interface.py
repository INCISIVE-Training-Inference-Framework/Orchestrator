import abc

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
    def start_schema_execution(execution: Execution) -> None:
        raise NotImplementedError('Method not implemented in interface class')
