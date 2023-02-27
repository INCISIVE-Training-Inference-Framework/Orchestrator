# we use the slim image which is better optimized
FROM python:3.9-slim

# install os packages, some of them needed to install the dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential gcc git && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip3 install --upgrade pip
    
# define and create working directory
WORKDIR /usr/application

# install required python packages
# copy step is done separately to not reinstall the python packages when the code changes
COPY /requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# copy the files inside the working directory (the .gitignore file ignores the not necessary files)
COPY / .

# change directory permissions to allow access for not root users
RUN chmod -R a+rwX .

# specify command to start the container
WORKDIR /usr/application/app
ENV PYTHONUNBUFFERED=TRUE
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "orchestrator.wsgi:application"]

# port to expose at runtime
EXPOSE 8000/tcp
