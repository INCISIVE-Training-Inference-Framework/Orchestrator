import json
from typing import List

import kubernetes.client as k8s
from django.conf import settings

from main.container_manager.types.kubernetes.utils import get_job_name, get_use_case_initializer_config
from main.models import \
    Job


def get_container_parallel_manager_config(
        job_name: str,
        number_iterations: int,
        number_pods: int,
        model_metadata: dict,
        job: Job
) -> k8s.V1Container:
    return k8s.V1Container(
        name='communicator',
        image=f'{settings.COMPONENT_IMAGES_REGISTRY}/pl-manager:{settings.KUBERNETES_PL_MANAGER_IMAGE_VERSION}',
        args=[
            str(job.id),
            job.complete_id,
            job_name,  # it is specific of the manager
            str(number_iterations),
            str(number_pods),
            json.dumps(model_metadata)
        ],
        env_from=[
            k8s.V1EnvFromSource(
                config_map_ref=k8s.V1ConfigMapEnvSource(name='pl-manager-config')
            )
        ],
        volume_mounts=[
            k8s.V1VolumeMount(
                name='input',
                mount_path='/usr/application/input'
            ),
            k8s.V1VolumeMount(
                name='output',
                mount_path='/usr/application/output'
            ),
            k8s.V1VolumeMount(
                name='service-account',
                mount_path='/var/run/secrets/kubernetes.io/serviceaccount',
                read_only=True
            )
        ]
    )


def get_parallel_container_client_config(
        job_name: str,
        data_partner: str,
        number_iterations: int,
        job: Job
) -> k8s.V1Container:
    return k8s.V1Container(
        name='communicator',
        image=f'{settings.COMPONENT_IMAGES_REGISTRY}/pl-client:{settings.KUBERNETES_PL_CLIENT_IMAGE_VERSION}',
        args=[
            str(job.id),
            job.complete_id,
            job_name,
            data_partner,
            str(number_iterations),
            job.use_case
        ],
        env_from=[
            k8s.V1EnvFromSource(
                config_map_ref=k8s.V1ConfigMapEnvSource(name='pl-client-config')
            )
        ],
        volume_mounts=[
            k8s.V1VolumeMount(
                name='input',
                mount_path='/usr/application/input'
            ),
            k8s.V1VolumeMount(
                name='output',
                mount_path='/usr/application/output'
            ),
            k8s.V1VolumeMount(
                name='service-account',
                mount_path='/var/run/secrets/kubernetes.io/serviceaccount',
                read_only=True
            )
        ]
    )


def get_parallel_container_ai_engine_config(
        ai_engine_container_name: str,
        ai_engine_container_version: str,
        manager: bool,
        job: Job
) -> k8s.V1Container:
    ai_engine_config = k8s.V1Container(
        name='ai-engine',
        image=f'{settings.AI_ENGINE_IMAGES_REGISTRY}/{ai_engine_container_name}:{ai_engine_container_version}',
        command=[
            '/bin/sh',
            '-c'
        ],
        args=['trap "exit 0" TERM INT; sleep infinity & wait'],
        volume_mounts=[
            k8s.V1VolumeMount(
                name='input',
                mount_path='/usr/application/input'
            ),
            k8s.V1VolumeMount(
                name='output',
                mount_path='/usr/application/output'
            )
        ]
    )
    if job.data_path and not manager:
        ai_engine_config.security_context = k8s.V1SecurityContext(privileged=True)
        ai_engine_config.volume_mounts += [k8s.V1VolumeMount(
            name='data',
            mount_path='/usr/application/input/data'
        )]
    return ai_engine_config


def get_parallel_training_manager_config(
        ai_engine_container_name: str,
        ai_engine_container_version: str,
        model_metadata: dict,
        job: Job
) -> k8s.V1Job:
    job_name = f'{get_job_name(job, None)}-manager'
    return k8s.V1Job(
        metadata=k8s.V1ObjectMeta(
            name=job_name,
            labels={
                'id': str(job.id)
            }
        ),
        spec=k8s.V1JobSpec(
            backoff_limit=0,  # they are not ready yet for restart
            ttl_seconds_after_finished=settings.KUBERNETES_JOBS_AUTO_DELETE_SECONDS,  # auto delete
            template=k8s.V1PodTemplateSpec(
                spec=k8s.V1PodSpec(
                    restart_policy='Never',
                    node_selector={
                        settings.KUBERNETES_CENTRAL_NODE_LABEL_KEY:
                            settings.KUBERNETES_CENTRAL_NODE_LABEL_VALUE
                    },
                    init_containers=[get_use_case_initializer_config(job)],
                    containers=[
                        get_container_parallel_manager_config(
                            job_name,
                            job.number_iterations,
                            len(job.parsed_data_partners_patients),
                            model_metadata,
                            job
                        ),
                        get_parallel_container_ai_engine_config(
                            ai_engine_container_name,
                            ai_engine_container_version,
                            True,
                            job
                        )
                    ],
                    volumes=[
                        k8s.V1Volume(
                            name='input',
                            empty_dir=k8s.V1EmptyDirVolumeSource()
                        ),
                        k8s.V1Volume(
                            name='output',
                            empty_dir=k8s.V1EmptyDirVolumeSource()
                        ),
                        k8s.V1Volume(
                            name='service-account',
                            secret=k8s.V1SecretVolumeSource(
                                secret_name=settings.KUBERNETES_PL_TRAINING_SERVICE_ACCOUNT_TOKEN
                            )
                        )
                    ]
                )
            )
        )
    )


def get_parallel_training_client_config(
        ai_engine_container_name: str,
        ai_engine_container_version: str,
        data_partner: str,
        data_partner_patients: List[str],
        job: Job
) -> k8s.V1Job:
    volumes = [
        k8s.V1Volume(
            name='input',
            empty_dir=k8s.V1EmptyDirVolumeSource()
        ),
        k8s.V1Volume(
            name='output',
            empty_dir=k8s.V1EmptyDirVolumeSource()
        ),
        k8s.V1Volume(
            name='service-account',
            secret=k8s.V1SecretVolumeSource(
                secret_name=settings.KUBERNETES_PL_TRAINING_SERVICE_ACCOUNT_TOKEN
            )
        )
    ]
    if job.data_path:
        volumes += [k8s.V1Volume(
            name='data',
            host_path=k8s.V1HostPathVolumeSource(path=job.data_path)
        )]
    job_name = f'{get_job_name(job, data_partner)}-client'
    job_config = k8s.V1Job(
        metadata=k8s.V1ObjectMeta(
            name=job_name,
            labels={
                'id': str(job.id),
            }
        ),
        spec=k8s.V1JobSpec(
            backoff_limit=0,  # they are not ready yet for restart
            ttl_seconds_after_finished=settings.KUBERNETES_JOBS_AUTO_DELETE_SECONDS,  # auto delete
            template=k8s.V1PodTemplateSpec(
                spec=k8s.V1PodSpec(
                    restart_policy='Never',
                    node_selector={'dataPartner': data_partner},
                    init_containers=[get_use_case_initializer_config(job, data_partner_patients)],
                    containers=[
                        get_parallel_container_client_config(
                            job_name,
                            data_partner,
                            job.number_iterations,
                            job
                        ),
                        get_parallel_container_ai_engine_config(
                            ai_engine_container_name,
                            ai_engine_container_version,
                            False,
                            job
                        )
                    ],
                    volumes=volumes
                )
            )
        )
    )
    return job_config
