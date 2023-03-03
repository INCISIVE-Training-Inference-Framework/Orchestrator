#!/bin/bash

# --> DESCRIPTION
# It is a script that retrives an Execution of the schema "d_4_2_service_breast_cancer" from the Orchestrator. It shows the different outputs depending on the status of the Execution.

# --> PREREQUISITES
# - curl installed

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
id=4

# --> CODE
# obtain global information
curl -X GET http://${orchestrator_api_hostname}/api/executions/${id}/

# obtain external_data url (no need to -> the url is always the same, this step can be skip)
external_data_url=$(curl -s -X GET http://${orchestrator_api_hostname}/api/executions/${id}/ | jq -r '.input_elements.external_data.contents')

# download version_user_vars
curl -s -X GET ${external_data_url} --output external_data.zip

# obtain version_user_vars urls (no need to -> the urls are always the same, this step can be skip)
prioritization_and_segmentation_version_user_vars_url=$(curl -s -X GET http://${orchestrator_api_hostname}/api/executions/${id}/ | jq -r '.ai_elements.ai_engines[0].version_user_vars')
birads_classification_version_user_vars_url=$(curl -s -X GET http://${orchestrator_api_hostname}/api/executions/${id}/ | jq -r '.ai_elements.ai_engines[1].version_user_vars')
density_classification_version_user_vars_url=$(curl -s -X GET http://${orchestrator_api_hostname}/api/executions/${id}/ | jq -r '.ai_elements.ai_engines[2].version_user_vars')
medical_report_generation_version_user_vars_url=$(curl -s -X GET http://${orchestrator_api_hostname}/api/executions/${id}/ | jq -r '.ai_elements.ai_engines[3].version_user_vars')

# download version_user_vars
curl -s -X GET ${prioritization_and_segmentation_version_user_vars_url} --output prioritization_and_segmentation_version_user_vars_url_version_user_vars.json
curl -s -X GET ${birads_classification_version_user_vars_url} --output birads_classification_version_user_vars_url_version_user_vars.json
curl -s -X GET ${density_classification_version_user_vars_url} --output density_classification_version_user_vars_url_version_user_vars.json
curl -s -X GET ${medical_report_generation_version_user_vars_url} --output medical_report_generation_version_user_vars_url_version_user_vars.json

# --> SUCCESSFUL OUTPUT
# code: 200
# content: 
#   pending status -> check pending_output.json
#   running status -> check running_output.json
#   failed status -> check failed_output.json
#   succeeded status -> check succeeded_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
