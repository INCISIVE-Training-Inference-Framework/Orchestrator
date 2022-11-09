import abc
import logging

import kafka.errors
from django.conf import settings
from kafka.admin import KafkaAdminClient, NewTopic

from main.domain.exceptions import InternalError

logger = logging.getLogger(__name__)

if settings.CONTAINER_MANAGER == 'dummy_kafka' or \
        (settings.CONTAINER_MANAGER == 'kubernetes' and settings.COMMUNICATION_ADAPTER == 'kafka'):
    bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
    max_model_size = f'{settings.KAFKA_MAX_MODEL_SIZE}000'


class CommunicationAdapterKafka(metaclass=abc.ABCMeta):

    def __init__(self):
        raise Exception('This static class can not be instantiated')

    # ---> Main methods

    @staticmethod
    def initialize() -> None:
        logger.info('Initializing kafka')

        # create general topic
        admin_client = None
        try:
            admin_client = KafkaAdminClient(
                    bootstrap_servers=bootstrap_servers,
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
        except kafka.errors.TopicAlreadyExistsError:
            logger.warning('Warning: Topic status already exists')
        except kafka.errors.KafkaError as e:
            raise InternalError(
                f'Error while performing the call to the Kafka API while initializing: {e}',
                None
            )
        finally:
            if admin_client:
                admin_client.close()

    @staticmethod
    def prepare_execution(execution_id: str) -> None:
        # create specific execution topics
        admin_client = None
        try:
            admin_client = KafkaAdminClient(
                    bootstrap_servers=bootstrap_servers,
                    client_id='orchestrator'
            )
            models_to_manager_topic = NewTopic(
                name=execution_id + '_models_to_manager',
                num_partitions=1,
                replication_factor=1,
                topic_configs={
                    'cleanup.policy': 'compact,delete',
                    'compression.type': 'gzip',
                    'max.message.bytes': max_model_size
                }
            )
            models_to_clients_topic = NewTopic(
                name=execution_id + '_models_to_clients',
                num_partitions=1,
                replication_factor=1,
                topic_configs={
                    'cleanup.policy': 'compact,delete',
                    'compression.type': 'gzip',
                    'max.message.bytes': max_model_size
                }
            )
            admin_client.create_topics(
                new_topics=[models_to_manager_topic, models_to_clients_topic],
                validate_only=False
            )
        except kafka.errors.KafkaError as e:
            raise InternalError(
                f'Error while performing the call to the Kafka API while preparing a new execution: {e}',
                None
            )
        finally:
            if admin_client:
                admin_client.close()

    @staticmethod
    def finalize_execution(execution_id: str) -> None:
        # delete specific execution topics
        admin_client = None
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=bootstrap_servers,
                client_id='orchestrator'
            )
            admin_client.delete_topics(topics=[
                execution_id + '_models_to_manager',
                execution_id + '_models_to_clients'
            ])
        except kafka.errors.KafkaError as e:
            raise InternalError(
                f'Error while performing the call to the Kafka API while finalizing an execution: {e}',
                None
            )
        finally:
            if admin_client:
                admin_client.close()
