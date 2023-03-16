#!/bin/bash

# --> DESCRIPTION
# It is a script that creates an Execution from the "inferencing_from_pretrained_model" Schema of the Orchestrator

# --> PREREQUISITES
# - curl installed

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES

# main attributes
schema="inferencing_from_pretrained_model" # str

# input attributes

input_external_data="./auxiliary_files/external_data.zip" # FILE

# AI logic attributes

input_ai_engine_version=1 # int, must exist on the MaaS
input_ai_engine_version_user_vars="./auxiliary_files/user_vars.json" # FILE
input_ai_model=1 # int, must exist on the MaaS

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
                                            \"descriptor\": \"main-ai-engine\",
                                            \"version\": ${input_ai_engine_version},
                                            \"ai_model\": ${input_ai_model}
                                        }
                                    ]
                                },
                                \"output_elements\": {}
                            }" \
                            -F external_data=@${input_external_data} \
                            -F main-ai-engine_version_user_vars=@${input_ai_engine_version_user_vars}

# --> SUCCESSFUL OUTPUT
# code: 201
# content: check successful_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
