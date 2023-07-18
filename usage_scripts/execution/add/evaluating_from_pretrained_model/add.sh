#!/bin/bash

# --> DESCRIPTION
# It is a script that creates an Execution from the "evaluating_from_pretrained_model" Schema of the Orchestrator

# --> PREREQUISITES
# - curl installed

# --> REQUIRED GLOBAL VARIABLES
# - orchestrator_api_hostname
source ../global_variables.sh

# --> REQUIRED LOCAL VARIABLES

# main attributes
schema="evaluating_from_pretrained_model" # str

# input attributes

input_platform_data='{
			"data-partner-1": {
				"fields_definition": {},
				"sheets_definition": {},
				"patients": [
				  {
					"id": "004-000001",
					"clinical_data": {}
				  },
				  {
					"id": "004-000002",
					"clinical_data": {}
				  }
                ]
			}
		}' # dict[str:dict], the partners and patients must exist on the platform

# AI logic attributes

input_ai_engine_version=1 # int, must exist on the MaaS
input_ai_engine_version_user_vars="./auxiliary_files/user_vars.json" # FILE
input_ai_engine_model=1 # int, must exist on the MaaS

# output attributes


# --> CODE
curl -X POST http://${orchestrator_api_hostname}/api/executions/ \
                            -H "Content-Type:multipart/form-data" \
                            -F data="{
                                \"schema\": \"${schema}\",
                                \"input_elements\": {
                                    \"platform_data\": {
                                        \"data_partners_patients\": ${input_platform_data}
                                    }
                                },
                                \"ai_elements\": {
                                    \"ai_engines\": [
                                        {
                                            \"descriptor\": \"main-ai-engine\",
                                            \"version\": ${input_ai_engine_version},
                                            \"ai_model\": ${input_ai_engine_model}
                                        }
                                    ]
                                },
                                \"output_elements\": {}
                            }" \
                            -F main-ai-engine_version_user_vars=@${input_ai_engine_version_user_vars}

# --> SUCCESSFUL OUTPUT
# code: 201
# content: check successful_output.json

# --> FAILED OUTPUT
# returns 4XX for bad requests along the reason and 5XX for internal errors
