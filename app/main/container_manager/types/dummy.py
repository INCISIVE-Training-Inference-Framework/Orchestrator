from main.container_manager.container_manager_interface import ContainerManagerInterface
from main.models import Job, JobSchemaStatus


class ContainerManagerDummy(ContainerManagerInterface):

    def __init__(self):
        super().__init__()

    # ---> Main methods

    @staticmethod
    def start_job_execution(platform_adapter, ai_engine_id: int, ai_engine_container_name: str, ai_engine_container_version: str, job: Job) -> None:
        pass

    @staticmethod
    def get_job_status(job: Job) -> JobSchemaStatus:
        return JobSchemaStatus.RUNNING

    @staticmethod
    def ended_job_execution(job: Job, finish_status: JobSchemaStatus.choices) -> None:
        pass
