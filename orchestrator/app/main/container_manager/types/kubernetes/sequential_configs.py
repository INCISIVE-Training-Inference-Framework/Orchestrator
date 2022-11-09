from typing import List, Optional

import kubernetes.client as k8s
from django.conf import settings

from main.container_manager.types.kubernetes.utils import \
    get_job_name, \
    get_use_case_initializer_config, \
    get_use_case_finalizer_config
from main.models import \
    Job


def get_sequential_container_ai_engine_config(ai_engine_container_name: str, ai_engine_container_version: str,
                                              job: Job) -> k8s.V1Container:
    ai_engine_config = k8s.V1Container(
        name='ai-engine',
        image=f''
              f'{settings.AI_ENGINE_IMAGES_REGISTRY}/{ai_engine_container_name}:'
              f'{ai_engine_container_version}',
        command=[
            'bash',
            f'/usr/application/{job.use_case}.sh'
        ],
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
    if job.data_path:
        ai_engine_config.security_context = k8s.V1SecurityContext(privileged=True)
        ai_engine_config.volume_mounts += [k8s.V1VolumeMount(
            name='data',
            mount_path='/usr/application/input/data'
        )]
    return ai_engine_config


def get_sequential_config(
        platform_adapter,
        ai_engine_id: Optional[int],  # TODO refactor the amount of Optionals (not good code)
        data_partner: Optional[str],
        data_partner_patients: Optional[List[str]],
        ai_engine_container_name: str,
        ai_engine_container_version: str,
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
        )
    ]
    if job.data_path:
        volumes += [k8s.V1Volume(
            name='data',
            host_path=k8s.V1HostPathVolumeSource(path=job.data_path)
        )]

    if data_partner:
        node_selector = {'dataPartner': data_partner}
    else:
        # inference
        node_selector = {settings.KUBERNETES_CENTRAL_NODE_LABEL_KEY: settings.KUBERNETES_CENTRAL_NODE_LABEL_VALUE}

    job_config = k8s.V1Job(
        metadata=k8s.V1ObjectMeta(
            name=get_job_name(job, data_partner),
            labels={
                'id': str(job.id)
            }
        ),
        spec=k8s.V1JobSpec(
            backoff_limit=settings.KUBERNETES_JOBS_BACK_OFF_LIMIT,
            ttl_seconds_after_finished=settings.KUBERNETES_JOBS_AUTO_DELETE_SECONDS,  # auto delete
            template=k8s.V1PodTemplateSpec(
                spec=k8s.V1PodSpec(
                    restart_policy='Never',
                    node_selector=node_selector,
                    init_containers=[
                        get_use_case_initializer_config(job, data_partner_patients),
                        get_sequential_container_ai_engine_config(ai_engine_container_name, ai_engine_container_version,
                                                                  job)
                    ],
                    containers=[get_use_case_finalizer_config(platform_adapter, ai_engine_id, data_partner,
                                                              data_partner_patients, job)],
                    volumes=volumes
                )
            )
        )
    )
    return job_config
