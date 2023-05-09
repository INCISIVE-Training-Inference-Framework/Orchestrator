import logging
from typing import List

import kafka.errors
from django.conf import settings
from kafka.admin import KafkaAdminClient, NewTopic

from main.communication_adapter.communication_adapter_interface import CommunicationAdapterInterface
from main.exceptions import InternalError
from main.models import Execution, ExecutionStatus

logger = logging.getLogger(__name__)


class CommunicationAdapterKafka(CommunicationAdapterInterface):
    INITIALIZED = False

    # ---> Main methods

    @staticmethod
    def initialize() -> None:
        logger.info('Initializing kafka')

        # create general topic
        admin_client = None
        try:
            admin_client = KafkaAdminClient(
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    client_id='orchestrator'
            )
            status_topic = NewTopic(
                name='status',
                num_partitions=1,
                replication_factor=1,
                topic_configs={
                    'cleanup.policy': 'compact,delete',
                    'compression.type': 'uncompressed'
                }
            )
            admin_client.create_topics(
                new_topics=[status_topic],
                validate_only=False
            )
            CommunicationAdapterKafka.INITIALIZED = True
        except kafka.errors.TopicAlreadyExistsError:
            logger.warning('Warning: Topic status already exists')
        except kafka.errors.KafkaError as e:
            raise InternalError(f'Error while performing the call to the Kafka API while initializing', e)
        finally:
            if admin_client:
                admin_client.close()

    @staticmethod
    def prepare_execution(execution: Execution) -> str:
        if not CommunicationAdapterKafka.INITIALIZED:
            CommunicationAdapterKafka.initialize()

        # create specific execution topics
        kafka_execution_id = CommunicationAdapterKafka.__generate_kafka_execution_id(execution)
        admin_client = None
        try:
            admin_client = KafkaAdminClient(
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    client_id='orchestrator'
            )
            models_to_manager_topic = NewTopic(
                name=f'{kafka_execution_id}_models_to_manager',
                num_partitions=1,
                replication_factor=1,
                topic_configs={
                    'cleanup.policy': 'compact,delete',
                    'compression.type': 'gzip'
                }
            )
            models_to_clients_topic = NewTopic(
                name=f'{kafka_execution_id}_models_to_clients',
                num_partitions=1,
                replication_factor=1,
                topic_configs={
                    'cleanup.policy': 'compact,delete',
                    'compression.type': 'gzip'
                }
            )
            admin_client.create_topics(
                new_topics=[models_to_manager_topic, models_to_clients_topic],
                validate_only=False
            )
            return kafka_execution_id
        except kafka.errors.KafkaError as e:
            raise InternalError(f'Error while performing the call to the Kafka API while preparing a new execution', e)
        finally:
            if admin_client:
                admin_client.close()

    @staticmethod
    def finalize_execution(execution: Execution) -> None:
        # delete specific execution topics
        kafka_execution_id = CommunicationAdapterKafka.__generate_kafka_execution_id(execution)
        admin_client = None
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id='orchestrator'
            )
            admin_client.delete_topics(topics=[
                f'{kafka_execution_id}_models_to_manager',
                f'{kafka_execution_id}_models_to_clients'
            ])
        except kafka.errors.KafkaError as e:
            raise InternalError(f'Error while performing the call to the Kafka API while finalizing an execution', e)
        finally:
            if admin_client:
                admin_client.close()

    @staticmethod
    def clean_old_topics() -> None:
        admin_client = None
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id='orchestrator'
            )
            topics_list = admin_client.list_topics()
            logger.info(f'Current topics: {topics_list}')

            executions_ids = {}
            for topic in topics_list:
                if 'models_to_manager' in topic or 'models_to_clients' in topic:
                    execution_id = CommunicationAdapterKafka.__get_execution_id_from_kafka_execution_id(topic)
                    if execution_id in executions_ids:
                        executions_ids[execution_id].append(topic)
                    else:
                        executions_ids[execution_id] = [topic]

            # existent executions
            existent_executions = Execution.objects.filter(pk__in=executions_ids.keys())
            existent_executions_ids = {existent_execution.id for existent_execution in existent_executions}
            logger.info(f'Existent executions with topics: {existent_executions_ids}')
            existent_old_executions = [
                execution
                for execution in existent_executions
                if execution.get_auxiliary_elements_state().status in {ExecutionStatus.SUCCEEDED, ExecutionStatus.FAILED}
            ]
            logger.info(f'Executions with old topics: {existent_old_executions}')
            for execution in existent_old_executions:
                CommunicationAdapterKafka.finalize_execution(execution)

            # not existent executions
            topics_to_delete = []
            not_existent_executions_ids = set(executions_ids.keys()).symmetric_difference(existent_executions_ids)
            logger.info(f'Not existent executions with topics: {not_existent_executions_ids}')
            for execution_id in not_existent_executions_ids:
                topics_to_delete += executions_ids[execution_id]
            logger.info(f'Topics of not existent executions: {topics_to_delete}')
            CommunicationAdapterKafka.__delete_topics(topics_to_delete)

        except kafka.errors.KafkaError as e:
            raise InternalError(f'Error while performing the call to the Kafka API while cleaning old topics', e)
        finally:
            if admin_client:
                admin_client.close()

    # ---> Auxiliary methods

    @staticmethod
    def __generate_kafka_execution_id(execution: Execution):
        # assure not sharing of topics in debugging envs
        # kafka permitted chars -> [a-zA-Z0-9\\._\\-]
        return f'' \
               f'{execution.id}_-SEP-_' \
               f'{str(execution.created_at).replace(" ", "_").replace(":", "-").replace("+", "_")}_-SEP-_'

    @staticmethod
    def __get_execution_id_from_kafka_execution_id(kafka_execution_id: str):
        return int(kafka_execution_id.split('_-SEP-_')[0])

    @staticmethod
    def __delete_topics(topics_list: List[str]) -> None:
        admin_client = None
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id='orchestrator'
            )
            admin_client.delete_topics(topics=topics_list)
        except kafka.errors.KafkaError as e:
            raise InternalError(f'Error while performing the call to the Kafka API while finalizing an execution', e)
        finally:
            if admin_client:
                admin_client.close()
