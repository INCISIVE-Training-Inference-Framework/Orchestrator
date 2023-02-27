#!/bin/bash

# --> DESCRIPTION
# It is a script that lists the jobs of the Orchestrator. It also shows how to perform filtering, paging and sorting.

# --> PREREQUISITES
# - curl installed

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_service_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
filter_use_case="training_from_scratch"

# --> CODE
# list all jobs
curl -X GET http://${orchestrator_service_hostname}/api/jobs/

# list all jobs of the selected use case
curl -X GET http://${orchestrator_service_hostname}/api/jobs/?use_case=${filter_use_case}
# this kind of filtering can be done for the following job attributes: ai_engine_id, model_id, model_name, model_type, status and use_case

# list all jobs of the selected page. The response also includes two pointers next and previous for moving around the pages along the count parameter with the total amount of items. It is also possible to specify the number of items per page with the parameter page_size
curl -X GET http://${orchestrator_service_hostname}/api/jobs/?page=2

# list all jobs ordered by the updated_at date desc (by default they are sorted by created_at desc)
curl -X GET http://${orchestrator_service_hostname}/api/jobs/?sort=-updated_at
# this kind of sorting can be done for the following job attributes: ai_engine_id, model_id, model_name, model_type, status, use_case, created_at and updated_at

# --> SUCCESFULL OUTPUT
# code: 200
# content: check succesfull_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
