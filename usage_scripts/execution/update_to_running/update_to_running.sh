#!/bin/bash

# --> DESCRIPTION
# It is a script that updates the status of an Execution of the Orchestrator to running

# --> PREREQUISITES
# - curl installed
# - the Execution have been already created in the Orchestrator

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
id=1

# --> CODE
curl -X PATCH http://${orchestrator_api_hostname}/api/executions/${id}/update_to_running/ \
                            -H "Content-Type:multipart/form-data" \
                            -F data="{}"

# --> SUCCESSFUL OUTPUT
# code: 200
# content: check successful_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
