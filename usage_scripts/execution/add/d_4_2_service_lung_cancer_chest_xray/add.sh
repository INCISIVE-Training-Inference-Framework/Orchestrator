#!/bin/bash

# --> DESCRIPTION
# It is a script that creates an Execution from the "d_4_2_lung_cancer_chest_xray" Schema of the Orchestrator

# --> PREREQUISITES
# - curl installed

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES

# main attributes
schema="d_4_2_lung_cancer_chest_xray" # str

# input attributes

input_external_data="./auxiliary_files/d_4_2_service_lung_cancer_chest_xray/external_data.zip" # FILE

# AI logic attributes

# 1. Lung Chest XRay Classification (ICCS)
_1_input_ai_engine_version=1 # int, must exist on the MaaS
_1_input_ai_engine_version_user_vars="./auxiliary_files/d_4_2_service_lung_cancer_chest_xray/lung_chest_xray_classification_user_vars.json" # FILE
_1_input_ai_model=1 # int, must exist on the MaaS

# 2. Lung Chest XRay Classification - XAI (SQD)
_2_input_ai_engine_version=7 # int, must exist on the MaaS
_2_input_ai_engine_version_user_vars="./auxiliary_files/d_4_2_service_lung_cancer_chest_xray/lung_sqd_xai_user_vars.json" # FILE
_2_input_ai_model=1 # int, must exist on the MaaS

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
                                            \"descriptor\": \"classification\",
                                            \"version\": ${_1_input_ai_engine_version},
                                            \"ai_model\": ${_1_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": \"xai\",
                                            \"version\": ${_2_input_ai_engine_version},
                                            \"ai_model\": ${_2_input_ai_model}
                                        }
                                    ]
                                },
                                \"output_elements\": {}
                            }" \
                            -F external_data=@${input_external_data} \
                            -F classification_version_user_vars=@${_1_input_ai_engine_version_user_vars} \
                            -F xai_version_user_vars=@${_2_input_ai_engine_version_user_vars}

# --> SUCCESSFUL OUTPUT
# code: 201
# content: check successful_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
