#!/bin/bash

# --> DESCRIPTION
# It is a script that deletes a job from the Orchestrator

# --> PREREQUISITES
# - curl installed
# - the job already exists in the Orchestrator

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_service_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
id=1

# --> CODE
curl -X DELETE http://${orchestrator_service_hostname}/api/jobs/${id}/

# --> SUCCESFULL OUTPUT
# code: 204
# content: nothing

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
