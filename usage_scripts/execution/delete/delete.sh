#!/bin/bash

# --> DESCRIPTION
# It is a script that deletes an Execution from the Orchestrator. Execution.

# --> PREREQUISITES
# - curl installed
# - the Execution has been already created in the Orchestrator

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
id=1

# --> CODE
curl -X DELETE http://${orchestrator_api_hostname}/api/executions/${id}/


# --> SUCCESSFUL OUTPUT
# code: 204
# content: nothing

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
