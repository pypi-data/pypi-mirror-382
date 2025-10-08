from elasticsearch import AsyncElasticsearch, Elasticsearch
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from pymongo import MongoClient
from redis.asyncio import Redis as AsyncRedis
from redis import Redis as SyncRedis
from sqlalchemy.engine import create_engine as create_sync_engine, Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from typing import Generic, Literal, Optional, TypeVar, Union, overload
from maleo.types.dict import StringToAnyDict
from ..enums import Connection
from .additional import AdditionalConfigT, RedisAdditionalConfig
from .connection import (
    ConnectionConfigT,
    PostgreSQLConnectionConfig,
    MySQLConnectionConfig,
    SQLiteConnectionConfig,
    SQLServerConnectionConfig,
    MongoConnectionConfig,
    RedisConnectionConfig,
    ElasticsearchConnectionConfig,
)
from .identifier import DatabaseIdentifierConfig
from .pooling import (
    PoolingConfigT,
    PostgreSQLPoolingConfig,
    MySQLPoolingConfig,
    SQLitePoolingConfig,
    SQLServerPoolingConfig,
    MongoPoolingConfig,
    RedisPoolingConfig,
    ElasticsearchPoolingConfig,
)


class BaseConfig(
    BaseModel, Generic[ConnectionConfigT, PoolingConfigT, AdditionalConfigT]
):
    """Base configuration for database."""

    identifier: DatabaseIdentifierConfig = Field(..., description="Identifier config")
    connection: ConnectionConfigT = Field(..., description="Connection config")
    pooling: PoolingConfigT = Field(..., description="Pooling config")
    additional: AdditionalConfigT = Field(..., description="Additional config")


class MySQLConfig(
    BaseConfig[
        MySQLConnectionConfig,
        MySQLPoolingConfig,
        None,
    ]
):
    additional: None = None

    @property
    def engine_kwargs(self) -> StringToAnyDict:
        return {
            **self.connection.engine_kwargs,
            **self.pooling.engine_kwargs,
        }

    @overload
    def create_engine(self, connection: Literal[Connection.ASYNC]) -> AsyncEngine: ...
    @overload
    def create_engine(self, connection: Literal[Connection.SYNC]) -> Engine: ...
    def create_engine(self, connection: Connection) -> Union[AsyncEngine, Engine]:
        url = self.connection.make_url(connection)
        if connection is Connection.ASYNC:
            return create_async_engine(url, **self.engine_kwargs)
        elif connection is Connection.SYNC:
            return create_sync_engine(url, **self.engine_kwargs)


class PostgreSQLConfig(
    BaseConfig[
        PostgreSQLConnectionConfig,
        PostgreSQLPoolingConfig,
        None,
    ]
):
    additional: None = None

    @property
    def engine_kwargs(self) -> StringToAnyDict:
        return {
            **self.connection.engine_kwargs,
            **self.pooling.engine_kwargs,
        }

    @overload
    def create_engine(self, connection: Literal[Connection.ASYNC]) -> AsyncEngine: ...
    @overload
    def create_engine(self, connection: Literal[Connection.SYNC]) -> Engine: ...
    def create_engine(self, connection: Connection) -> Union[AsyncEngine, Engine]:
        url = self.connection.make_url(connection)
        if connection is Connection.ASYNC:
            return create_async_engine(url, **self.engine_kwargs)
        elif connection is Connection.SYNC:
            return create_sync_engine(url, **self.engine_kwargs)


class SQLiteConfig(
    BaseConfig[
        SQLiteConnectionConfig,
        SQLitePoolingConfig,
        None,
    ]
):
    additional: None = None

    @property
    def engine_kwargs(self) -> StringToAnyDict:
        return {
            **self.connection.engine_kwargs,
            **self.pooling.engine_kwargs,
        }

    @overload
    def create_engine(self, connection: Literal[Connection.ASYNC]) -> AsyncEngine: ...
    @overload
    def create_engine(self, connection: Literal[Connection.SYNC]) -> Engine: ...
    def create_engine(self, connection: Connection) -> Union[AsyncEngine, Engine]:
        url = self.connection.make_url(connection)
        if connection is Connection.ASYNC:
            return create_async_engine(url, **self.engine_kwargs)
        elif connection is Connection.SYNC:
            return create_sync_engine(url, **self.engine_kwargs)


class SQLServerConfig(
    BaseConfig[
        SQLServerConnectionConfig,
        SQLServerPoolingConfig,
        None,
    ]
):
    additional: None = None

    @property
    def engine_kwargs(self) -> StringToAnyDict:
        return {
            **self.connection.engine_kwargs,
            **self.pooling.engine_kwargs,
        }

    @overload
    def create_engine(self, connection: Literal[Connection.ASYNC]) -> AsyncEngine: ...
    @overload
    def create_engine(self, connection: Literal[Connection.SYNC]) -> Engine: ...
    def create_engine(self, connection: Connection) -> Union[AsyncEngine, Engine]:
        url = self.connection.make_url(connection)
        if connection is Connection.ASYNC:
            return create_async_engine(url, **self.engine_kwargs)
        elif connection is Connection.SYNC:
            return create_sync_engine(url, **self.engine_kwargs)


SQLConfigT = TypeVar(
    "SQLConfigT",
    PostgreSQLConfig,
    MySQLConfig,
    SQLiteConfig,
    SQLServerConfig,
)


class ElasticsearchConfig(
    BaseConfig[
        ElasticsearchConnectionConfig,
        ElasticsearchPoolingConfig,
        None,
    ]
):
    additional: None = None

    @property
    def client_kwargs(self) -> StringToAnyDict:
        client_kwargs = {}

        if self.connection.username and self.connection.password:
            client_kwargs["http_auth"] = (
                self.connection.username,
                self.connection.password,
            )

        client_kwargs.update(self.pooling.client_kwargs)

        return client_kwargs

    @overload
    def create_client(
        self, connection: Literal[Connection.ASYNC]
    ) -> AsyncElasticsearch: ...
    @overload
    def create_client(self, connection: Literal[Connection.SYNC]) -> Elasticsearch: ...
    def create_client(
        self, connection: Connection
    ) -> Union[AsyncElasticsearch, Elasticsearch]:
        hosts = [{"host": self.connection.host, "port": self.connection.port}]
        if connection is Connection.ASYNC:
            return AsyncElasticsearch(hosts, **self.client_kwargs)
        else:
            return Elasticsearch(hosts, **self.client_kwargs)


class MongoConfig(
    BaseConfig[
        MongoConnectionConfig,
        MongoPoolingConfig,
        None,
    ]
):
    additional: None = None

    @property
    def client_kwargs(self) -> StringToAnyDict:
        return self.pooling.client_kwargs

    @overload
    def create_client(
        self, connection: Literal[Connection.ASYNC]
    ) -> AsyncIOMotorClient: ...
    @overload
    def create_client(self, connection: Literal[Connection.SYNC]) -> MongoClient: ...
    def create_client(
        self, connection: Connection
    ) -> Union[AsyncIOMotorClient, MongoClient]:
        url = self.connection.make_url(connection)
        if connection is Connection.ASYNC:
            return AsyncIOMotorClient(url, **self.client_kwargs)
        else:
            return MongoClient(url, **self.client_kwargs)


class RedisConfig(
    BaseConfig[
        RedisConnectionConfig,
        RedisPoolingConfig,
        RedisAdditionalConfig,
    ]
):
    additional: RedisAdditionalConfig = Field(..., description="Additional config")

    @property
    def client_kwargs(self) -> StringToAnyDict:
        return self.pooling.client_kwargs

    @overload
    def create_client(self, connection: Literal[Connection.ASYNC]) -> AsyncRedis: ...
    @overload
    def create_client(self, connection: Literal[Connection.SYNC]) -> SyncRedis: ...
    def create_client(self, connection: Connection) -> Union[AsyncRedis, SyncRedis]:
        url = self.connection.make_url(connection)
        if connection is Connection.ASYNC:
            return AsyncRedis.from_url(url, **self.client_kwargs)
        else:
            return SyncRedis.from_url(url, **self.client_kwargs)


NoSQLConfigT = TypeVar(
    "NoSQLConfigT",
    ElasticsearchConfig,
    MongoConfig,
    RedisConfig,
)


ConfigT = TypeVar(
    "ConfigT",
    ElasticsearchConfig,
    MongoConfig,
    RedisConfig,
    MySQLConfig,
    PostgreSQLConfig,
    SQLiteConfig,
    SQLServerConfig,
)


class ElasticsearchConfigs(BaseModel):
    primary: ElasticsearchConfig = Field(
        ..., description="Primary Elasticsearch config"
    )


ElasticsearchConfigsT = TypeVar(
    "ElasticsearchConfigsT", bound=Optional[ElasticsearchConfigs]
)


class MongoConfigs(BaseModel):
    primary: MongoConfig = Field(..., description="Primary Mongo config")


MongoConfigsT = TypeVar("MongoConfigsT", bound=Optional[MongoConfigs])


class RedisConfigs(BaseModel):
    primary: RedisConfig = Field(..., description="Primary Redis config")


RedisConfigsT = TypeVar("RedisConfigsT", bound=Optional[RedisConfigs])


class NoSQLConfigs(
    BaseModel, Generic[ElasticsearchConfigsT, MongoConfigsT, RedisConfigsT]
):
    elasticsearch: ElasticsearchConfigsT = Field(
        ..., description="Elasticsearch configs"
    )
    mongo: MongoConfigsT = Field(..., description="Mongo configs")
    redis: RedisConfigsT = Field(..., description="Redis configs")


NoSQLConfigsT = TypeVar("NoSQLConfigsT", bound=Optional[NoSQLConfigs])


class MySQLConfigs(BaseModel):
    primary: MySQLConfig = Field(..., description="Primary MySQL config")


MySQLConfigsT = TypeVar("MySQLConfigsT", bound=Optional[MySQLConfigs])


class PostgreSQLConfigs(BaseModel):
    primary: PostgreSQLConfig = Field(..., description="Primary PostgreSQL config")


PostgreSQLConfigsT = TypeVar("PostgreSQLConfigsT", bound=Optional[PostgreSQLConfigs])


class SQLiteConfigs(BaseModel):
    primary: SQLiteConfig = Field(..., description="Primary SQLite config")


SQLiteConfigsT = TypeVar("SQLiteConfigsT", bound=Optional[SQLiteConfigs])


class SQLServerConfigs(BaseModel):
    primary: SQLServerConfig = Field(..., description="Primary SQLServer config")


SQLServerConfigsT = TypeVar("SQLServerConfigsT", bound=Optional[SQLServerConfigs])


class SQLConfigs(
    BaseModel,
    Generic[
        MySQLConfigsT,
        PostgreSQLConfigsT,
        SQLiteConfigsT,
        SQLServerConfigsT,
    ],
):
    mysql: MySQLConfigsT = Field(..., description="MySQL configs")
    postgresql: PostgreSQLConfigsT = Field(..., description="PostgreSQL configs")
    sqlite: SQLiteConfigsT = Field(..., description="SQLite configs")
    sqlserver: SQLServerConfigsT = Field(..., description="SQLServer configs")


SQLConfigsT = TypeVar("SQLConfigsT", bound=Optional[SQLConfigs])


class Configs(
    BaseModel,
    Generic[
        NoSQLConfigsT,
        SQLConfigsT,
    ],
):
    nosql: NoSQLConfigsT = Field(..., description="NoSQL configs")
    sql: SQLConfigsT = Field(..., description="SQL configs")


ConfigsT = TypeVar("ConfigsT", bound=Optional[Configs])


class ConfigsMixin(BaseModel, Generic[ConfigsT]):
    database: ConfigsT = Field(..., description="Database configs")
