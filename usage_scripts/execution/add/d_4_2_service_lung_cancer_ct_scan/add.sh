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
schema="d_4_2_service_lung_cancer_ct_scan" # str

# input attributes

input_external_data="./auxiliary_files/${schema}/${schema}_input.zip" # FILE

# AI logic attributes
# CT-Scan segmentation
_1_input_descriptor="segmentation"
_1_input_ai_engine_version=6 # int, must exist on the MaaS
_1_input_ai_engine_version_user_vars="./auxiliary_files/${schema}/${_1_input_descriptor}_user_vars.json" # FILE
_1_input_ai_model=4 # int, must exist on the MaaS

# CT-Scan localization
_2_input_descriptor="localization"
_2_input_ai_engine_version=6 # int, must exist on the MaaS
_2_input_ai_engine_version_user_vars="./auxiliary_files/${schema}/${_2_input_descriptor}_user_vars.json" # FILE
_2_input_ai_model=4 # int, must exist on the MaaS

# CT-Scan prioritization
_3_input_descriptor="prioritization"
_3_input_ai_engine_version=6 # int, must exist on the MaaS
_3_input_ai_engine_version_user_vars="./auxiliary_files/${schema}/${_3_input_descriptor}_user_vars.json" # FILE
_3_input_ai_model=4 # int, must exist on the MaaS

# Staging classification XAI
_4_input_descriptor="staging-classification-xai"
_4_input_ai_engine_version=10 # int, must exist on the MaaS
_4_input_ai_engine_version_user_vars="./auxiliary_files/${schema}/${_4_input_descriptor}_user_vars.json" # FILE
_4_input_ai_model=7 # int, must exist on the MaaS

# Metastasis Risk classification XAI
_5_input_descriptor="metastasis-risk-classification-xai"
_5_input_ai_engine_version=12 # int, must exist on the MaaS
_5_input_ai_engine_version_user_vars="./auxiliary_files/${schema}/${_5_input_descriptor}_user_vars.json" # FILE
_5_input_ai_model=9 # int, must exist on the MaaS

# Medical report generation
_6_input_descriptor="medical-report-generation"
_6_input_ai_engine_version=13 # int, must exist on the MaaS
_6_input_ai_engine_version_user_vars="./auxiliary_files/${schema}/${_6_input_descriptor}_user_vars.json" # FILE

# ========================== DO NOT MODIFY CODE BELOW THIS LINE! ==================================
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
                                            \"descriptor\": \"${_1_input_descriptor}\",
                                            \"version\": ${_1_input_ai_engine_version},
                                            \"ai_model\": ${_1_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": \"${_2_input_descriptor}\",
                                            \"version\": ${_2_input_ai_engine_version},
                                            \"ai_model\": ${_2_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": \"${_3_input_descriptor}\",
                                            \"version\": ${_3_input_ai_engine_version},
                                            \"ai_model\": ${_3_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": \"${_4_input_descriptor}\",
                                            \"version\": ${_4_input_ai_engine_version},
                                            \"ai_model\": ${_4_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": \"${_5_input_descriptor}\",
                                            \"version\": ${_5_input_ai_engine_version},
                                            \"ai_model\": ${_5_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": \"${_6_input_descriptor}\",
                                            \"version\": ${_6_input_ai_engine_version}
                                        }
                                    ]
                                },
                                \"output_elements\": {}
                            }" \
                            -F external_data=@${input_external_data} \
                            -F ${_1_input_descriptor}_version_user_vars=@${_1_input_ai_engine_version_user_vars} \
                            -F ${_2_input_descriptor}_version_user_vars=@${_2_input_ai_engine_version_user_vars} \
                            -F ${_3_input_descriptor}_version_user_vars=@${_3_input_ai_engine_version_user_vars} \
                            -F ${_4_input_descriptor}_version_user_vars=@${_4_input_ai_engine_version_user_vars} \
                            -F ${_5_input_descriptor}_version_user_vars=@${_5_input_ai_engine_version_user_vars} \
                            -F ${_6_input_descriptor}_version_user_vars=@${_6_input_ai_engine_version_user_vars}

# --> SUCCESSFUL OUTPUT
# code: 201
# content: check successful_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
