from django.db import transaction

from main.factory import Factory
from main.models import RunningContainer, RunningContainerStatus, RunningExecutionStatus, FinishedExecution, \
    FinishedExecutionStatus, FinishedContainer, FinishedContainerStatus


class ContainerStateMachine:

    states = {'PD': 0, 'RN': 1, 'FS': 2, 'FL': 3}
    transitions = [
        ['PD', 'RN', 'FS', 'FL'],  # in pending state
        ['NULL', 'NULL', 'FS', 'FL'],  # in running state
        ['NULL', 'NULL', 'NULL', 'NULL'],  # in finished state
        ['NULL', 'NULL', 'NULL', 'NULL']  # in failure state
    ]

    def __init__(self):
        raise Exception('This static class can not be instantiated')

    @staticmethod
    def update_status(container: RunningContainer, new_status: str):
        old_status = container.status
        old_status_id = ContainerStateMachine.states.get(old_status)  # TODO check errors
        new_status_id = ContainerStateMachine.states.get(new_status)  # TODO check errors
        real_new_status = ContainerStateMachine.transitions[old_status_id][new_status_id]
        if real_new_status != 'NULL':
            ContainerStateMachine.perform_action(container, new_status_id)
            return real_new_status
        else:
            return None

    @staticmethod
    def perform_action(container: RunningContainer, new_status_id: int):
        actions = [
            ContainerStateMachine.container_to_pending_action,
            ContainerStateMachine.container_to_running_action,
            ContainerStateMachine.container_to_finished_action,
            ContainerStateMachine.container_to_failure_action
        ]
        actions[new_status_id](container, new_status_id)

    @staticmethod
    def container_to_pending_action(container: RunningContainer, new_status_id: int):
        pass  # nothing to do

    @staticmethod
    def container_to_running_action(container: RunningContainer, new_status_id: int):
        container.status = RunningContainerStatus.RUNNING
        # check if all the containers of the container execution ara running
        execution_containers = RunningContainer.objects.filter(execution=container.execution).exclude(id=container.id)
        if all([execution_container.status == RunningContainerStatus.RUNNING for execution_container in execution_containers]):
            container.execution.status = RunningExecutionStatus.RUNNING
            # update container and execution status
            with transaction.atomic():
                container.save()
                container.execution.save()
        else:
            # update container status
            container.save()

    @staticmethod
    def container_to_finished_action(container: RunningContainer, new_status_id: int):
        # check if all the containers of the container execution have finished
        execution_containers = RunningContainer.objects.filter(execution=container.execution)
        execution_containers_without_itself = execution_containers.exclude(id=container.id)
        if all([execution_container.status == RunningContainerStatus.FINISHED for execution_container in execution_containers_without_itself]):
            # move execution along containers to archive
            finished_execution = FinishedExecution.objects.create(
                status=FinishedExecutionStatus.SUCCESS,
                started_at=container.execution.created_at
            )
            finished_containers = [FinishedContainer.objects.create(
                status=FinishedContainerStatus.SUCCESS,
                started_at=execution_container.created_at,
                node=execution_container.node,
                ai_engine=execution_container.ai_engine,
                data=execution_container.data,
                model=execution_container.model,
                execution=finished_execution
            ) for execution_container in execution_containers]
            with transaction.atomic():
                finished_execution.save()
                for finished_container in finished_containers:
                    finished_container.save()
                container.execution.delete()
        else:
            # update container status
            container.status = RunningContainerStatus.FINISHED
            container.save()

    @staticmethod
    def container_to_failure_action(container: RunningContainer, new_status_id: int):
        # check the failures of the container
        if container.failures > 2:
            # stop execution  # TODO check that all containers get stopped
            execution_containers = RunningContainer.objects.filter(execution=container.execution)
            container_manager = Factory.get_container_manager()
            for execution_container in execution_containers:
                if execution_container.status in [RunningContainerStatus.RUNNING, RunningContainerStatus.PENDING]:
                    container_manager.stop_container(execution_container)

            # move execution along containers to archive
            finished_execution = FinishedExecution.objects.create(
                status=FinishedExecutionStatus.FAILURE,
                started_at=container.execution.created_at
            )
            finished_containers = [FinishedContainer.objects.create(
                status=FinishedContainerStatus.FAILURE,
                started_at=execution_container.created_at,
                node=execution_container.node,
                ai_engine=execution_container.ai_engine,
                data=execution_container.data,
                model=execution_container.model,
                execution=finished_execution
            ) for execution_container in execution_containers]
            with transaction.atomic():
                finished_execution.save()
                for finished_container in finished_containers:
                    finished_container.save()
                container.execution.delete()
        else:
            # try to run again the failure container
            container.status = RunningContainerStatus.PENDING
            container.failures += 1
            container_manager = Factory.get_container_manager()
            container_manager.create_container(container)
            container.save()
