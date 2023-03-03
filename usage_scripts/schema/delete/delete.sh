#!/bin/bash

# --> DESCRIPTION
# It is a script that deletes a Schema from the Orchestrator.
# It also deletes all related Executions

# --> PREREQUISITES
# - curl installed
# - the Schema has been already uploaded to the Orchestrator

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
id="training_from_scratch"

# --> CODE
curl -X DELETE http://${orchestrator_api_hostname}/api/schemas/${id}/

# --> SUCCESSFUL OUTPUT
# code: 204
# content: nothing

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
