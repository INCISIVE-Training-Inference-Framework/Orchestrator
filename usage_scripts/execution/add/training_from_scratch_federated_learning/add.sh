#!/bin/bash

# --> DESCRIPTION
# It is a script that creates an Execution from the "traning_from_scratch_federated_learning" Schema of the Orchestrator

# --> PREREQUISITES
# - curl installed

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES

# main attributes
schema="training_from_scratch_federated_learning" # str

# input attributes

input_platform_data="{\"data-partner-1\": [\"1\", \"2\"], \"data-partner-2\": [\"1\"]}" # dict[str:list[str]], the partners must exist on the platform
input_federated_learning_configuration='{"number_iterations": 2}'

# AI logic attributes

input_ai_engine_version=1 # int, must exist on the MaaS
input_ai_engine_version_user_vars="./auxiliary_files/user_vars.json" # FILE

# output attributes

output_ai_model_name="init_plt_data" # str
output_ai_model_description="initial model trained on platform data" # str
output_ai_model_merge_type="default" # str, optional

# --> CODE
curl -X POST http://${orchestrator_api_hostname}/api/executions/ \
                            -H "Content-Type:multipart/form-data" \
                            -F data="{
                                \"schema\": \"${schema}\",
                                \"input_elements\": {
                                    \"platform_data\": {
                                        \"data_partners_patients\": ${input_platform_data}
                                    },
                                    \"federated_learning_configuration\": ${input_federated_learning_configuration}
                                },
                                \"ai_elements\": {
                                    \"ai_engines\": [
                                        {
                                            \"descriptor\": \"main_ai_engine\",
                                            \"version\": ${input_ai_engine_version}
                                        }
                                    ]
                                },
                                \"output_elements\": {
                                    \"ai_model\": {
                                        \"name\": \"${output_ai_model_name}\",
                                        \"description\": \"${output_ai_model_description}\",
                                        \"merge_type\": \"${output_ai_model_merge_type}\"
                                    }
                                }
                            }" \
                            -F main_ai_engine_version_user_vars=@${input_ai_engine_version_user_vars}

# --> SUCCESSFUL OUTPUT
# code: 201
# content: check successful_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors