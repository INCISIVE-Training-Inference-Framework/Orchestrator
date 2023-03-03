#!/bin/bash

# --> DESCRIPTION
# It is a script that updates the status of an Execution of the Orchestrator to failed

# --> PREREQUISITES
# - curl installed
# - the Execution have been already created in the Orchestrator

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
id=1
error_message="some error message" # str

# --> CODE
curl -X PATCH http://${orchestrator_api_hostname}/api/executions/${id}/update_to_failed/ \
                            -H "Content-Type:multipart/form-data" \
                            -F data="{\"message\": \"${error_message}\"}"

# --> SUCCESSFUL OUTPUT
# code: 200
# content: check successful_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
