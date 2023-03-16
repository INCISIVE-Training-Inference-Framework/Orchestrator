#!/bin/bash

# --> DESCRIPTION
# It is a script that creates an Execution from the "d_4_2_breast_cancer" Schema of the Orchestrator

# --> PREREQUISITES
# - curl installed

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES

# main attributes
schema="d_4_2_breast_cancer" # str

# input attributes

input_external_data="./auxiliary_files/external_data.zip" # FILE

# AI logic attributes

_1_input_ai_engine_version=1 # int, must exist on the MaaS
_1_input_ai_engine_version_user_vars="./auxiliary_files/user_vars.json" # FILE
_1_input_ai_model=1 # int, must exist on the MaaS

_2_input_ai_engine_version=2 # int, must exist on the MaaS
_2_input_ai_engine_version_user_vars="./auxiliary_files/user_vars.json" # FILE
_2_input_ai_model=2 # int, must exist on the MaaS

_3_input_ai_engine_version=4 # int, must exist on the MaaS
_3_input_ai_engine_version_user_vars="./auxiliary_files/user_vars.json" # FILE

# output attributes

# --> CODE
curl -X POST http://${orchestrator_api_hostname}/api/executions/ \
                            -H "Content-Type:multipart/form-data" \
                            -F data="{
                                \"schema\": \"${schema}\",
                                \"input_elements\": {},
                                \"ai_elements\": {
                                    \"ai_engines\": [
                                        {
                                            \"descriptor\": \"prioritization-and-segmentation\",
                                            \"version\": ${_1_input_ai_engine_version},
                                            \"ai_model\": ${_1_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": \"birads-classification\",
                                            \"version\": ${_2_input_ai_engine_version},
                                            \"ai_model\": ${_2_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": \"medical-report-generation\",
                                            \"version\": ${_3_input_ai_engine_version}
                                        }
                                    ]
                                },
                                \"output_elements\": {}
                            }" \
                            -F external_data=@${input_external_data} \
                            -F prioritization-and-segmentation_version_user_vars=@${_1_input_ai_engine_version_user_vars} \
                            -F birads-classification_version_user_vars=@${_2_input_ai_engine_version_user_vars} \
                            -F medical-report-generation_version_user_vars=@${_3_input_ai_engine_version_user_vars}

# --> SUCCESSFUL OUTPUT
# code: 201
# content: check successful_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
