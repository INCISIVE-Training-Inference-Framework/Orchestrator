import abc


class CommunicationAdapterInterface(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):  # to check that the subclasses follow the interface
        return (hasattr(subclass, 'initialize') and
                callable(subclass.initialize) and
                hasattr(subclass, 'prepare_execution') and
                callable(subclass.prepare_execution) and
                hasattr(subclass, 'evaluating_from_pretrained_model') and
                callable(subclass.finalize_execution) and
                hasattr(subclass, 'finalize_execution') or
                NotImplemented)

    def __init__(self):
        raise Exception('This static class can not be instantiated')

    # ---> Main methods

    @staticmethod
    def initialize() -> None:
        raise NotImplementedError('Method not implemented in interface class')

    @staticmethod
    def prepare_execution(execution_id: str) -> None:
        raise NotImplementedError('Method not implemented in interface class')

    @staticmethod
    def finalize_execution(execution_id: str) -> None:
        raise NotImplementedError('Method not implemented in interface class')
