#!/bin/bash

# --> DESCRIPTION
# It is a script that updates the Orchestrator component of the end of a job execution

# --> PREREQUISITES
# - curl installed

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_service_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
id=1  # it should exist in the Orchestrator component
status="Succeeded" 
result="http://127.0.0.2:8000/api/models/1/"  # only if status equal to Succeeded

# --> CODE
curl -X PATCH http://${orchestrator_service_hostname}/api/jobs/${id}/ended_job_execution/ \
             -H "Content-Type: application/json" \
             -d "{\"status\": \"${status}\",
                  \"result\": \"${result}\"}"
                  
# --> SUCCESFULL OUTPUT
# code: 200
# content: check succesfull_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
