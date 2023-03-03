import abc

from main.models import Job, JobSchemaStatus


class ContainerManagerInterface(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):  # to check that the subclasses follow the interface
        return (hasattr(subclass, 'start_job_execution') and
                callable(subclass.start_job_execution) and
                hasattr(subclass, 'get_job_status') and
                callable(subclass.get_job_status) and
                hasattr(subclass, 'ended_job_execution') and
                callable(subclass.ended_job_execution) or
                NotImplemented)

    def __init__(self):
        raise Exception('This static class can not be instantiated')

    # ---> Main methods

    @staticmethod
    def start_job_execution(platform_adapter, ai_engine_id: int, ai_engine_container_name: str, ai_engine_container_version: str, job: Job) -> None:
        raise NotImplementedError('Method not implemented in interface class')

    @staticmethod
    def get_job_status(job: Job) -> JobSchemaStatus:
        raise NotImplementedError('Method not implemented in interface class')

    @staticmethod
    def ended_job_execution(job: Job, finish_status: JobSchemaStatus.choices) -> None:
        raise NotImplementedError('Method not implemented in interface class')
