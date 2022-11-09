from django.conf import settings

from main.container_manager.container_manager_interface import ContainerManagerInterface
from main.container_manager.types.dummy import ContainerManagerDummy
from main.container_manager.types.dummy_with_kafka import ContainerManagerDummyWithKafka
from main.container_manager.types.kubernetes.kubernetes import ContainerManagerKubernetes
from main.platform_adapter.platform_adapter_interface import PlatformAdapterInterface
from main.platform_adapter.types.dummy import DummyPlatformAdapter
from main.platform_adapter.types.maas import MaaSPlatformAdapter


class Factory:

    def __init__(self):
        raise Exception('This static class can not be instantiated')

    @staticmethod
    def get_platform_adapter() -> PlatformAdapterInterface.__class__:
        if settings.PLATFORM_ADAPTER == 'maas':
            return MaaSPlatformAdapter
        elif settings.PLATFORM_ADAPTER == 'dummy':
            return DummyPlatformAdapter
        else:
            raise Exception(f'Platform adapter implementation {settings.PLATFORM_ADAPTER} does not exist')

    @staticmethod
    def get_container_manager() -> ContainerManagerInterface.__class__:
        if settings.CONTAINER_MANAGER == 'kubernetes':
            return ContainerManagerKubernetes
        elif settings.CONTAINER_MANAGER == 'dummy':
            return ContainerManagerDummy
        elif settings.CONTAINER_MANAGER == 'dummy_kafka':
            return ContainerManagerDummyWithKafka
        else:
            raise Exception(f'Container manager implementation {settings.CONTAINER_MANAGER} does not exist')
