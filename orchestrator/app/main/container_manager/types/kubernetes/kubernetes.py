import logging

import kubernetes.client as k8s
from django.conf import settings
from kubernetes import config
from kubernetes.client.rest import ApiException

from main.communication_adapter.types.kafka import CommunicationAdapterKafka
from main.container_manager.container_manager_interface import ContainerManagerInterface
from main.container_manager.types.kubernetes.parallel_configs import \
    get_parallel_training_manager_config, \
    get_parallel_training_client_config
from main.container_manager.types.kubernetes.sequential_configs import get_sequential_config
from main.container_manager.types.kubernetes.utils import get_job_name
from main.domain.exceptions import InternalError
from main.models import \
    Job, \
    JobStatus, \
    JobTraining, \
    JobEvaluatingFromPretrainedModel, \
    JobInferencingFromPretrainedModel

logger = logging.getLogger(__name__)

if settings.CONTAINER_MANAGER == 'kubernetes':
    config.load_incluster_config()
    if settings.COMMUNICATION_ADAPTER == 'kafka':
        COMMUNICATION_ADAPTER = CommunicationAdapterKafka
    else:
        raise InternalError('Unknown communication adapter ' + settings.COMMUNICATION_ADAPTER, None)


class ContainerManagerKubernetes(ContainerManagerInterface):
    communication_initialized = False

    def __init__(self):
        super().__init__()

    # ---> Main methods

    @classmethod
    def start_job_execution(cls, platform_adapter, ai_engine_id: int, ai_engine_container_name: str, ai_engine_container_version: str, job: Job) -> None:
        if isinstance(job, JobTraining):
            cls.__training(platform_adapter, ai_engine_id, ai_engine_container_name, ai_engine_container_version, job)
        elif isinstance(job, JobEvaluatingFromPretrainedModel):
            cls.__evaluating_from_pretrained_model(platform_adapter, ai_engine_container_name, ai_engine_container_version, job)
        else:
            cls.__inferencing_from_pretrained_model(platform_adapter, ai_engine_container_name, ai_engine_container_version, job)

    @staticmethod
    def get_job_status(job: Job) -> JobStatus:
        # TODO implement cleaner
        try:
            if not job.is_parallel:
                data_partner = next(iter(job.parsed_data_partners_patients.keys()))
                with k8s.ApiClient() as api_client:
                    api_instance = k8s.BatchV1Api(api_client)
                    api_response = api_instance.read_namespaced_job_status(
                        get_job_name(job, data_partner),
                        settings.KUBERNETES_NAMESPACE,
                        pretty='true'
                    )
                    if api_response and hasattr(api_response, 'status'):
                        status = api_response.status
                        if hasattr(status, 'failed') and status.failed:
                            return JobStatus.FAILED
                        if hasattr(status, 'succeeded') and status.succeeded:
                            return JobStatus.SUCCEEDED
                        elif hasattr(status, 'active') and status.active:
                            return JobStatus.RUNNING
                        else:
                            return JobStatus.PENDING
            else:
                if isinstance(job, JobTraining):
                    with k8s.ApiClient() as api_client:
                        api_instance = k8s.BatchV1Api(api_client)
                        succeeded = 0
                        running = 0

                        # manager
                        api_response = api_instance.read_namespaced_job_status(
                            f'{get_job_name(job, None)}-manager',
                            settings.KUBERNETES_NAMESPACE,
                            pretty='true'
                        )
                        if api_response and hasattr(api_response, 'status'):
                            status = api_response.status
                            if hasattr(status, 'failed') and status.failed:
                                return JobStatus.FAILED
                            if hasattr(status, 'succeeded') and status.succeeded:
                                succeeded += 1
                            elif hasattr(status, 'active') and status.active:
                                running += 1

                        # clients
                        for data_partner, data_partner_patients in job.parsed_data_partners_patients.items():
                            api_response = api_instance.read_namespaced_job_status(
                                f'{get_job_name(job, data_partner)}-client',
                                settings.KUBERNETES_NAMESPACE,
                                pretty='true'
                            )
                            if api_response and hasattr(api_response, 'status'):
                                status = api_response.status
                                if hasattr(status, 'failed') and status.failed:
                                    return JobStatus.FAILED
                                if hasattr(status, 'succeeded') and status.succeeded:
                                    succeeded += 1
                                elif hasattr(status, 'active') and status.active:
                                    running += 1

                        if succeeded == len(job.parsed_data_partners_patients) + 1:
                            return JobStatus.SUCCEEDED
                        elif running == len(job.parsed_data_partners_patients) + 1:
                            return JobStatus.RUNNING
                        else:
                            return JobStatus.PENDING
                else:
                    with k8s.ApiClient() as api_client:
                        api_instance = k8s.BatchV1Api(api_client)
                        succeeded = 0
                        running = 0

                        for data_partner, data_partner_patients in job.parsed_data_partners_patients.items():
                            api_response = api_instance.read_namespaced_job_status(
                                get_job_name(job, data_partner),
                                settings.KUBERNETES_NAMESPACE,
                                pretty='true'
                            )
                            if api_response and hasattr(api_response, 'status'):
                                status = api_response.status
                                if hasattr(status, 'failed') and status.failed:
                                    return JobStatus.FAILED
                                if hasattr(status, 'succeeded') and status.succeeded:
                                    succeeded += 1
                                elif hasattr(status, 'active') and status.active:
                                    running += 1

                        if succeeded == len(job.parsed_data_partners_patients):
                            return JobStatus.SUCCEEDED
                        elif running == len(job.parsed_data_partners_patients):
                            return JobStatus.RUNNING
                        else:
                            return JobStatus.PENDING
        except ApiException as e:
            raise InternalError(
                f'Error while performing the call to the kubernetes API asking for the job {job.id}; status: {e.status}; reason: {e.reason}; {e}',
                None
            )

    @staticmethod
    def ended_job_execution(job: Job, finish_status: JobStatus.choices) -> None:
        if job.is_parallel and isinstance(job, JobTraining):
            COMMUNICATION_ADAPTER.finalize_execution(job.complete_id)

    # --> Auxiliary methods

    @classmethod
    def __training(cls, platform_adapter, ai_engine_id: int, ai_engine_container_name: str, ai_engine_container_version: str, job: JobTraining) -> None:
        try:
            if not job.is_parallel:
                data_partner, data_partner_patients = next(iter(job.parsed_data_partners_patients.items()))
                with k8s.ApiClient() as api_client:
                    api_instance = k8s.BatchV1Api(api_client)
                    api_instance.create_namespaced_job(
                        settings.KUBERNETES_NAMESPACE,
                        get_sequential_config(  # TODO refactor the amount of parameters
                            platform_adapter,
                            ai_engine_id,
                            data_partner,
                            data_partner_patients,
                            ai_engine_container_name,
                            ai_engine_container_version,
                            job
                        )
                    )
            else:
                # TODO call end execution when one of them fails
                with k8s.ApiClient() as api_client:
                    model_metadata = platform_adapter.get_model_metadata(ai_engine_id, job)
                    if not cls.communication_initialized:
                        COMMUNICATION_ADAPTER.initialize()
                        cls.communication_initialized = True
                    COMMUNICATION_ADAPTER.prepare_execution(job.complete_id)
                    api_instance = k8s.BatchV1Api(api_client)
                    api_instance.create_namespaced_job(
                        settings.KUBERNETES_NAMESPACE,
                        get_parallel_training_manager_config(
                            ai_engine_container_name,
                            ai_engine_container_version,
                            model_metadata,
                            job
                        )
                    )
                    for data_partner, data_partner_patients in job.parsed_data_partners_patients.items():
                        api_instance.create_namespaced_job(
                            settings.KUBERNETES_NAMESPACE,
                            get_parallel_training_client_config(
                                ai_engine_container_name,
                                ai_engine_container_version,
                                data_partner,
                                data_partner_patients,
                                job
                            )
                        )
        except ApiException as e1:
            try:
                if job.is_parallel and isinstance(job, JobTraining):
                    COMMUNICATION_ADAPTER.finalize_execution(job.complete_id)
            except InternalError as e2:
                logger.error(f'{e2}')
            finally:
                raise InternalError(
                    f'Error while performing the call to the kubernetes API doing the training from scratch use case: {e1}',
                    None
                )

    @staticmethod
    def __evaluating_from_pretrained_model(platform_adapter, ai_engine_container_name: str, ai_engine_container_version: str, job: JobEvaluatingFromPretrainedModel):
        try:
            # TODO call end execution when one of them fails
            with k8s.ApiClient() as api_client:
                api_instance = k8s.BatchV1Api(api_client)
                for data_partner, data_partner_patients in job.parsed_data_partners_patients.items():
                    api_instance.create_namespaced_job(
                        settings.KUBERNETES_NAMESPACE,
                        get_sequential_config(
                            platform_adapter,
                            None,
                            data_partner,
                            data_partner_patients,
                            ai_engine_container_name,
                            ai_engine_container_version,
                            job
                        )
                    )
        except ApiException as e:
            raise InternalError(f'Error while performing the call to the kubernetes API doing the evaluating from'
                                f' pretrained model use case: {e}', None)

    @staticmethod
    def __inferencing_from_pretrained_model(platform_adapter, ai_engine_container_name: str, ai_engine_container_version: str, job: JobInferencingFromPretrainedModel):
        try:
            # TODO call end execution when one of them fails
            with k8s.ApiClient() as api_client:
                api_instance = k8s.BatchV1Api(api_client)
                api_instance.create_namespaced_job(
                    settings.KUBERNETES_NAMESPACE,
                    get_sequential_config(
                        platform_adapter,
                        None,
                        None,
                        None,
                        ai_engine_container_name,
                        ai_engine_container_version,
                        job
                    )
                )
        except ApiException as e:
            raise InternalError(f'Error while performing the call to the kubernetes API doing the inferencing from'
                                f' pretrained model use case: {e}', None)
