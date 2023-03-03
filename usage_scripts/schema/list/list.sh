#!/bin/bash

# --> DESCRIPTION
# It is a script that lists the available Schemas of the Orchestrator. It also shows how to perform filtering, paging and sorting.

# --> PREREQUISITES
# - curl installed

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES
filter_type="joint"

# --> CODE
# list all available Schemas
curl -X GET http://${orchestrator_api_hostname}/api/schemas/

# list all available Schemas of the selected type
curl -X GET http://${orchestrator_api_hostname}/api/schemas/?type=${filter_type}
# this kind of filtering can be done for the following Schema attributes: name, type and implementation

# list all Schemas of the selected page. The response also includes two pointers next and previous for moving around the pages along the count parameter with the total amount of items. It is also possible to specify the number of items per page with the parameter page_size
curl -X GET http://${orchestrator_api_hostname}/api/schemas/?page=2

# list all Schemas ordered by the name desc (by default they are sorted by created_at desc)
curl -X GET http://${orchestrator_api_hostname}/api/schemas/?sort=-name
# this kind of sorting can be done for the following Schema attributes: name, type, implementation and created_at

# --> SUCCESSFUL OUTPUT
# code: 200
# content: check successful_output.json for the output of the first request (all other requests follow the same format)

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
