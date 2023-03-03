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

_3_input_ai_engine_version=3 # int, must exist on the MaaS
_3_input_ai_engine_version_user_vars="./auxiliary_files/user_vars.json" # FILE
_3_input_ai_model=3 # int, must exist on the MaaS

_4_input_ai_engine_version=4 # int, must exist on the MaaS
_4_input_ai_engine_version_user_vars="./auxiliary_files/user_vars.json" # FILE
_4_input_ai_model=4 # int, must exist on the MaaS

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
                                            \"descriptor\": \"prioritization_and_segmentation\",
                                            \"version\": ${_1_input_ai_engine_version},
                                            \"ai_model\": ${_1_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": \"birads_classification\",
                                            \"version\": ${_2_input_ai_engine_version},
                                            \"ai_model\": ${_2_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": \"density_classification\",
                                            \"version\": ${_3_input_ai_engine_version},
                                            \"ai_model\": ${_3_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": \"medical_report_generation\",
                                            \"version\": ${_4_input_ai_engine_version},
                                            \"ai_model\": ${_4_input_ai_model}
                                        }
                                    ]
                                },
                                \"output_elements\": {}
                            }" \
                            -F external_data=@${input_external_data} \
                            -F prioritization_and_segmentation_version_user_vars=@${_1_input_ai_engine_version_user_vars} \
                            -F birads_classification_version_user_vars=@${_2_input_ai_engine_version_user_vars} \
                            -F density_classification_version_user_vars=@${_3_input_ai_engine_version_user_vars} \
                            -F medical_report_generation_version_user_vars=@${_4_input_ai_engine_version_user_vars}

# --> SUCCESSFUL OUTPUT
# code: 201
# content: check successful_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
