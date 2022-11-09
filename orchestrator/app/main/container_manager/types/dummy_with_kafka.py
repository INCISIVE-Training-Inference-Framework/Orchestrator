from main.communication_adapter.types.kafka import CommunicationAdapterKafka
from main.container_manager.container_manager_interface import ContainerManagerInterface
from main.models import Job, JobStatus


class ContainerManagerDummyWithKafka(ContainerManagerInterface):
    communication_adapter = CommunicationAdapterKafka
    initialized = False

    def __init__(self):
        super().__init__()

    # ---> Main methods

    @classmethod
    def start_job_execution(cls, platform_adapter, ai_engine_id: int, ai_engine_container_name: str, ai_engine_container_version: str, job: Job) -> None:
        if not cls.initialized:
            cls.communication_adapter.initialize()
            cls.initialized = True
        cls.communication_adapter.prepare_execution(job.complete_id)

    @staticmethod
    def get_job_status(job: Job) -> JobStatus:
        return JobStatus.RUNNING

    @classmethod
    def ended_job_execution(cls, job: Job, finish_status: JobStatus.choices) -> None:
        cls.communication_adapter.finalize_execution(job.complete_id)
