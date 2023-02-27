#!/bin/bash

# --> DESCRIPTION
# It is a script that requests the Orchestrator component to perform the inferencing_from_pretrained_model job use case

# --> PREREQUISITES
# - curl installed

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_service_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
ai_engine_config="./auxiliary_files/ai_engine_config.json"
# information about the model to use
model_id=1  # it should exist in MaaS component
# data to predict
input_data_files="./auxiliary_files/inferencing_input_data_files.zip"

# --> CODE
curl -X POST http://${orchestrator_service_hostname}/api/jobs/inferencing_from_pretrained_model/ \
                            -H "Content-Type:multipart/form-data" \
                            -F data="{\"model_id\": ${model_id}}" \
                            -F input_data_files=@${input_data_files} \
                            -F ai_engine_config=@${ai_engine_config}
                  
# --> SUCCESFULL OUTPUT
# code: 201
# content: check succesfull_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
