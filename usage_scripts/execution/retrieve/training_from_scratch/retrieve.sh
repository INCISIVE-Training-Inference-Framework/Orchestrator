#!/bin/bash

# --> DESCRIPTION
# It is a script that retrives an Execution of the schema "training_from_scratch" from the Orchestrator. It shows the different outputs depending on the status of the Execution.

# --> PREREQUISITES
# - curl installed

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
id=1

# --> CODE
# obtain global information
curl -X GET http://${orchestrator_api_hostname}/api/executions/${id}/

# obtain version_user_vars url (no need to -> the url is always the same, this step can be skip)
version_user_vars_url=$(curl -s -X GET http://${orchestrator_api_hostname}/api/executions/${id}/ | jq -r '.ai_elements.ai_engines[0].version_user_vars')

# download version_user_vars
curl -s -X GET ${version_user_vars_url} --output version_user_vars.json

# --> SUCCESSFUL OUTPUT
# code: 200
# content: 
#   pending status -> check pending_output.json
#   running status -> check running_output.json
#   failed status -> check failed_output.json
#   succeeded status -> check succeeded_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
