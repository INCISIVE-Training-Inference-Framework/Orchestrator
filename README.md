# Orchestrator
_This component was created as an output of the INCISIVE European project software, forming part of the final platform_

### Introduction
The Orchestrator is the component in charge of controlling the placement and behaviour of all AI Executions and the dependencies between them when performing AI functionalities in the INCISIVE infrastructure. That is to say, the Orchestrator is the component that receives the requests for performing each of the AI functionalities, and the one that, in consequence, deploys the needed AI related components (specifically, the AI Engine, the Federated Learning Manager or the Processor Resource Manager) with the necessary configuration. Among others, it defines where the different elements are placed, how many resources are allocated and with what structure they are deployed. In the same way, the Orchestrator is responsible for keeping track of the AI Executions and informing about their status.

Check the last version of the D.3.X report for the full abstract description of the component and its functionalities.

### Implementation
The Orchestrator is a simple API that can run all the expected AI functionalities. It is implemented in the Python programming language, and it is based on the Django framework. Before developing further the component, please check the official documentation of [Django](https://docs.djangoproject.com/en/4.2/) along the [quick start tutorial](https://docs.djangoproject.com/en/4.2/intro/).

The component uses the [Argo Workflows](https://argoproj.github.io/argo-workflows/) framework for making all the possible deployments of the need AI related components. The Orchestrator expects it to be already deployed and fully operational in the corresponding platform along a configured [Artifact Repository](https://argoproj.github.io/argo-workflows/configure-artifact-repository/).

Concerning the storage, the Orchestrator manages both a relational database and a file system storage. The file system storage is administrated directly by Django inside the file system of the component, whereas the relational database uses a framework. It is configured to use a SQLite database in the development environment and an **external** Postgres database in the production environment. The file system storage is used to save all data corresponding natively to files, whereas the relational database stores all other types of data along the pointers to the locations of the stored files.

Lastly, for running federated learning, the Orchestrator uses the [Kafka](https://kafka.apache.org/) framework for doing all the required communications. The Orchestrator expects it to be already deployed and fully operational in the corresponding platform if using these kinds of AI Executions. 


### How to set up
This section describes how to set up the component with docker and directly with python. 

All the configuration is done through the [Settings](https://docs.djangoproject.com/en/4.2/ref/settings/) environment variables of Django. The important variables are the following:
- DEBUG (str, `true`or `false`): being `true` the development environment and `false` the production environment. This is used to set up, between other things, the different types of database.
- MEDIA_ROOT && MEDIA_URL (str): root path location to store the files in the file system storage.
- MAAS_API_HOSTNAME (str): being the hostname of the MaaS API, including the port.
- ORCHESTRATOR_API_HOSTNAME (str): being the hostname of the Orchestrator API, including the port.
- VALID_DATA_PARTNERS (list[str]): the nodes that are valid data providers (federated nodes), where training and evaluation AI Executions are meant to be run.
- VALID_AI_ENGINE_FUNCTIONALITIES(list[str]): the values to accept as functionalities.
- VALIDATE_WITH_MAAS (str, `true`or `false`): whether to use the MaaS to validate the information being sent to the Orchestrator API.
- PLATFORM_CENTRAL_NODE_LABEL_KEY (str): key of the label to use to mark the central node, where inference AI Executions are meant to be run.
- PLATFORM_CENTRAL_NODE_LABEL_VALUE (str): value of the label to use to mark the central node, where inference AI Executions are meant to be run.
- ARGO_WORKFLOWS_NAMESPACE (str): the namespace to use for deploying the Argo Workflows of the AI Executions.
- COMMUNICATION_ADAPTER (str, being `kafka` the only possible value): the identifier of the implementation to use to communicate during federated training AI Executions. Right now only is implemented with the Kafka framework.

#### Python directly
Follows a list with the instructions to set up the component with python directly:
- install python3.9 and pip 
- install the python libraries specified in the requirements.txt file
- create the SQLite database (check the Django documentation for a thorough description): `python3 app/manage.py migrate`
- run the component (check the Django documentation for a thorough description), add `DEBUG=true` to use the SQLite database: `python3 app/manage.py runserver 127.0.0.1:8000`

Notice that both the IP and the port can be changed, remember to modify accordingly the [ALLOWED_HOSTS](https://docs.djangoproject.com/en/4.2/ref/settings/#allowed-hosts) environment variable of Django.

#### Docker
Follows a list with the instructions to set up the component with docker. Notice that the docker deployment uses Gunicorn as HTTP server since Django only provides a development server.
- create the docker image: `docker build -f Dockerfile -t orchestrator .`
- run a docker container (use the desired parameters): `docker run -it --rm --network host orchestrator`

The default IP and port is 127.0.0.1:8000, it can be changed inside the Dockerfile.

### How to use
Once the Orchestrator is set up and its API is running on the determined location, it can be reached in the different endpoints of its API for performing all the functionalities. The way to run all functionalities is showed in a practical manner with shell scripts that can be found in the directory named as *usage_scripts/* in this same repository.

The full list of functionalities is the following:

- Schemas: An schema determines the flow of an AI Execution, the components involved and their running dependencies. At the moment, the Orchestrator only implements the possibility of defining them with Argo Workflows, but other frameworks could be configured in the future as well. The available use cases for the Schema concept are the following:
  - Create a new Schema
  - List the existent Schemas
  - Retrieve an existent Schema
  - Delete an existent Schema

  This repository contains the usage scripts for the next types of flows (although other schemas can be added very easily):
  - Training from scratch -> train a new AI Model from scratch with the data from a specific Data Provider
  - Training from a pretrained model -> fine tune a pretrained AI Model with the data from a specific Data Provider
  - Training from [...] in a federated manner -> train / fine tune an AI Model with the data from a specific set of Data Providers
  - Evaluating from a pretrained model -> evaluate a pretrained AI Model with the data from a specific Data Provider
  - Inferencing from a pretrained model -> perform inference from a pretrained AI Model
  - Breast Cancer MG Pipeline -> perform inference for mammographies with the set of AI Models specified in the D.4.X report
  - Breast Cancer MG Pipeline in one node -> same as before but only using one node (not parallelism)

- AI Executions: An AI Execution refers to the low-level action of running a specific Schema in the platform, containing the technical aspects like the location of the deployed components and their current status along the specific elements used as components of the Schema. The available use cases for the Execution concept are the following:
  - Create a new AI Execution
  - List the existent AI Executions
  - Retrieve an existent AI Execution
  - Delete an existent AI Execution
  - Update to running status an existent AI Execution
  - Update to failed status an existent AI Execution
  - Update to succeeded status an existent AI Execution

Concerning the database, here are the most useful commands to manage it (check the official Django documentation for a full list):
- Create a database migration -> `python3 app/manage.py makemigrations`. This should be executed every time there is a codewise change in the database structure. It will generate a file that will be used by the current database deployments to update their structure.
- Apply a database migration -> `python3 app/manage.py migrate`. It will update the database according to the available migration files.
- Clean all data from the database tables -> `python3 app/manage.py flush`. It will delete all the data from the database, maintaining the tables. It is recommended to perform this command along the command `rm -r storage/files/*`. This is a workaround for a bug that keeps some files in the file system storage even if their related object in the relational database is deleted.
- Reset the database -> `python3 app/manage.py migrate main zero`. It will clean all the data and tables from the database.

### Other
It is worth mentioning that the Orchestrator implements a cron routine inside *app/management/commands/* following the Django specification. This routine cleans some data that is produced when running federated training AI Executions. This task must be run externally if using these kinds of executions. It can be run in the following way: `python3 app/manage.py clean_old_kafka_topics`.
 
