#!/bin/bash

# --> DESCRIPTION
# It is a script that lists the available Executions of the Orchestrator. It also shows how to perform filtering, paging and sorting.

# --> PREREQUISITES
# - curl installed

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
filter_schema="training_from_scratch"

# --> CODE
# list all available Executions
curl -X GET http://${orchestrator_api_hostname}/api/executions/

# list all available Executions with the desired status
curl -X GET http://${orchestrator_api_hostname}/api/executions/?schema=${filter_schema}
# this kind of filtering can be done for the following attributes: schema

# list all Executions of the selected page. The response also includes two pointers next and previous for moving around the pages along the count parameter with the total amount of items. It is also possible to specify the number of items per page with the parameter page_size
curl -X GET http://${orchestrator_api_hostname}/api/executions/?page=2

# list all Executions ordered by the updated_at date desc (by default they are sorted by created_at desc)
curl -X GET http://${orchestrator_api_hostname}/api/executions/?sort=-updated_at
# this kind of sorting can be done for the following attributes: schema, created_at and updated_at

# --> SUCCESSFUL OUTPUT
# code: 200
# content: check successful_output.json for the output of the first request (all other requests follow the same format)

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
