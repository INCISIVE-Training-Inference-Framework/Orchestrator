#!/bin/bash

# --> DESCRIPTION
# It is a script that retrieves a job from the Orchestrator

# --> PREREQUISITES
# - curl installed
# - the job already exists in the Orchestrator

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_service_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
id=1

# --> CODE
# obtain global information
curl -X GET http://${orchestrator_service_hostname}/api/jobs/${id}/

# obtain config file url (no need to -> the url is always the same, this step can be skip)
ai_engine_config=$(curl -s -X GET http://${orchestrator_service_hostname}/api/jobs/${id}/ | jq -r '.ai_engine_config')

# download model files
curl -s -X GET ${ai_engine_config} --output ai_engine_config.json


# --> INFORMATION
# The responses are the same as the output when creating each of the use cases
# Some aspects to mention:
# use_case: can only get the value of one of the available use cases
# status: can only take the following values: Pending, Running, Succeeded and Failed
# updated_at: is updated each time the status of the job changes
# result: it only appears if the job has succesfully finished and it can have the following values depending on the use case:
# - training_from_scratch: a link to the created model i.e. http://${maas_api_hostname}/api/models/${id}/
# - training_from_pretrained_model: idem
# - evaluating_from_pretrained_model: a link to the metrics of the model i.e. http://${maas_api_hostname}/api/metrics/?model=${id}
# - inferencing_from_pretrained_model: a link to the inference results i.e. http://${maas_api_hostname}/api/inference_results/${id}/download_result_files/

# --> SUCCESFULL OUTPUT
# code: 200
# content: check succesfull_output_finished_XXX.json for each use case response when the job has finished succesfully

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
