#!/bin/bash

# --> DESCRIPTION
# It is a script that retrieves a Schemas from the Orchestrator.

# --> PREREQUISITES
# - curl and jq installed
# - the Schema has been already uploaded to the Orchestrator

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
id="training_from_scratch"

# --> CODE
# obtain global information
response=$(curl -s -X GET http://${orchestrator_api_hostname}/api/schemas/${id}/)
echo ${response}

# obtain auxiliary file' url (no need to -> the url is always the same, this step can be skip)
auxiliary_file_url=$(echo ${response} | jq -r '.auxiliary_file')

# download auxiliary file
curl -s -X GET ${auxiliary_file_url} --output auxiliary_file.yaml

# --> SUCCESSFUL OUTPUT
# code: 200
# content: check successful_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
