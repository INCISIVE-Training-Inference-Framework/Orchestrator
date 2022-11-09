import abc
from typing import List

from main.models import \
    Job, \
    JobTraining, \
    JobWithPretrainedModel, \
    JobEvaluatingFromPretrainedModel, \
    JobInferencingFromPretrainedModel


class PlatformAdapterInterface(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):  # to check that the subclasses follow the interface
        return (hasattr(subclass, 'get_ai_engine_metadata') and
                callable(subclass.check_ai_engine_correctness_and_get_container_metadata) and
                hasattr(subclass, 'get_model_metadata') and
                callable(subclass.check_model_correctness_and_get_ai_engine) or
                NotImplemented)

    def __init__(self):
        raise Exception('This static class can not be instantiated')

    # ---> Main methods

    @staticmethod
    def check_ai_engine_correctness_and_get_container_metadata(_id: int, job: Job) -> (str, str):
        raise NotImplementedError('Method not implemented in interface class')

    @staticmethod
    def check_model_correctness_and_get_ai_engine(job: JobWithPretrainedModel) -> int:
        raise NotImplementedError('Method not implemented in interface class')

    @staticmethod
    def get_model_metadata(ai_engine_id: int, job: JobTraining) -> dict:
        raise NotImplementedError('Method not implemented in interface class')

    @staticmethod
    def get_metrics_metadata(data_partner: str, data_partner_patients: List[str], job: JobTraining or JobEvaluatingFromPretrainedModel) -> dict:
        raise NotImplementedError('Method not implemented in interface class')

    @staticmethod
    def get_inference_results_metadata(job: JobInferencingFromPretrainedModel) -> dict:
        raise NotImplementedError('Method not implemented in interface class')
