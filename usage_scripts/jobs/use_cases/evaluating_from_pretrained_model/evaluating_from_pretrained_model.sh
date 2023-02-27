#!/bin/bash

# --> DESCRIPTION
# It is a script that requests the Orchestrator component to perform the evaluating_from_pretrained_model job use case

# --> PREREQUISITES
# - curl installed

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_service_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
ai_engine_config="./auxiliary_files/ai_engine_config.json"
data_partners_patients="{\"data-partner-1\": [\"1\", \"2\"]}"  # should be compliant with the labels assigned to the nodes of the Kubernetes cluster
# information about the model to use
model_id=1  # it should exist in MaaS component

# --> CODE
curl -X POST http://${orchestrator_service_hostname}/api/jobs/evaluating_from_pretrained_model/ \
                            -H "Content-Type:multipart/form-data" \
                            -F data="{
                            \"model_id\": ${model_id},
                            \"data_partners_patients\": ${data_partners_patients}}" \
                            -F ai_engine_config=@${ai_engine_config}
                  
# --> SUCCESFULL OUTPUT
# code: 201
# content: check succesfull_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
