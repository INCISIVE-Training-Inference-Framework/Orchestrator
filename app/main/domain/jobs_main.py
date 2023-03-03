import logging

from django.db import Error

from main.domain.exceptions import InternalError
from main.factory import Factory
from main.models import \
    Job, \
    JobSchemaStatus, \
    JobWithPretrainedModel

logger = logging.getLogger(__name__)
PLATFORM_ADAPTER = Factory.get_platform_adapter()
CONTAINER_MANAGER = Factory.get_container_manager()


class JobsDomain:

    def __init__(self):
        raise Exception('This static class can not be instantiated')

    @staticmethod
    def start_job_execution(job: Job) -> Job:
        public_error_message = f'Internal error: Error while performing the {job.use_case} use case'

        if isinstance(job, JobWithPretrainedModel):
            # get AI Engine id
            ai_engine_id = PLATFORM_ADAPTER.check_model_correctness_and_get_ai_engine(job)
        else:
            ai_engine_id = job.ai_engine_id  # it is JobTrainingFromScratch

        # get AI Engine container_name and container_version
        container_name, container_version = PLATFORM_ADAPTER.check_ai_engine_correctness_and_get_container_metadata(
            ai_engine_id,
            job
        )

        # save job object
        try:
            job.save()
        except Error as e:
            raise InternalError(str(e), public_error_message)

        # call the container manager
        try:
            CONTAINER_MANAGER.start_job_execution(PLATFORM_ADAPTER, ai_engine_id, container_name, container_version, job)
        except InternalError as e:
            try:
                job.delete()
            except Error as e:
                raise InternalError(str(e), public_error_message)
            raise InternalError(e.internal_message, public_error_message)

        return job

    # triggered internally at intervals of time
    @staticmethod
    def update_jobs_status():
        # only update executions that have not finished
        # and only able to put Failed or Running status, never Succeeded
        try:
            jobs = Job.objects.filter(status__in=[JobSchemaStatus.PENDING, JobSchemaStatus.RUNNING])
            logger.info(f'Number of not finished jobs: {len(jobs)}')
            for job in jobs:
                try:
                    new_execution_status = CONTAINER_MANAGER.get_job_status(job)
                    if new_execution_status != job.status and new_execution_status in {JobSchemaStatus.RUNNING, JobSchemaStatus.FAILED}:
                        job.status = new_execution_status
                        job.save()
                # TODO add time out to kill executions that took much longer than expected
                except InternalError as e:
                    logger.error(f'Caught internal error while updating jobs status: {e.internal_message}')
                finally:
                    if job.status == JobSchemaStatus.FAILED:
                        CONTAINER_MANAGER.ended_job_execution(job, JobSchemaStatus.FAILED)
        except Error as e:
            logger.error(f'Uncaught internal error while updating jobs status: {e}')

    # triggered at the end of the job executions
    @staticmethod
    def ended_job_execution(job: Job, finish_status: JobSchemaStatus.choices, result: str) -> Job:
        is_ok = True
        exception = None

        # update job status and result
        if job.status != JobSchemaStatus.SUCCEEDED and job.status != JobSchemaStatus.FAILED:
            job.status = finish_status
            if finish_status == JobSchemaStatus.SUCCEEDED:
                job.result = result
            try:
                job.save()
            except Error as e:
                is_ok = False
                exception = e

            # transmit end information to the container manager
            try:
                CONTAINER_MANAGER.ended_job_execution(job, finish_status)
            except InternalError as e:
                is_ok = False
                exception = e

            if not is_ok:
                raise InternalError(str(exception), f'Internal error while updating execution status')
            else:
                return job
