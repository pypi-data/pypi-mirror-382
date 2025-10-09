#!/usr/bin/env python3
"""
账务登记表业务服务

提供账务登记相关的业务逻辑处理
"""

from typing import List, Optional, Dict, Any
from pyadvincekit import (
    BaseCRUD, get_database,
    success_response, error_response, paginated_response
)
from pyadvincekit.logging import get_logger

# 导入模型和模式
import sys
from pathlib import Path

# PyAdvanceKit Admin Backend 的标准做法
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from models.t_mntx_acct_book import TMntxAcctBook
from schemas.t_mntx_acct_book import (
    TMntxAcctBookCreate, TMntxAcctBookUpdate, TMntxAcctBookResponse,
    TMntxAcctBookQuery, TMntxAcctBookFilter
)

logger = get_logger(__name__)


class AcctBookService:
    """账务登记表业务服务"""
    
    def __init__(self):
        # 直接使用 PyAdvanceKit 的 BaseCRUD，无需独立的 CRUD 层
        self.crud = BaseCRUD(TMntxAcctBook)
    
    async def create_acct_book(self, data: TMntxAcctBookCreate) -> Dict[str, Any]:
        """创建账务登记"""
        async with get_database() as db:
            try:
                # 业务验证
                validation_result = await self._validate_create_rules(db, data)
                if not validation_result["valid"]:
                    return error_response(
                        message=validation_result["message"],
                        ret_code="400001"
                    )
                
                # 创建记录
                created = await self.crud.create(db, obj_in=data)
                
                # 记录操作日志
                logger.info(f"创建账务登记成功: PLAT_SEQ={data.PLAT_SEQ}, BUSI_NO={data.BUSI_NO}")
                
                return success_response(
                    data=created.__dict__,
                    message="账务登记创建成功"
                )
                
            except Exception as e:
                logger.error(f"创建账务登记失败: {str(e)}")
                return error_response(
                    message=f"创建失败: {str(e)}",
                    ret_code="500001"
                )
    
    async def get_acct_book(self, record_id: str) -> Dict[str, Any]:
        """获取账务登记详情"""
        async with get_database() as db:
            try:
                record = await self.crud.get(db, id=record_id)
                if record:
                    return success_response(
                        data=record.__dict__,
                        message="查询成功"
                    )
                else:
                    return error_response(
                        message="账务登记记录不存在",
                        ret_code="404001"
                    )
            except Exception as e:
                logger.error(f"查询账务登记失败: {str(e)}")
                return error_response(
                    message=f"查询失败: {str(e)}",
                    ret_code="500002"
                )
    
    async def query_acct_books(self, query: TMntxAcctBookQuery, filters: TMntxAcctBookFilter = None) -> Dict[str, Any]:
        """查询账务登记列表"""
        async with get_database() as db:
            try:
                # 构建查询条件
                query_params = self._build_query_params(query, filters)
                
                # 执行查询
                filters = query_params.get("filters", {})
                records = await self.crud.get_multi(
                    db, 
                    skip=(query.page - 1) * query.size,
                    limit=query.size,
                    order_by=query_params.get("order_by"),
                    order_desc=query_params.get("order_desc", False),
                    filters=filters
                )
                total = await self.crud.count(db, filters=filters)
                
                # 转换响应数据
                response_items = [record.__dict__ for record in records]
                
                return success_response(
                    data={
                        "items": response_items,
                        "total": total,
                        "page": query.page,
                        "size": query.size,
                        "pages": (total + query.size - 1) // query.size
                    },
                    message="查询成功"
                )
            except Exception as e:
                logger.error(f"查询账务登记列表失败: {str(e)}")
                return error_response(
                    message=f"查询失败: {str(e)}",
                    ret_code="500003"
                )
    
    async def update_acct_book(self, record_id: str, data: TMntxAcctBookUpdate) -> Dict[str, Any]:
        """更新账务登记"""
        async with get_database() as db:
            try:
                # 检查记录是否存在
                existing = await self.crud.get(db, id=record_id)
                if not existing:
                    return error_response(
                        message="账务登记记录不存在",
                        ret_code="404001"
                    )
                
                # 业务验证
                validation_result = await self._validate_update_rules(db, existing, data)
                if not validation_result["valid"]:
                    return error_response(
                        message=validation_result["message"],
                        ret_code="400002"
                    )
                
                # 执行更新
                updated = await self.crud.update(db, db_obj=existing, obj_in=data)
                
                logger.info(f"更新账务登记成功: ID={record_id}")
                
                return success_response(
                    data=updated.__dict__,
                    message="更新成功"
                )
                
            except Exception as e:
                logger.error(f"更新账务登记失败: {str(e)}")
                return error_response(
                    message=f"更新失败: {str(e)}",
                    ret_code="500004"
                )
    
    async def delete_acct_book(self, record_id: str) -> Dict[str, Any]:
        """删除账务登记"""
        async with get_database() as db:
            try:
                # 检查记录是否存在
                existing = await self.crud.get(db, id=record_id)
                if not existing:
                    return error_response(
                        message="账务登记记录不存在",
                        ret_code="404001"
                    )
                
                # 业务验证（某些状态下不允许删除）
                if existing.STAT == "02":  # 假设 02 表示已完成状态
                    return error_response(
                        message="已完成的账务登记不能删除",
                        ret_code="400003"
                    )
                
                # 执行删除（软删除）
                await self.crud.remove(db, id=record_id)
                
                logger.info(f"删除账务登记成功: ID={record_id}")
                
                return success_response(
                    data=None,
                    message="删除成功"
                )
                
            except Exception as e:
                logger.error(f"删除账务登记失败: {str(e)}")
                return error_response(
                    message=f"删除失败: {str(e)}",
                    ret_code="500005"
                )
    
    async def get_by_plat_seq(self, plat_seq: str) -> Dict[str, Any]:
        """根据平台流水查询"""
        async with get_database() as db:
            try:
                # 使用 BaseCRUD 的通用查询方法
                records = await self.crud.get_multi(db, filters={"PLAT_SEQ": plat_seq})
                if records:
                    return success_response(
                        data=[record.__dict__ for record in records],
                        message="查询成功"
                    )
                else:
                    return error_response(
                        message="未找到对应的账务登记记录",
                        ret_code="404002"
                    )
            except Exception as e:
                logger.error(f"根据平台流水查询失败: {str(e)}")
                return error_response(
                    message=f"查询失败: {str(e)}",
                    ret_code="500006"
                )
    
    async def get_by_business_no(self, busi_no: str) -> Dict[str, Any]:
        """根据业务编号查询"""
        async with get_database() as db:
            try:
                records = await self.crud.get_multi(db, filters={"BUSI_NO": busi_no})
                if records:
                    return success_response(
                        data=[record.__dict__ for record in records],
                        message="查询成功"
                    )
                else:
                    return error_response(
                        message="未找到对应业务编号的账务登记记录",
                        ret_code="404003"
                    )
            except Exception as e:
                logger.error(f"根据业务编号查询失败: {str(e)}")
                return error_response(
                    message=f"查询失败: {str(e)}",
                    ret_code="500007"
                )
    
    # === 私有方法：业务验证逻辑 ===
    
    async def _validate_create_rules(self, db, data: TMntxAcctBookCreate) -> Dict[str, Any]:
        """创建时的业务规则验证"""
        try:
            # 验证1：平台流水不能重复
            if data.PLAT_SEQ:
                existing_records = await self.crud.get_multi(db, filters={"PLAT_SEQ": data.PLAT_SEQ})
                if existing_records:
                    return {
                        "valid": False,
                        "message": f"平台流水号 {data.PLAT_SEQ} 已存在"
                    }
            
            # 验证2：业务编号格式检查
            if data.BUSI_NO and len(data.BUSI_NO) < 3:
                return {
                    "valid": False,
                    "message": "业务编号长度不能少于3位"
                }
            
            # 验证3：金额必须大于0
            if data.AMT is not None and data.AMT <= 0:
                return {
                    "valid": False,
                    "message": "金额必须大于0"
                }
            
            return {"valid": True, "message": "验证通过"}
            
        except Exception as e:
            logger.error(f"创建验证规则执行失败: {str(e)}")
            return {
                "valid": False,
                "message": f"验证过程出错: {str(e)}"
            }
    
    async def _validate_update_rules(self, db, existing, data: TMntxAcctBookUpdate) -> Dict[str, Any]:
        """更新时的业务规则验证"""
        try:
            # 验证1：某些状态下不允许修改
            if existing.STAT == "02":  # 已完成状态
                return {
                    "valid": False,
                    "message": "已完成状态的账务登记不允许修改"
                }
            
            # 验证2：关键字段修改检查
            if data.PLAT_SEQ and data.PLAT_SEQ != existing.PLAT_SEQ:
                # 检查新的平台流水是否重复
                existing_records = await self.crud.get_multi(db, filters={"PLAT_SEQ": data.PLAT_SEQ})
                if existing_records:
                    return {
                        "valid": False,
                        "message": f"平台流水号 {data.PLAT_SEQ} 已存在"
                    }
            
            # 验证3：金额修改检查
            if data.AMT is not None and data.AMT <= 0:
                return {
                    "valid": False,
                    "message": "金额必须大于0"
                }
            
            return {"valid": True, "message": "验证通过"}
            
        except Exception as e:
            logger.error(f"更新验证规则执行失败: {str(e)}")
            return {
                "valid": False,
                "message": f"验证过程出错: {str(e)}"
            }
    
    def _build_query_params(self, query: TMntxAcctBookQuery, filters: TMntxAcctBookFilter = None) -> Dict[str, Any]:
        """构建查询参数"""
        params = {}
        
        # 添加搜索条件
        if query.search:
            # 定义可搜索的字段
            params["search_fields"] = ["BUSI_NAME", "NOTE_NO", "PAY_ACCT_NAME", "PAYEE_ACCT_NAME"]
            params["search_value"] = query.search
        
        # 添加排序
        if query.order_by:
            params["order_by"] = query.order_by
            params["order_desc"] = query.order_desc
        else:
            # 默认按创建时间倒序
            params["order_by"] = "created_at"
            params["order_desc"] = True
        
        # 添加过滤条件（如果定义了具体的过滤字段）
        if filters:
            # 这里可以根据 TMntxAcctBookFilter 中定义的具体字段添加过滤逻辑
            # 例如按状态过滤、按日期范围过滤等
            pass
        
        return params
    
    # === 扩展业务方法 ===
    
    async def get_statistics(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """获取账务统计信息"""
        async with get_database() as db:
            try:
                # 可以使用 BaseCRUD 的原生查询能力
                # 或者调用数据库函数/存储过程
                
                # 示例统计逻辑
                total_count = await self.crud.count(db)
                
                # 这里可以添加更复杂的统计查询
                stats = {
                    "total_records": total_count,
                    "date_range": {
                        "start": start_date,
                        "end": end_date
                    }
                }
                
                return success_response(
                    data=stats,
                    message="统计查询成功"
                )
                
            except Exception as e:
                logger.error(f"统计查询失败: {str(e)}")
                return error_response(
                    message=f"统计查询失败: {str(e)}",
                    code="500008"
                )
    
    async def batch_process(self, records: List[TMntxAcctBookCreate]) -> Dict[str, Any]:
        """批量处理账务登记"""
        async with get_database() as db:
            try:
                success_count = 0
                failed_items = []
                
                for idx, record_data in enumerate(records):
                    try:
                        # 逐个验证并创建
                        validation_result = await self._validate_create_rules(db, record_data)
                        if validation_result["valid"]:
                            await self.crud.create(db, obj_in=record_data)
                            success_count += 1
                        else:
                            failed_items.append({
                                "index": idx,
                                "data": record_data.dict(),
                                "error": validation_result["message"]
                            })
                    except Exception as e:
                        failed_items.append({
                            "index": idx,
                            "data": record_data.dict(),
                            "error": str(e)
                        })
                
                logger.info(f"批量处理完成: 成功={success_count}, 失败={len(failed_items)}")
                
                return success_response(
                    data={
                        "success_count": success_count,
                        "failed_count": len(failed_items),
                        "failed_items": failed_items
                    },
                    message=f"批量处理完成，成功 {success_count} 条"
                )
                
            except Exception as e:
                logger.error(f"批量处理失败: {str(e)}")
                return error_response(
                    message=f"批量处理失败: {str(e)}",
                    code="500009"
                )
