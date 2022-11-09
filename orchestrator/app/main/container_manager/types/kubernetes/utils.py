import json
from typing import List, Optional

import kubernetes.client as k8s
from django.conf import settings

from main.models import \
    Job, \
    JobTraining, \
    JobWithPretrainedModel, \
    JobEvaluatingFromPretrainedModel, \
    JobInferencingFromPretrainedModel


def get_job_name(job: Job, data_partner: Optional[str]) -> str:
    if data_partner:
        return f'job-{job.complete_id}-{data_partner}-{"pl" if job.is_parallel else "sq"}'
    else:
        return f'job-{job.complete_id}-{"pl" if job.is_parallel else "sq"}'


def get_use_case_initializer_config(job: Job, data_partner_patients: Optional[List[str]] = None) -> k8s.V1Container:
    volume_mounts = [
        k8s.V1VolumeMount(
            name='input',
            mount_path='/usr/application/input'
        )
    ]
    actions = {
        'actions': []
    }
    actions['actions'].append(  # done in two phases for removing strange warning in ide
        {
            'name': 'download_config',
            'job_id': job.id
        }
    )
    if isinstance(job, JobInferencingFromPretrainedModel):
        actions['actions'].append(
            {
                'name': 'download_data',
                'method': {
                    'name': 'inference_input_data',
                    'job_id': job.id
                }
            }
        )
        actions['actions'].append(
            {
                'name': 'create_output_inference_results_directory'
            }
        )
        volume_mounts.append(
            k8s.V1VolumeMount(
                name='output',
                mount_path='/usr/application/output'
            )
        )
    elif settings.USE_INCISIVE_DP and data_partner_patients:
        actions['actions'].append(
            {
                'name': 'download_data',
                'method': {
                    'name': 'input_data',
                    'job_id': job.id,
                    'data_partner_patients': data_partner_patients
                }
            }
        )
    if isinstance(job, JobWithPretrainedModel):
        actions['actions'].append(
            {
                'name': 'download_model',
                'model_id': job.model_id
            }
        )
    if isinstance(job, JobTraining):
        actions['actions'].append(
            {
                'name': 'create_output_model_directory'
            }
        )
        volume_mounts.append(
            k8s.V1VolumeMount(
                name='output',
                mount_path='/usr/application/output'
            )
        )
    return k8s.V1Container(
        name='use-case-initializer',
        image=f''
              f'{settings.COMPONENT_IMAGES_REGISTRY}/use-case-initializer:'
              f'{settings.KUBERNETES_USE_CASE_INITIALIZER_IMAGE_VERSION}',
        args=[json.dumps(actions)],
        env_from=[
            k8s.V1EnvFromSource(
                config_map_ref=k8s.V1ConfigMapEnvSource(name='use-case-initializer-config')
            )
        ],
        volume_mounts=volume_mounts
    )


def get_use_case_finalizer_config(
        platform_adapter,
        ai_engine_id: Optional[int],
        data_partner: Optional[str],
        data_partner_patients: Optional[List[str]],
        job: Job
) -> k8s.V1Container:
    actions = {
        'actions': []
    }
    if isinstance(job, JobTraining):
        actions['actions'].append(
            {
                'name': 'upload_model',
                'metadata': platform_adapter.get_model_metadata(ai_engine_id, job)
            }
        )
    if isinstance(job, JobTraining) or isinstance(job, JobEvaluatingFromPretrainedModel):
        actions['actions'].append(
            {
                'name': 'upload_metrics',
                'metadata': platform_adapter.get_metrics_metadata(data_partner, data_partner_patients, job)
            }
        )
    if isinstance(job, JobInferencingFromPretrainedModel):
        actions['actions'].append(
            {
                'name': 'upload_inference_results',
                'metadata': platform_adapter.get_inference_results_metadata(job)
            }
        )

    return k8s.V1Container(
        name='use-case-finalizer',
        image=f''
              f'{settings.COMPONENT_IMAGES_REGISTRY}/use-case-finalizer:'
              f'{settings.KUBERNETES_USE_CASE_FINALIZER_IMAGE_VERSION}',
        args=[str(job.id), job.use_case, json.dumps(actions)],
        env_from=[
            k8s.V1EnvFromSource(
                config_map_ref=k8s.V1ConfigMapEnvSource(name='use-case-finalizer-config')
            )
        ],
        volume_mounts=[
            k8s.V1VolumeMount(
                name='output',
                mount_path='/usr/application/output'
            )
        ]
    )