from typing import List

from main.models import \
    Job, \
    JobTraining, \
    JobWithPretrainedModel, \
    JobEvaluatingFromPretrainedModel, \
    JobInferencingFromPretrainedModel
from main.platform_adapter.platform_adapter_interface import PlatformAdapterInterface


class DummyPlatformAdapter(PlatformAdapterInterface):

    def __init__(self):
        super().__init__()

    # ---> Main methods

    @staticmethod
    def check_ai_engine_correctness_and_get_container_metadata(_id: int, job: Job) -> (str, str):
        return 'container_name', 'container_version'

    @staticmethod
    def check_model_correctness_and_get_ai_engine(job: JobWithPretrainedModel) -> int:
        return 1

    @staticmethod
    def get_model_metadata(ai_engine_id: int, job: JobTraining) -> dict:
        return {}

    @staticmethod
    def get_metrics_metadata(data_partner: str, data_partner_patients: List[str], job: JobTraining or JobEvaluatingFromPretrainedModel) -> dict:
        return {}

    @staticmethod
    def get_inference_results_metadata(job: JobInferencingFromPretrainedModel) -> dict:
        return {}
