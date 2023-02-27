#!/bin/bash

# --> DESCRIPTION
# It is a script that requests the Orchestrator component to perform the training_from_scratch job use case using multiple data partners

# --> PREREQUISITES
# - curl installed

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_service_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
ai_engine_id=1  # it should exist in MaaS component
data_partners_patients="{\"data-partner-1\": [\"1\", \"2\"], \"data-partner-2\": [\"1\", \"3\"]}"  # should be compliant with the labels assigned to the nodes of the Kubernetes cluster
number_iterations=2
ai_engine_config="./auxiliary_files/ai_engine_config.json"
# information about the model to create
model_name="mnist_epochs_1_training_from_scratch_parallel" 
model_type="default"
model_description="testing_infrastructure"

# --> CODE
curl -X POST http://${orchestrator_service_hostname}/api/jobs/training_from_scratch/ \
                            -H "Content-Type:multipart/form-data" \
                            -F data="{
                            \"ai_engine_id\": ${ai_engine_id},
                            \"data_partners_patients\": ${data_partners_patients},
                            \"number_iterations\": ${number_iterations},
                            \"model_name\": \"${model_name}\",
                            \"model_type\": \"${model_type}\",
                            \"model_description\": \"${model_description}\"}" \
                            -F ai_engine_config=@${ai_engine_config}
                  
# --> SUCCESFULL OUTPUT
# code: 201
# content: check succesfull_output_parallel.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
