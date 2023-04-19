import json
import logging

import argo_workflows
from argo_workflows.api import workflow_service_api
from argo_workflows.model.io_argoproj_workflow_v1alpha1_parameter import IoArgoprojWorkflowV1alpha1Parameter
from argo_workflows.model.io_argoproj_workflow_v1alpha1_workflow_create_request import \
    IoArgoprojWorkflowV1alpha1WorkflowCreateRequest
from django.conf import settings

from main.communication_adapter.communication_adapter_interface import CommunicationAdapterInterface
from main.container_manager.container_manager_interface import ContainerManagerInterface
from main.exceptions import InternalError
from main.models import Execution
from main.models.utils import get_class_name_low_case
from main.utils import load_yaml_file
from .models import ExecutionWorkflow

logger = logging.getLogger(__name__)


def keys_exists(element, *keys):
    if not isinstance(element, dict):
        raise AttributeError('keys_exists() expects dict as first argument.')
    if len(keys) == 0:
        raise AttributeError('keys_exists() expects at least two arguments, one given.')

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True


class ContainerManagerArgoWorkflows(ContainerManagerInterface):

    def __init__(self):
        super().__init__()

    # ---> Main methods

    @staticmethod
    def start_schema_execution(execution: Execution, communication_adapter: CommunicationAdapterInterface.__class__) -> None:
        logger.debug('start_schema_execution method called')
        api_response = None
        try:
            # load params for schema
            manifest = load_yaml_file(execution.schema.auxiliary_file.path)
            parameters = ContainerManagerArgoWorkflows._get_parameters(execution)

            # perform additional actions in case of federated
            if execution.schema.requires_input_elements_federated_learning_configuration():
                parameters['execution_communicationAdapterId'] = communication_adapter.prepare_execution(execution)

            # insert params into schema
            final_parameters = []
            for key, value in parameters.items():
                if isinstance(value, dict) or isinstance(value, list):
                    value = json.dumps(value)
                final_parameters.append(IoArgoprojWorkflowV1alpha1Parameter(key, value=str(value)))
            if keys_exists(manifest, 'spec', 'arguments', 'parameters'):
                final_parameters.append(manifest['spec']['arguments']['parameters'])
                manifest['spec']['arguments']['parameters'] = final_parameters
            elif keys_exists(manifest, 'spec', 'arguments'):
                manifest['spec']['arguments']['parameters'] = final_parameters
            else:
                manifest['spec']['arguments'] = {
                    'parameters': final_parameters
                }

            # send schema to argoWorkflows
            configuration = argo_workflows.Configuration(host=settings.ARGO_WORKFLOWS_API_HOST)
            configuration.verify_ssl = False
            api_client = argo_workflows.ApiClient(configuration)
            api_instance = workflow_service_api.WorkflowServiceApi(api_client)
            api_response = api_instance.create_workflow(
                namespace=settings.ARGO_WORKFLOWS_NAMESPACE,
                body=IoArgoprojWorkflowV1alpha1WorkflowCreateRequest(workflow=dict(manifest), _check_type=False),
                _check_return_type=False
            )
            logger.debug(api_response)
            workflow_name = api_response['metadata']['name']
            ExecutionWorkflow.objects.create(workflow_name=workflow_name, execution=execution)
            # TODO delete workflow in argo if object creation fails, take into account that workflow_name wont be available on the db object
        except InternalError as e:
            raise e
        except Exception as e:
            if api_response:
                logger.error(api_response)
            raise InternalError(f'Error while doing request to Argo Workflows to create workflow', e)

    @staticmethod
    def end_schema_execution(execution: Execution, communication_adapter: CommunicationAdapterInterface.__class__) -> None:
        logger.debug('end_schema_execution method called')
        api_response = None
        try:
            configuration = argo_workflows.Configuration(host=settings.ARGO_WORKFLOWS_API_HOST)
            configuration.verify_ssl = False
            api_client = argo_workflows.ApiClient(configuration)
            api_instance = workflow_service_api.WorkflowServiceApi(api_client)
            api_response = api_instance.delete_workflow(
                namespace=settings.ARGO_WORKFLOWS_NAMESPACE,
                name=eval(f'execution.{get_class_name_low_case(ExecutionWorkflow)}').workflow_name,
                _check_return_type=False
            )
            logger.debug(api_response)
        except argo_workflows.exceptions.NotFoundException:
            logger.warning(f'Workflow of execution {execution.id} does not exist')
        except Exception as e:
            if api_response:
                logger.error(api_response)
            raise InternalError(f'Error while doing request to Argo Workflows to delete workflow', e)

    # ---> Auxiliary methods

    @staticmethod
    def _get_parameters(execution: Execution):
        parameters = {
            'platform_maasApiHostname': settings.MAAS_API_HOSTNAME,
            'platform_orchestratorApiHostname': settings.ORCHESTRATOR_API_HOSTNAME,
            'platform_processorResourceManagerVersion': settings.PROCESSOR_RESOURCE_MANAGER_VERSION,
            'platform_processorResourceManagerCallbackUrl': settings.PROCESSOR_RESOURCE_MANAGER_CALLBACK_URL,
            'platform_processorResourceManagerApiHost': settings.PROCESSOR_RESOURCE_MANAGER_API_HOST,
            'platform_federatedLearningManagerVersion': settings.FEDERATED_LEARNING_MANAGER_VERSION,
            'aiEngine_plaformVarsInputElements': settings.AI_ENGINE_PLATFORM_VARS_INPUT_ELEMENTS,
            'aiEngine_plaformVarsInputDataTraining': settings.AI_ENGINE_PLATFORM_VARS_INPUT_DATA_TRAINING,
            'aiEngine_plaformVarsInputDataEvaluation': settings.AI_ENGINE_PLATFORM_VARS_INPUT_DATA_EVALUATION,
            'aiEngine_plaformVarsInputDataInference': settings.AI_ENGINE_PLATFORM_VARS_INPUT_DATA_INFERENCE,
            'aiEngine_plaformVarsInputAIElements': settings.AI_ENGINE_PLATFORM_VARS_INPUT_AI_ELEMENTS,
            'aiEngine_plaformVarsInputUserVars': settings.AI_ENGINE_PLATFORM_VARS_INPUT_USER_VARS,
            'aiEngine_plaformVarsInputModel': settings.AI_ENGINE_PLATFORM_VARS_INPUT_MODEL,
            'aiEngine_plaformVarsInputModels': settings.AI_ENGINE_PLATFORM_VARS_INPUT_MODELS,
            'aiEngine_plaformVarsOutputElements': settings.AI_ENGINE_PLATFORM_VARS_OUTPUT_ELEMENTS,
            'aiEngine_plaformVarsOutputModel': settings.AI_ENGINE_PLATFORM_VARS_OUTPUT_MODEL,
            'aiEngine_plaformVarsOutputEvaluationMetrics': settings.AI_ENGINE_PLATFORM_VARS_OUTPUT_EVALUATION_METRICS,
            'aiEngine_plaformVarsOutputInferenceResults': settings.AI_ENGINE_PLATFORM_VARS_OUTPUT_INFERENCE_RESULTS,
            'aiEngine_plaformVarsApiPingUrl': settings.AI_ENGINE_PLATFORM_VARS_API_PING_URL,
            'aiEngine_plaformVarsApiRunUrl': settings.AI_ENGINE_PLATFORM_VARS_API_RUN_URL,
            'aiEngine_plaformVarsApiHost': settings.AI_ENGINE_PLATFORM_VARS_API_HOST,
            'execution_id': execution.id
        }

        if execution.schema.requires_input_elements_platform_data():
            parsed_data_partners_patients = execution.get_input_elements_platform_data().parsed_data_partners_patients
            parameters['execution_dataPartner'] = list(parsed_data_partners_patients.keys())[0]
            parameters['execution_dataPartnerPatients'] = parsed_data_partners_patients
            parameters['execution_dataPartnerPatientsList'] = [{'data_partner': data_partner} for data_partner in list(parsed_data_partners_patients.keys())]

        if execution.schema.requires_input_elements_federated_learning_configuration():
            parameters['execution_federatedConfigNumberIterations'] = execution.get_input_elements_federated_learning_configuration().number_iterations
            parameters['execution_federatedConfigNumberDataPartners'] = len(execution.get_input_elements_platform_data().parsed_data_partners_patients)

        ai_engines = execution.get_ai_elements_ai_engines()
        for ai_engine in ai_engines:
            parameters[f'execution_{ai_engine.descriptor}-version'] = ai_engine.version
            parameters[f'execution_{ai_engine.descriptor}-container-name'] = ai_engine.container_name
            parameters[f'execution_{ai_engine.descriptor}-container-version'] = ai_engine.container_version
            if ai_engine.requires_ai_model():
                parameters[f'execution_{ai_engine.descriptor}-ai-model'] = ai_engine.get_ai_model().ai_model

        if execution.schema.produces_output_elements_ai_model():
            parameters['execution_outputAIModelName'] = execution.get_output_elements_ai_model().name
            parameters['execution_outputAIModelDescription'] = execution.get_output_elements_ai_model().description
            merge_type = execution.get_output_elements_ai_model().merge_type
            if merge_type:
                parameters['execution_outputAIModelMergeType'] = merge_type
            else:
                parameters['execution_outputAIModelMergeType'] = "default"

        return parameters
