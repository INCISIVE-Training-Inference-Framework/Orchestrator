# INCISIVE platform Orchestrator component
This repository contains the code of the Orchestrator component of the INCISIVE platform along its auxiliary components. Check the official documentation for a full specification of this component and the overall service.

Follow the next instructions to run the component in local premisses. Check the official documentation for the deployment instructions with docker:
- install pip and python3.9
- install the python libraries specified in the requirements.txt file
- go inside the app directory: cd app
- create database: python3 manage.py migrate
- run django server: python3 manage.py runserver 0.0.0.0:8000
- create superuser: python3 manage.py createsuperuser
- go to 0.0.0.0:8000, log in and start developing
