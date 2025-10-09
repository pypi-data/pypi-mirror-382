#!/usr/bin/env python3
"""
账务登记表 API 接口（手动定义方式）

手动定义接口，提供更精细的控制和自定义业务逻辑
"""

import sys
from pathlib import Path

# PyAdvanceKit Admin Backend 的标准做法
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import APIRouter, HTTPException, status
from pyadvincekit.core.response import success_response, error_response
from pyadvincekit.logging import get_logger

from services.acct_book_service import AcctBookService
from schemas.t_mntx_acct_book import (
    TMntxAcctBookCreate, TMntxAcctBookUpdate, TMntxAcctBookQuery, TMntxAcctBookFilter
)

# 创建路由
acct_book_manual_router = APIRouter(
    prefix="/api/acct-book/manual",
    tags=["账务登记（手动定义）"]
)

# 实例化服务
service = AcctBookService()
logger = get_logger(__name__)

# === 标准 CRUD 接口 ===

@acct_book_manual_router.post("/create")
async def create_acct_book(data: TMntxAcctBookCreate):
    """
    创建账务登记
    
    - **PLAT_SEQ**: 平台流水（必需，唯一）
    - **BUSI_NO**: 业务编号（必需）
    - **AMT**: 金额（必需，大于0）
    - **CURR**: 币种（建议填写）
    """
    logger.info(f"创建账务登记请求: PLAT_SEQ={data.PLAT_SEQ}")
    return await service.create_acct_book(data)

@acct_book_manual_router.post("/get")
async def get_acct_book(request: dict):
    """
    获取单个账务登记
    
    请求体格式:
    ```json
    {"id": "record_uuid"}
    ```
    """
    record_id = request.get("id")
    if not record_id:
        return error_response(message="记录ID不能为空", code="400001")
    
    logger.info(f"查询账务登记: ID={record_id}")
    return await service.get_acct_book(record_id)

@acct_book_manual_router.post("/query")
async def query_acct_books(request: dict):
    """
    查询账务登记列表
    
    请求体格式:
    ```json
    {
        "query": {
            "page": 1,
            "size": 10,
            "search": "搜索关键词",
            "order_by": "created_at",
            "order_desc": true
        },
        "filters": {
            // 可以添加具体的过滤条件
        }
    }
    ```
    """
    query_data = request.get("query", {})
    filters_data = request.get("filters", {})
    
    query = TMntxAcctBookQuery(**query_data)
    filters = TMntxAcctBookFilter(**filters_data) if filters_data else None
    
    logger.info(f"查询账务登记列表: page={query.page}, size={query.size}")
    return await service.query_acct_books(query, filters)

@acct_book_manual_router.post("/update")
async def update_acct_book(request: dict):
    """
    更新账务登记
    
    请求体格式:
    ```json
    {
        "id": "record_uuid",
        "data": {
            "STAT": "01",
            "AMT": 2000.00,
            // 其他要更新的字段
        }
    }
    ```
    """
    record_id = request.get("id")
    update_data = request.get("data", {})
    
    if not record_id:
        return error_response(message="记录ID不能为空", code="400001")
    
    data = TMntxAcctBookUpdate(**update_data)
    
    logger.info(f"更新账务登记: ID={record_id}")
    return await service.update_acct_book(record_id, data)

@acct_book_manual_router.post("/delete")
async def delete_acct_book(request: dict):
    """
    删除账务登记
    
    请求体格式:
    ```json
    {"id": "record_uuid"}
    ```
    """
    record_id = request.get("id")
    if not record_id:
        return error_response(message="记录ID不能为空", code="400001")
    
    logger.info(f"删除账务登记: ID={record_id}")
    return await service.delete_acct_book(record_id)

# === 自定义业务接口 ===

@acct_book_manual_router.post("/query-by-plat-seq")
async def query_by_plat_seq(request: dict):
    """
    根据平台流水查询账务登记
    
    请求体格式:
    ```json
    {"plat_seq": "202509280001"}
    ```
    """
    plat_seq = request.get("plat_seq")
    if not plat_seq:
        return error_response(message="平台流水号不能为空", code="400002")
    
    logger.info(f"根据平台流水查询: PLAT_SEQ={plat_seq}")
    return await service.get_by_plat_seq(plat_seq)

@acct_book_manual_router.post("/query-by-business")
async def query_by_business_no(request: dict):
    """
    根据业务编号查询账务登记
    
    请求体格式:
    ```json
    {"busi_no": "B001"}
    ```
    """
    busi_no = request.get("busi_no")
    if not busi_no:
        return error_response(message="业务编号不能为空", code="400003")
    
    logger.info(f"根据业务编号查询: BUSI_NO={busi_no}")
    return await service.get_by_business_no(busi_no)

@acct_book_manual_router.post("/statistics")
async def get_statistics(request: dict = None):
    """
    获取账务统计信息
    
    请求体格式（可选）:
    ```json
    {
        "start_date": "20250901",
        "end_date": "20250930"
    }
    ```
    """
    if request:
        start_date = request.get("start_date")
        end_date = request.get("end_date")
    else:
        start_date = end_date = None
    
    logger.info(f"获取账务统计: {start_date} - {end_date}")
    return await service.get_statistics(start_date, end_date)

@acct_book_manual_router.post("/batch-process")
async def batch_process_acct_books(request: dict):
    """
    批量处理账务登记
    
    请求体格式:
    ```json
    {
        "records": [
            {
                "PLAT_SEQ": "202509280001",
                "BUSI_NO": "B001",
                "AMT": 1000.00,
                // 其他字段...
            },
            // 更多记录...
        ]
    }
    ```
    """
    records_data = request.get("records", [])
    if not records_data:
        return error_response(message="批量数据不能为空", code="400004")
    
    # 转换为 Pydantic 对象
    try:
        records = [TMntxAcctBookCreate(**record) for record in records_data]
    except Exception as e:
        return error_response(message=f"数据格式错误: {str(e)}", code="400005")
    
    logger.info(f"批量处理账务登记: {len(records)} 条记录")
    return await service.batch_process(records)

# === 状态管理接口 ===

@acct_book_manual_router.post("/change-status")
async def change_acct_book_status(request: dict):
    """
    修改账务登记状态
    
    请求体格式:
    ```json
    {
        "id": "record_uuid",
        "new_status": "02",
        "reason": "状态变更原因"
    }
    ```
    """
    record_id = request.get("id")
    new_status = request.get("new_status")
    reason = request.get("reason", "")
    
    if not record_id or not new_status:
        return error_response(message="记录ID和新状态不能为空", code="400006")
    
    # 状态变更逻辑
    update_data = TMntxAcctBookUpdate(
        STAT=new_status,
        SHORT_RMRK=reason  # 将原因记录在备注中
    )
    
    logger.info(f"修改账务登记状态: ID={record_id}, Status={new_status}")
    return await service.update_acct_book(record_id, update_data)

"""
手动定义接口的优点：

✅ 精细控制：每个接口都可以自定义验证逻辑
✅ 业务封装：可以组合多个操作为一个业务接口
✅ 参数灵活：可以接受复杂的请求参数结构
✅ 文档完善：可以添加详细的接口说明和示例
✅ 错误处理：可以提供特定的错误码和消息

适用场景：
- 复杂的业务逻辑
- 需要特殊验证的接口
- 组合操作接口
- 对接口行为有特殊要求
"""
