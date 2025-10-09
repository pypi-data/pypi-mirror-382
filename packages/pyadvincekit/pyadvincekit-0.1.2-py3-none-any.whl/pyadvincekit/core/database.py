"""
数据库连接和会话管理模块

提供异步数据库连接、会话管理、连接池配置等功能。
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from pyadvincekit.core.config import Settings, get_settings
from pyadvincekit.core.exceptions import DatabaseConnectionError, DatabaseError
from pyadvincekit.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    def _create_engine(self) -> AsyncEngine:
        """创建数据库引擎"""
        database_url = self.settings.get_database_url(async_driver=True)
        
        # 基础引擎配置
        engine_kwargs = {
            "url": database_url,
            "echo": self.settings.database_echo_sql,
            "pool_pre_ping": self.settings.database_pool_pre_ping,
            "pool_recycle": self.settings.database_pool_recycle,
        }

        # 根据数据库类型调整配置
        if "sqlite" in database_url:
            # SQLite 特殊配置
            engine_kwargs.update({
                "poolclass": StaticPool,
                "connect_args": {
                    "check_same_thread": False,
                },
            })
        else:
            # PostgreSQL/MySQL 连接池配置
            engine_kwargs.update({
                "pool_size": self.settings.database_pool_size,
                "max_overflow": self.settings.database_max_overflow,
            })

        try:
            engine = create_async_engine(**engine_kwargs)
            logger.info(f"数据库引擎创建成功: {database_url}")
            return engine
        except Exception as e:
            logger.error(f"数据库引擎创建失败: {e}")
            raise DatabaseConnectionError(f"Failed to create database engine: {e}")

    def _setup_engine_events(self, engine: AsyncEngine) -> None:
        """设置数据库引擎事件监听"""
        
        @event.listens_for(engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """SQLite特殊配置"""
            if "sqlite" in str(engine.url):
                try:
                    # 对于异步SQLite，需要特殊处理
                    if hasattr(dbapi_connection, 'execute'):
                        # 启用外键约束
                        dbapi_connection.execute("PRAGMA foreign_keys=ON")
                        # 设置WAL模式以提高并发性能
                        dbapi_connection.execute("PRAGMA journal_mode=WAL")
                        # 设置同步模式
                        dbapi_connection.execute("PRAGMA synchronous=NORMAL")
                        # 设置缓存大小
                        dbapi_connection.execute("PRAGMA cache_size=10000")
                    else:
                        # 传统同步方式
                        cursor = dbapi_connection.cursor()
                        cursor.execute("PRAGMA foreign_keys=ON")
                        cursor.execute("PRAGMA journal_mode=WAL")
                        cursor.execute("PRAGMA synchronous=NORMAL")
                        cursor.execute("PRAGMA cache_size=10000")
                        cursor.close()
                except Exception as e:
                    logger.warning(f"Failed to set SQLite pragma: {e}")

        @event.listens_for(engine.sync_engine, "checkout")
        def checkout_event(dbapi_connection, connection_record, connection_proxy):
            """连接检出事件"""
            logger.debug("数据库连接已检出")

        @event.listens_for(engine.sync_engine, "checkin")
        def checkin_event(dbapi_connection, connection_record):
            """连接归还事件"""
            logger.debug("数据库连接已归还")

    @property
    def engine(self) -> AsyncEngine:
        """获取数据库引擎"""
        if self._engine is None:
            self._engine = self._create_engine()
            self._setup_engine_events(self._engine)
        return self._engine

    @property 
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """获取会话工厂"""
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
            )
        return self._session_factory

    async def create_all_tables(self) -> None:
        """创建所有表（开发环境使用）"""
        try:
            # 导入所有模型，确保表结构被注册
            from pyadvincekit.models.base import Base
            
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("数据库表创建成功")
        except Exception as e:
            logger.error(f"数据库表创建失败: {e}")
            raise DatabaseError(f"Failed to create tables: {e}")

    async def drop_all_tables(self) -> None:
        """删除所有表（测试环境使用）"""
        try:
            from pyadvincekit.models.base import Base
            
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("数据库表删除成功")
        except Exception as e:
            logger.error(f"数据库表删除失败: {e}")
            raise DatabaseError(f"Failed to drop tables: {e}")

    async def check_connection(self) -> bool:
        """检查数据库连接"""
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("数据库连接检查成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接检查失败: {e}")
            return False

    async def close(self) -> None:
        """关闭数据库连接"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("数据库连接已关闭")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话（上下文管理器）"""
        session = self.session_factory()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库会话异常，已回滚: {e}")
            raise DatabaseError(f"Database session error: {e}")
        finally:
            await session.close()

    async def execute_raw_sql(self, sql: str, params: Optional[dict] = None) -> any:
        """执行原生SQL"""
        try:
            async with self.get_session() as session:
                result = await session.execute(text(sql), params or {})
                await session.commit()
                return result
        except Exception as e:
            logger.error(f"原生SQL执行失败: {sql}, 错误: {e}")
            raise DatabaseError(f"Failed to execute raw SQL: {e}")

    # 事务管理方法
    async def begin_transaction(self) -> AsyncSession:
        """开始一个新事务，返回会话对象"""
        session = self.session_factory()
        try:
            await session.begin()
            logger.debug("数据库事务已开始")
            return session
        except Exception as e:
            await session.close()
            logger.error(f"开始事务失败: {e}")
            raise DatabaseError(f"Failed to begin transaction: {e}")

    async def commit_transaction(self, session: AsyncSession) -> None:
        """提交事务"""
        try:
            await session.commit()
            logger.debug("数据库事务已提交")
        except Exception as e:
            logger.error(f"提交事务失败: {e}")
            raise DatabaseError(f"Failed to commit transaction: {e}")

    async def rollback_transaction(self, session: AsyncSession) -> None:
        """回滚事务"""
        try:
            await session.rollback()
            logger.debug("数据库事务已回滚")
        except Exception as e:
            logger.error(f"回滚事务失败: {e}")
            raise DatabaseError(f"Failed to rollback transaction: {e}")

    async def close_session(self, session: AsyncSession) -> None:
        """关闭会话"""
        try:
            await session.close()
            logger.debug("数据库会话已关闭")
        except Exception as e:
            logger.error(f"关闭会话失败: {e}")
            # 这里不抛出异常，因为关闭失败通常不是致命错误

    @asynccontextmanager
    async def get_transaction(self) -> AsyncGenerator[AsyncSession, None]:
        """获取事务会话（上下文管理器）"""
        session = await self.begin_transaction()
        try:
            yield session
            await self.commit_transaction(session)
        except Exception as e:
            await self.rollback_transaction(session)
            logger.error(f"事务执行异常，已回滚: {e}")
            raise
        finally:
            await self.close_session(session)


# 全局数据库管理器实例
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def set_database_manager(manager: DatabaseManager) -> None:
    """设置数据库管理器实例（主要用于测试）"""
    global _db_manager
    _db_manager = manager


def reset_database_manager() -> None:
    """重置数据库管理器实例（用于重新加载配置后）"""
    global _db_manager
    if _db_manager is not None:
        # 关闭旧的连接
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，创建一个任务来关闭
                asyncio.create_task(_db_manager.close())
            else:
                # 如果事件循环没有运行，直接运行
                asyncio.run(_db_manager.close())
        except Exception:
            pass  # 忽略关闭时的错误
    _db_manager = None


@asynccontextmanager
async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的便捷函数"""
    manager = get_database_manager()
    async with manager.get_session() as session:
        yield session


async def init_database() -> None:
    """初始化数据库（创建表等）"""
    manager = get_database_manager()
    await manager.create_all_tables()


async def close_database() -> None:
    """关闭数据库连接"""
    manager = get_database_manager()
    await manager.close()


async def check_database_health() -> bool:
    """检查数据库健康状态"""
    manager = get_database_manager()
    return await manager.check_connection()


# 事务管理便捷函数
async def begin_transaction() -> AsyncSession:
    """开始一个新事务"""
    manager = get_database_manager()
    return await manager.begin_transaction()


async def commit_transaction(session: AsyncSession) -> None:
    """提交事务"""
    manager = get_database_manager()
    await manager.commit_transaction(session)


async def rollback_transaction(session: AsyncSession) -> None:
    """回滚事务"""
    manager = get_database_manager()
    await manager.rollback_transaction(session)


async def close_session(session: AsyncSession) -> None:
    """关闭会话"""
    manager = get_database_manager()
    await manager.close_session(session)


@asynccontextmanager
async def get_transaction() -> AsyncGenerator[AsyncSession, None]:
    """获取事务会话（便捷函数）"""
    manager = get_database_manager()
    async with manager.get_transaction() as session:
        yield session


# 兼容性函数，用于依赖注入
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI依赖注入用的数据库会话获取函数"""
    async with get_database() as session:
        yield session
