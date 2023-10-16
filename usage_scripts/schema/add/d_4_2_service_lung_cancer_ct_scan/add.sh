#!/bin/bash

# --> DESCRIPTION
# It is a script that uploads a Schema to the Orchestrator

# --> PREREQUISITES
# - curl installed

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES

# main attributes
name="d_4_2_service_lung_cancer_ct_scan" # str
type="joint" # str, possible values -> {individual, joint}, individual for one AI Engine executions, joint for pipelines
implementation="argo_workflows" # str, possible values -> {argo_workflows}
description="A schema that performs the Lung cancer CT-Scan Service from D.4.2, creating a set of results and charts"
auxiliary_file="./auxiliary_files/schema_${name}/schema.yaml" # FILE, optional (it is mandatory for the argo_workflows implementation)

# input attributes

input_platform_data="false" # bool
input_external_data="true" # bool, can only be true if input_platform_data and input_federated_learning_configuration are false
input_federated_learning_configuration="false" # bool


# AI logic attributes

_1_input_ai_engine_descriptor="segmentation" # str, cannot contain spaces or special symbols
_1_input_ai_engine_role_type="segmentation" # str, possible values -> the ones defined on the MaaS along the symbol *
_1_input_ai_engine_functionalities='["inferencing_from_pretrained_model"]' # list[str], possible values -> the ones defined on the MaaS
_1_input_ai_engine_model="true" # bool

_2_input_ai_engine_descriptor="localization" # str, cannot contain spaces or special symbols
_2_input_ai_engine_role_type="localization" # str, possible values -> the ones defined on the MaaS along the symbol *
_2_input_ai_engine_functionalities='["inferencing_from_pretrained_model"]' # list[str], possible values -> the ones defined on the MaaS
_2_input_ai_engine_model="true" # bool

_3_input_ai_engine_descriptor="prioritization" # str, cannot contain spaces or special symbols
_3_input_ai_engine_role_type="prioritization" # str, possible values -> the ones defined on the MaaS along the symbol *
_3_input_ai_engine_functionalities='["inferencing_from_pretrained_model"]' # list[str], possible values -> the ones defined on the MaaS
_3_input_ai_engine_model="true" # bool

_4_input_ai_engine_descriptor="staging-classification-xai" # str, cannot contain spaces or special symbols
_4_input_ai_engine_role_type="xai" # str, possible values -> the ones defined on the MaaS along the symbol *
_4_input_ai_engine_functionalities='["inferencing_from_pretrained_model"]' # list[str], possible values -> the ones defined on the MaaS
_4_input_ai_engine_model="true" # bool

_5_input_ai_engine_descriptor="metastasis-risk-classification-xai" # str, cannot contain spaces or special symbols
_5_input_ai_engine_role_type="xai" # str, possible values -> the ones defined on the MaaS along the symbol *
_5_input_ai_engine_functionalities='["inferencing_from_pretrained_model"]' # list[str], possible values -> the ones defined on the MaaS
_5_input_ai_engine_model="true" # bool

_6_input_ai_engine_descriptor="medical-report-generation" # str, cannot contain spaces or special symbols
_6_input_ai_engine_role_type="report_generation" # str, possible values -> the ones defined on the MaaS along the symbol *
_6_input_ai_engine_functionalities='["inferencing_from_pretrained_model"]' # list[str], possible values -> the ones defined on the MaaS
_6_input_ai_engine_model="false" # bool

# output attributes

output_ai_model="false" # bool
output_evaluation_metrics="false" # bool
output_generic_file="true" # bool

# ========================== DO NOT MODIFY ABOVE CODE! ==================================
# --> CODE
curl -X POST http://${orchestrator_api_hostname}/api/schemas/ \
                            -H "Content-Type:multipart/form-data" \
                            -F data="{
                                \"name\": \"${name}\",
                                \"type\": \"${type}\",
                                \"implementation\": \"${implementation}\",
                                \"description\": \"${description}\",
                                \"input_elements\": {
                                    \"platform_data\": ${input_platform_data},
                                    \"external_data\": ${input_external_data},
                                    \"federated_learning_configuration\": ${input_federated_learning_configuration}
                                },
                                \"ai_elements\": {
                                    \"ai_engines\": [
                                        {
                                            \"descriptor\": \"${_1_input_ai_engine_descriptor}\",
                                            \"role_type\": \"${_1_input_ai_engine_role_type}\",
                                            \"functionalities\": ${_1_input_ai_engine_functionalities},
                                            \"ai_model\": ${_1_input_ai_engine_model}
                                        },
                                        {
                                            \"descriptor\": \"${_2_input_ai_engine_descriptor}\",
                                            \"role_type\": \"${_2_input_ai_engine_role_type}\",
                                            \"functionalities\": ${_2_input_ai_engine_functionalities},
                                            \"ai_model\": ${_2_input_ai_engine_model}
                                        },
                                        {
                                            \"descriptor\": \"${_3_input_ai_engine_descriptor}\",
                                            \"role_type\": \"${_3_input_ai_engine_role_type}\",
                                            \"functionalities\": ${_3_input_ai_engine_functionalities},
                                            \"ai_model\": ${_3_input_ai_engine_model}
                                        },
                                        {
                                            \"descriptor\": \"${_4_input_ai_engine_descriptor}\",
                                            \"role_type\": \"${_4_input_ai_engine_role_type}\",
                                            \"functionalities\": ${_4_input_ai_engine_functionalities},
                                            \"ai_model\": ${_4_input_ai_engine_model}
                                        },
                                        {
                                            \"descriptor\": \"${_5_input_ai_engine_descriptor}\",
                                            \"role_type\": \"${_5_input_ai_engine_role_type}\",
                                            \"functionalities\": ${_5_input_ai_engine_functionalities},
                                            \"ai_model\": ${_5_input_ai_engine_model}
                                        },
                                        {
                                            \"descriptor\": \"${_6_input_ai_engine_descriptor}\",
                                            \"role_type\": \"${_6_input_ai_engine_role_type}\",
                                            \"functionalities\": ${_6_input_ai_engine_functionalities},
                                            \"ai_model\": ${_6_input_ai_engine_model}
                                        }
                                    ]
                                },
                                \"output_elements\": {
                                    \"ai_model\": ${output_ai_model},
                                    \"evaluation_metrics\": ${output_evaluation_metrics},
                                    \"generic_file\": ${output_generic_file}
                                }
                            }" \
                            -F auxiliary_file=@${auxiliary_file}
# --> SUCCESSFUL OUTPUT
# code: 201
# content: check successful_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
