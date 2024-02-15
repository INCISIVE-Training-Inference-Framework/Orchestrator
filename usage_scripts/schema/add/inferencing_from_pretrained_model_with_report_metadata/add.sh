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
name="inferencing_from_pretrained_model_with_report_metadata" # str
type="individual" # str, possible values -> {individual, joint}, individual for one AI Engine executions, joint for pipelines
implementation="argo_workflows" # str, possible values -> {argo_workflows}
description="A schema that performs inference with an AI Engine to some external data, creating a set of results and charts"
auxiliary_file="./auxiliary_files/schema_inferencing_from_pretrained_model_with_report_metadata/schema.yaml" # FILE, optional (it is mandatory for the argo_workflows implementation)

# input attributes

input_platform_data="false" # bool
input_external_data="true" # bool, can only be true if input_platform_data and input_federated_learning_configuration are false
input_federated_learning_configuration="false" # bool
input_report_metadata="true" # bool, optional

# AI logic attributes

input_ai_engine_descriptor="main-ai-engine" # str, cannot contain spaces or special symbols (neither _)
input_ai_engine_role_type="*" # str, possible values -> the ones defined on the MaaS along the symbol *
input_ai_engine_functionalities='["inferencing_from_pretrained_model"]' # list[str], possible values -> the ones defined on the MaaS
input_ai_engine_model="true" # bool

# output attributes

output_ai_model="false" # bool
output_evaluation_metrics="false" # bool
output_generic_file="true" # bool

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
                                    \"report_metadata\": ${input_report_metadata},
                                    \"federated_learning_configuration\": ${input_federated_learning_configuration}
                                },
                                \"ai_elements\": {
                                    \"ai_engines\": [
                                        {
                                            \"descriptor\": \"${input_ai_engine_descriptor}\",
                                            \"role_type\": \"${input_ai_engine_role_type}\",
                                            \"functionalities\": ${input_ai_engine_functionalities},
                                            \"ai_model\": ${input_ai_engine_model}
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