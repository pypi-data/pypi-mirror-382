"""
事务装饰器

提供自动事务管理的装饰器，支持异常时自动回滚。
"""

import functools
from typing import Any, Callable, Optional, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession

from pyadvincekit.core.database import get_transaction, begin_transaction, commit_transaction, rollback_transaction, close_session
from pyadvincekit.logging import get_logger

logger = get_logger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def transactional(
    auto_commit: bool = True,
    rollback_on_exception: bool = True,
    session_param: str = "session"
) -> Callable[[F], F]:
    """
    事务装饰器
    
    Args:
        auto_commit: 是否自动提交事务
        rollback_on_exception: 异常时是否自动回滚
        session_param: 会话参数名称
        
    Returns:
        装饰后的函数
    """
    def decorator(func: F) -> F:
        if hasattr(func, '__call__') and hasattr(func, '__code__'):
            # 检查函数是否已经有session参数
            param_names = func.__code__.co_varnames[:func.__code__.co_argcount]
            has_session_param = session_param in param_names
        else:
            has_session_param = False
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 如果函数已经有session参数且传入了session，直接调用
            if has_session_param and session_param in kwargs:
                return await func(*args, **kwargs)
            
            # 否则创建新的事务
            session = None
            try:
                session = await begin_transaction()
                
                # 将session添加到参数中
                if has_session_param:
                    kwargs[session_param] = session
                
                result = await func(*args, **kwargs)
                
                if auto_commit:
                    await commit_transaction(session)
                
                return result
                
            except Exception as e:
                if session and rollback_on_exception:
                    try:
                        await rollback_transaction(session)
                        logger.info(f"Transaction rolled back due to exception: {e}")
                    except Exception as rollback_error:
                        logger.error(f"Failed to rollback transaction: {rollback_error}")
                
                raise e
                
            finally:
                if session:
                    await close_session(session)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 同步函数不支持事务装饰器
            raise RuntimeError("Transaction decorator only supports async functions")
        
        # 检查函数是否为异步函数
        if hasattr(func, '__code__') and hasattr(func.__code__, 'co_flags'):
            # CO_ITERABLE_COROUTINE = 0x0100
            if func.__code__.co_flags & 0x0080:  # CO_COROUTINE
                return async_wrapper
        
        return sync_wrapper
    
    return decorator


def transactional_method(
    auto_commit: bool = True,
    rollback_on_exception: bool = True
) -> Callable[[F], F]:
    """
    事务方法装饰器（用于类方法）
    
    Args:
        auto_commit: 是否自动提交事务
        rollback_on_exception: 异常时是否自动回滚
        
    Returns:
        装饰后的方法
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            session = None
            try:
                session = await begin_transaction()
                
                # 将session作为第一个参数传递
                result = await func(self, session, *args, **kwargs)
                
                if auto_commit:
                    await commit_transaction(session)
                
                return result
                
            except Exception as e:
                if session and rollback_on_exception:
                    try:
                        await rollback_transaction(session)
                        logger.info(f"Transaction rolled back due to exception: {e}")
                    except Exception as rollback_error:
                        logger.error(f"Failed to rollback transaction: {rollback_error}")
                
                raise e
                
            finally:
                if session:
                    await close_session(session)
        
        return async_wrapper
    
    return decorator


class TransactionContext:
    """事务上下文管理器"""
    
    def __init__(self, auto_commit: bool = True):
        self.auto_commit = auto_commit
        self.session: Optional[AsyncSession] = None
    
    async def __aenter__(self) -> AsyncSession:
        self.session = await begin_transaction()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            try:
                if exc_type is None and self.auto_commit:
                    await commit_transaction(self.session)
                else:
                    await rollback_transaction(self.session)
                    if exc_type:
                        logger.info(f"Transaction rolled back due to exception: {exc_val}")
            except Exception as e:
                logger.error(f"Error in transaction cleanup: {e}")
            finally:
                await close_session(self.session)


# 便捷函数
def transaction_context(auto_commit: bool = True) -> TransactionContext:
    """创建事务上下文管理器"""
    return TransactionContext(auto_commit=auto_commit)


# 使用示例：
"""
# 1. 装饰器方式
@transactional()
async def create_user_and_profile(user_data: dict, profile_data: dict, session: AsyncSession):
    user = await user_crud.create(session, user_data)
    profile_data['user_id'] = user.id
    profile = await profile_crud.create(session, profile_data)
    return user, profile

# 2. 上下文管理器方式
async def create_user_and_profile(user_data: dict, profile_data: dict):
    async with transaction_context() as session:
        user = await user_crud.create(session, user_data)
        profile_data['user_id'] = user.id
        profile = await profile_crud.create(session, profile_data)
        return user, profile

# 3. 手动管理方式
async def create_user_and_profile(user_data: dict, profile_data: dict):
    session = await begin_transaction()
    try:
        user = await user_crud.create(session, user_data)
        profile_data['user_id'] = user.id
        profile = await profile_crud.create(session, profile_data)
        await commit_transaction(session)
        return user, profile
    except Exception:
        await rollback_transaction(session)
        raise
    finally:
        await close_session(session)
"""









