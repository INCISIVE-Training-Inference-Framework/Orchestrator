#!/bin/bash

# --> DESCRIPTION
# It is a script that updates the status of an Execution of the Orchestrator from the Schema 'training_from_scratch_federated_learning' to succeeded

# --> PREREQUISITES
# - curl installed
# - the Execution have been already created in the Orchestrator

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
id=5

ai_model=1 # int, must exist on the MaaS
_1_evaluation_metric=1 # int, must exist on the MaaS
_2_evaluation_metric=2 # int, must exist on the MaaS
_3_evaluation_metric=3 # int, must exist on the MaaS

# --> CODE
curl -X PATCH http://${orchestrator_api_hostname}/api/executions/${id}/update_to_succeeded/ \
                            -H "Content-Type:multipart/form-data" \
                            -F data="{
                                \"ai_model\": {
                                    \"ai_model\": ${ai_model}
                                },
                                \"evaluation_metrics\": [
                                    {\"evaluation_metric\": ${_1_evaluation_metric}},
                                    {\"evaluation_metric\": ${_2_evaluation_metric}},
                                    {\"evaluation_metric\": ${_3_evaluation_metric}}
                                ]
                            }"

# --> SUCCESSFUL OUTPUT
# code: 200
# content: check successful_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
