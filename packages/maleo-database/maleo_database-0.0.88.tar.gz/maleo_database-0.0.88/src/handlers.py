from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, Generic, Optional, TypeVar
from .config import (
    ElasticsearchConfig,
    MongoConfig,
    RedisConfig,
    MySQLConfig,
    PostgreSQLConfig,
    SQLiteConfig,
    SQLServerConfig,
    DatabaseConfigT,
)
from .managers import (
    ElasticsearchManager,
    MongoManager,
    RedisManager,
    MySQLManager,
    PostgreSQLManager,
    SQLiteManager,
    SQLServerManager,
    DatabaseManagerT,
)
from .types import DeclarativeBaseT


class Handler(
    BaseModel,
    Generic[
        DatabaseConfigT,
        DatabaseManagerT,
    ],
):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    config: Annotated[DatabaseConfigT, Field(..., description="Config")]
    manager: Annotated[DatabaseManagerT, Field(..., description="Manager")]


HandlerT = TypeVar("HandlerT", bound=Handler)


class ElasticsearchHandler(Handler[ElasticsearchConfig, ElasticsearchManager]):
    pass


class MongoHandler(Handler[MongoConfig, MongoManager]):
    pass


class RedisHandler(Handler[RedisConfig, RedisManager]):
    pass


class MySQLHandler(
    Handler[MySQLConfig, MySQLManager[DeclarativeBaseT]], Generic[DeclarativeBaseT]
):
    pass


class PostgreSQLHandler(
    Handler[PostgreSQLConfig, PostgreSQLManager[DeclarativeBaseT]],
    Generic[DeclarativeBaseT],
):
    pass


class SQLiteHandler(
    Handler[SQLiteConfig, SQLiteManager[DeclarativeBaseT]], Generic[DeclarativeBaseT]
):
    pass


class SQLServerHandler(
    Handler[SQLServerConfig, SQLServerManager[DeclarativeBaseT]],
    Generic[DeclarativeBaseT],
):
    pass


class BaseHandlers(BaseModel, Generic[HandlerT]):
    primary: Annotated[HandlerT, Field(..., description="Primary handler")]


BaseHandlersT = TypeVar("BaseHandlersT", bound=Optional[BaseHandlers])


class ElasticsearchHandlers(BaseHandlers[ElasticsearchHandler]):
    pass


ElasticsearchHandlersT = TypeVar(
    "ElasticsearchHandlersT", bound=Optional[ElasticsearchHandlers]
)


class MongoHandlers(BaseHandlers[MongoHandler]):
    pass


MongoHandlersT = TypeVar("MongoHandlersT", bound=Optional[MongoHandlers])


class RedisHandlers(BaseHandlers[RedisHandler]):
    pass


RedisHandlersT = TypeVar("RedisHandlersT", bound=Optional[RedisHandlers])


class NoSQLHandlers(
    BaseModel, Generic[ElasticsearchHandlersT, MongoHandlersT, RedisHandlersT]
):
    elasticsearch: Annotated[
        ElasticsearchHandlersT, Field(..., description="Elasticsearch handlers")
    ]
    mongo: Annotated[MongoHandlersT, Field(..., description="Mongo handlers")]
    redis: Annotated[RedisHandlersT, Field(..., description="Redis handlers")]


NoSQLHandlersT = TypeVar("NoSQLHandlersT", bound=Optional[NoSQLHandlers])


class MySQLHandlers(
    BaseHandlers[MySQLHandler[DeclarativeBaseT]], Generic[DeclarativeBaseT]
):
    pass


MySQLHandlersT = TypeVar("MySQLHandlersT", bound=Optional[MySQLHandlers])


class PostgreSQLHandlers(
    BaseHandlers[PostgreSQLHandler[DeclarativeBaseT]], Generic[DeclarativeBaseT]
):
    pass


PostgreSQLHandlersT = TypeVar("PostgreSQLHandlersT", bound=Optional[PostgreSQLHandlers])


class SQLiteHandlers(
    BaseHandlers[SQLiteHandler[DeclarativeBaseT]], Generic[DeclarativeBaseT]
):
    pass


SQLiteHandlersT = TypeVar("SQLiteHandlersT", bound=Optional[SQLiteHandlers])


class SQLServerHandlers(
    BaseHandlers[SQLServerHandler[DeclarativeBaseT]], Generic[DeclarativeBaseT]
):
    pass


SQLServerHandlersT = TypeVar("SQLServerHandlersT", bound=Optional[SQLServerHandlers])


class SQLHandlers(
    BaseModel,
    Generic[
        MySQLHandlersT,
        PostgreSQLHandlersT,
        SQLiteHandlersT,
        SQLServerHandlersT,
    ],
):
    mysql: Annotated[MySQLHandlersT, Field(..., description="MySQL handlers")]
    postgresql: Annotated[
        PostgreSQLHandlersT, Field(..., description="PostgreSQL handlers")
    ]
    sqlite: Annotated[SQLiteHandlersT, Field(..., description="SQLite handlers")]
    sqlserver: Annotated[
        SQLServerHandlersT, Field(..., description="SQLServer handlers")
    ]


SQLHandlersT = TypeVar("SQLHandlersT", bound=Optional[SQLHandlers])


class DatabaseHandlers(
    BaseModel,
    Generic[
        NoSQLHandlersT,
        SQLHandlersT,
    ],
):
    nosql: Annotated[NoSQLHandlersT, Field(..., description="NoSQL handlers")]
    sql: Annotated[SQLHandlersT, Field(..., description="SQL handlers")]


DatabaseHandlersT = TypeVar("DatabaseHandlersT", bound=Optional[DatabaseHandlers])
