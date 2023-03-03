from typing import List

import requests
from django.conf import settings

from main.domain.exceptions import UserError, InternalError
from main.models import \
    Job, \
    JobTraining, \
    JobTrainingFromPretrainedModel, \
    JobWithPretrainedModel, \
    JobEvaluatingFromPretrainedModel, \
    JobInferencingFromPretrainedModel
from main.platform_adapter.platform_adapter_interface import PlatformAdapterInterface


class MaaSPlatformAdapter(PlatformAdapterInterface):

    def __init__(self):
        super().__init__()

    # ---> Main methods

    @staticmethod
    def check_ai_engine_correctness_and_get_container_metadata(_id: int, job: Job) -> (str, str):
        error_message = 'Error while checking AI Engine existence'
        url = f'http://{settings.MAAS_API_HOSTNAME}/api/ai_engines/{_id}/'
        try:
            response = requests.get(url)
            status_code = response.status_code
            if status_code == 200:
                metadata = response.json()

                # check if the use case is supported
                if job.use_case not in metadata['job_use_cases']:
                    raise UserError('The specified use case is not supported by the AI Engine')

                if job.is_parallel and isinstance(job, JobTraining):
                    if settings.MERGING_MODELS not in metadata['job_use_cases']:
                        raise UserError('The AI Engine must support merging models in the case of parallel training')

                return metadata['container_name'], metadata['container_version']
            elif status_code == 404:
                raise UserError('The specified AI Engine does not exist')
            else:
                raise InternalError(
                    f'{error_message}. Status code: {status_code}. Message: {response.text}',
                    error_message
                )
        except requests.exceptions.RequestException as e:
            raise InternalError(
                f'{error_message}. {e}',
                error_message
            )
        except KeyError as e:
            raise InternalError(
                f'{error_message}. {e}',
                error_message
            )

    @staticmethod
    def check_model_correctness_and_get_ai_engine(job: JobWithPretrainedModel) -> int:
        error_message = 'Error while checking model correctness and getting its ai engine'
        url = f'http://{settings.MAAS_API_HOSTNAME}/api/models/{job.model_id}/'
        try:
            response = requests.get(url)
            status_code = response.status_code
            if status_code == 200:
                metadata = response.json()
                ai_engine_id = int(metadata['ai_engine'].split('/')[-2])  # hyperlinked API
                return ai_engine_id
            elif status_code == 404:
                raise UserError('The specified Model does not exist')
            else:
                raise InternalError(
                    f'{error_message}. Status code: {status_code}. Message: {response.text}',
                    error_message
                )
        except requests.exceptions.RequestException as e:
            raise InternalError(
                f'{error_message}. {e}',
                error_message
            )
        except KeyError as e:
            raise InternalError(
                f'{error_message}. {e}',
                error_message
            )

    @staticmethod
    def get_model_metadata(ai_engine_id: int, job: JobTraining) -> dict:
        metadata = {
            'name': job.model_name,
            'type': job.model_type,
            'data_partners_patients': job.parsed_data_partners_patients,
            'description': job.model_description,
            'ai_engine': ai_engine_id
        }
        if isinstance(job, JobTrainingFromPretrainedModel):
            metadata['parent_model'] = job.model_id
        return metadata

    @staticmethod
    def get_metrics_metadata(data_partner: str, data_partner_patients: List[str], job: JobTraining or JobEvaluatingFromPretrainedModel) -> dict:
        metadata = {
            'data_partner': data_partner,
            'data_partner_patients': data_partner_patients
        }
        if isinstance(job, JobEvaluatingFromPretrainedModel):
            metadata['model'] = job.model_id
        return metadata

    @staticmethod
    def get_inference_results_metadata(job: JobInferencingFromPretrainedModel) -> dict:
        return {
            'execution_id': job.id
        }
