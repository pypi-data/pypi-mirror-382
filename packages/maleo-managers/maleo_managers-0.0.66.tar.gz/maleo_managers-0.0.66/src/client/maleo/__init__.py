from abc import ABC, abstractmethod
from Crypto.PublicKey.RSA import RsaKey
from typing import Generic
from maleo.database.enums import CacheOrigin, CacheLayer
from maleo.database.handlers import RedisHandler
from maleo.enums.environment import Environment
from maleo.enums.service import Key as ServiceKey
from maleo.logging.config import Config as LogConfig
from maleo.logging.logger import Client
from maleo.schemas.application import ApplicationContext
from maleo.schemas.operation.context import generate
from maleo.schemas.operation.enums import Origin, Layer, Target
from maleo.schemas.resource import Resource, AggregateField
from ..http import HTTPClientManager
from .config import AnyMaleoClientConfigT


class MaleoClientService(Generic[AnyMaleoClientConfigT]):
    resource: Resource

    def __init__(
        self,
        *,
        application_context: ApplicationContext,
        config: AnyMaleoClientConfigT,
        logger: Client,
        http_client_manager: HTTPClientManager,
        private_key: RsaKey,
        redis: RedisHandler,
    ):
        self._application_context = application_context
        self._config = config
        self._logger = logger
        self._http_client_manager = http_client_manager
        self._private_key = private_key
        self._redis = redis

        self._namespace = self._redis.config.additional.build_namespace(
            self.resource.aggregate(AggregateField.KEY),
            use_self_base=True,
            client=self._config.key,
            origin=CacheOrigin.CLIENT,
            layer=CacheLayer.SERVICE,
        )

        self._operation_context = generate(
            origin=Origin.CLIENT, layer=Layer.SERVICE, target=Target.INTERNAL
        )


class MaleoClientManager(ABC, Generic[AnyMaleoClientConfigT]):
    def __init__(
        self,
        *,
        application_context: ApplicationContext,
        config: AnyMaleoClientConfigT,
        log_config: LogConfig,
        private_key: RsaKey,
        redis: RedisHandler,
    ):
        self._application_context = application_context
        self._config = config
        self._log_config = log_config

        self._key = self._config.key
        self._name = self._config.name

        self._logger = Client[Environment, ServiceKey](
            environment=self._application_context.environment,
            service_key=self._application_context.key,
            client_key=self._key,
            config=log_config,
        )

        self._http_client_manager = HTTPClientManager()
        self._private_key = private_key
        self._redis = redis

        self.initalize_services()
        self._logger.info(f"{self._name} client manager initialized successfully")

    @abstractmethod
    def initalize_services(self):
        """Initialize all services of this client"""
