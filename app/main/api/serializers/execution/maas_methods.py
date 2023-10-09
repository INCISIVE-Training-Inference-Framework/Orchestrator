import requests
from django.conf import settings
from rest_framework import serializers

from main.exceptions import InternalError


def get_maas_url(resource, resource_id):
    if resource == 'ai_engine_version':
        return f'http://{settings.MAAS_API_HOSTNAME}/api/ai_engines_versions/{resource_id}/'
    elif resource == 'ai_model':
        return f'http://{settings.MAAS_API_HOSTNAME}/api/ai_models/{resource_id}/'
    elif resource == 'evaluation_metric':
        return f'http://{settings.MAAS_API_HOSTNAME}/api/evaluation_metrics/{resource_id}/'
    elif resource == 'generic_file':
        return f'http://{settings.MAAS_API_HOSTNAME}/api/generic_files/{resource_id}/'
    else:
        raise NotImplementedError()


def retrieve_container_information(ai_engine_version_id):
    try:
        # retrieve AI Engine Version
        headers = {'Accept': 'application/json'}
        r = requests.get(get_maas_url('ai_engine_version', ai_engine_version_id), headers=headers)

        if r.status_code == 500:
            message = 'Internal error while retrieving AI Engine Version from MaaS'
            raise InternalError(f'{message}. Status code {r.status_code}', None)
        elif r.status_code != 200:
            try:
                message = r.json()
            except:
                message = ''
            raise serializers.ValidationError(f'Error while retrieving AI Engine Version from MaaS. Status code {r.status_code}. {message}')
        response = r.json()
        container_version = response['container_version']
        max_iteration_time = response['max_iteration_time']
        memory_request = response['memory_request']
        cpu_request = response['cpu_request']
        memory_limit = response['memory_limit']
        cpu_limit = response['cpu_limit']
    except Exception as e:
        if not isinstance(e, serializers.ValidationError):
            raise InternalError(f'Error while retrieving AI Engine Version from MaaS. {e}', e)
        else:
            raise e

    try:
        # retrieve AI Engine
        ai_engine_url = response['ai_engine']
        headers = {'Accept': 'application/json'}
        r = requests.get(ai_engine_url, headers=headers)
        if r.status_code == 500:
            message = 'Internal error while retrieving AI Engine from MaaS'
            raise InternalError(f'{message}. Status code {r.status_code}', None)
        elif r.status_code != 200:
            try:
                message = r.json()
            except:
                message = ''
            raise serializers.ValidationError(f'Error while retrieving AI Engine from MaaS. Status code {r.status_code}. {message}')
        container_name = r.json()['container_name']
    except Exception as e:
        if not isinstance(e, serializers.ValidationError):
            raise InternalError(f'Error while retrieving AI Engine from MaaS. {e}', e)
        else:
            raise e

    return container_name, container_version, max_iteration_time, memory_request, cpu_request, memory_limit, cpu_limit


def retrieve_ai_model_information(ai_model_id: int) -> int:
    """

    """
    try:
        # Retrieve AI Model
        headers = {'Accept': 'application/json'}
        r = requests.get(get_maas_url('ai_model', ai_model_id), headers=headers)

        # Evaluate response status code
        if r.status_code == 500:
            message = 'Internal error while retrieving AI Model from MaaS'
            raise InternalError(f'{message}. Status code {r.status_code}', None)
        elif r.status_code != 200:
            try:
                message = r.json()
            except:
                message = ''
            raise serializers.ValidationError(
                f'Error while retrieving AI Model from MaaS. Status code {r.status_code}. {message}')

        # Get the desired values from the AI Model response
        response = r.json()
        download_resume_retries = response['download_resume_retries']

    except Exception as e:
        if not isinstance(e, serializers.ValidationError):
            raise InternalError(f'Error while retrieving AI Model from MaaS. {e}', e)
        else:
            raise e

    return download_resume_retries
