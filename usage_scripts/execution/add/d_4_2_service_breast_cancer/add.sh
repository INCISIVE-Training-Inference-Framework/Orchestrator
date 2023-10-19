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
schema="d_4_2_breast_cancer_mg" # str

# input attributes

input_external_data="./auxiliary_files/d_4_2_service_breast_cancer_mg/external_breast_mg_input.zip" # FILE

# AI logic attributes
# MG prioritization
_1_input_descriptor="prioritization"
_1_input_ai_engine_version=3 # int, must exist on the MaaS
_1_input_ai_engine_version_user_vars="./auxiliary_files/d_4_2_service_breast_cancer_mg/mg_prioritization_user_vars.json" # FILE
_1_input_ai_model=2 # int, must exist on the MaaS

# MG localization
_2_input_descriptor="localization"
_2_input_ai_engine_version=3 # int, must exist on the MaaS
_2_input_ai_engine_version_user_vars="./auxiliary_files/d_4_2_service_breast_cancer_mg/mg_localization_user_vars.json" # FILE
_2_input_ai_model=2 # int, must exist on the MaaS

# MG segmentation
_3_input_descriptor="segmentation"
_3_input_ai_engine_version=3 # int, must exist on the MaaS
_3_input_ai_engine_version_user_vars="./auxiliary_files/d_4_2_service_breast_cancer_mg/mg_segmentation_user_vars.json" # FILE
_3_input_ai_model=2 # int, must exist on the MaaS

# Birads classification XAI
_4_input_descriptor="birads-classification-xai"
_4_input_ai_engine_version=4 # int, must exist on the MaaS
_4_input_ai_engine_version_user_vars="./auxiliary_files/d_4_2_service_breast_cancer_mg/birads_classification_xai_user_vars.json" # FILE
_4_input_ai_model=3 # int, must exist on the MaaS

# Density classification XAI
_5_input_descriptor="density-classification-xai"
_5_input_ai_engine_version=4 # int, must exist on the MaaS
_5_input_ai_engine_version_user_vars="./auxiliary_files/d_4_2_service_breast_cancer_mg/density_classification_xai_user_vars.json" # FILE
_5_input_ai_model=10 # int, must exist on the MaaS

# Medical report generation
_6_input_descriptor="medical-report-generation"
_6_input_ai_engine_version=5 # int, must exist on the MaaS
_6_input_ai_engine_version_user_vars="./auxiliary_files/d_4_2_service_breast_cancer_mg/medical_report_generation_user_vars.json" # FILE

# output attributes

# ============================== DO NOT TOUCH BELOW THIS LINE ====================================================
# --> CODE
curl -X POST http://${orchestrator_api_hostname}/api/executions/ \
                            -H "Content-Type:multipart/form-data" \
                            -F data="{
                                \"schema\": \"${schema}\",
                                \"input_elements\": {},
                                \"ai_elements\": {
                                    \"ai_engines\": [
                                        {
                                            \"descriptor\": ${_1_input_descriptor},
                                            \"version\": ${_1_input_ai_engine_version},
                                            \"ai_model\": ${_1_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": ${_2_input_descriptor},
                                            \"version\": ${_2_input_ai_engine_version},
                                            \"ai_model\": ${_2_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": ${_3_input_descriptor},
                                            \"version\": ${_3_input_ai_engine_version},
                                            \"ai_model\": ${_3_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": ${_4_input_descriptor},
                                            \"version\": ${_4_input_ai_engine_version},
                                            \"ai_model\": ${_4_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": ${_5_input_descriptor},
                                            \"version\": ${_5_input_ai_engine_version},
                                            \"ai_model\": ${_5_input_ai_model}
                                        },
                                        {
                                            \"descriptor\": ${_6_input_descriptor},
                                            \"version\": ${_6_input_ai_engine_version}
                                        }
                                    ]
                                },
                                \"output_elements\": {}
                            }" \
                            -F external_data=@${input_external_data} \
                            -F segmentation_version_user_vars=@${_1_input_ai_engine_version_user_vars} \
                            -F localization_version_user_vars=@${_2_input_ai_engine_version_user_vars} \
                            -F prioritization_version_user_vars=@${_3_input_ai_engine_version_user_vars} \
                            -F birads-classification-xai_version_user_vars=@${_4_input_ai_engine_version_user_vars} \
                            -F density-classification-xai_version_user_vars=@${_5_input_ai_engine_version_user_vars} \
                            -F medical-report-generation_version_user_vars=@${_6_input_ai_engine_version_user_vars}

# --> SUCCESSFUL OUTPUT
# code: 201
# content: check successful_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
