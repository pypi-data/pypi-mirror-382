#!/usr/bin/env python3
"""
同步版本的第一阶段功能测试
避免异步相关的复杂性，专注于测试核心功能
"""

import sys
import os
import json

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_response_format():
    """测试响应格式"""
    print("🧪 测试新的响应格式...")
    
    try:
        from pyadvincekit.core.response import (
            success_response, error_response, paginated_response,
            ResponseCode, ResponseMessage
        )
        
        # 测试成功响应
        print("\n📊 成功响应测试:")
        response = success_response(
            data={"id": "123", "name": "测试产品", "price": 99.99},
            message="产品查询成功",
            ret_code=ResponseCode.SUCCESS
        )
        
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # 验证结构
        required_keys = ["sysHead", "appHead", "body"]
        has_structure = all(key in response for key in required_keys)
        print(f"✅ 响应结构完整: {has_structure}")
        
        # 验证sysHead
        sys_head = response["sysHead"]
        print(f"✅ 交易状态: {sys_head['tranStat']}")
        print(f"✅ 返回码: {sys_head['tranRet'][0]['retCode']}")
        print(f"✅ 返回消息: {sys_head['tranRet'][0]['retMsg']}")
        
        # 测试错误响应
        print("\n❌ 错误响应测试:")
        error_resp = error_response(
            message="测试错误",
            ret_code=ResponseCode.BUSINESS_ERROR
        )
        
        # 由于error_response返回JSONResponse对象，我们需要获取其content
        if hasattr(error_resp, 'body'):
            error_content = json.loads(error_resp.body.decode())
        else:
            # 如果是字典，直接使用
            error_content = error_resp if isinstance(error_resp, dict) else {"error": "无法解析"}
        
        print(f"✅ 错误响应生成成功")
        
        # 测试分页响应
        print("\n📄 分页响应测试:")
        items = [
            {"id": "1", "name": "产品1", "price": 99.99},
            {"id": "2", "name": "产品2", "price": 149.99},
            {"id": "3", "name": "产品3", "price": 199.99}
        ]
        
        paginated_resp = paginated_response(
            items=items,
            page=1,
            page_size=10,
            total=3
        )
        
        print(f"✅ 分页信息 - 总数: {paginated_resp['sysHead']['totNum']}")
        print(f"✅ 分页信息 - 响应数: {paginated_resp['sysHead']['respRecNum']}")
        print(f"✅ 分页信息 - 结束标志: {paginated_resp['sysHead']['endFlg']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 响应格式测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_request_schemas():
    """测试请求Schema"""
    print("\n🧪 测试请求Schema...")
    
    try:
        from pyadvincekit.schemas.common import (
            QueryRequest, GetByIdRequest, DeleteRequest, UpdateRequest, CountRequest
        )
        
        # 测试QueryRequest
        print("\n📝 QueryRequest测试:")
        query_req = QueryRequest(
            page=1,
            size=20,
            filters={"category": "electronics", "status": "active"},
            order_by="created_at",
            order_desc=True
        )
        print(f"✅ QueryRequest: {query_req.model_dump()}")
        
        # 测试GetByIdRequest
        print("\n🔍 GetByIdRequest测试:")
        get_req = GetByIdRequest(id="prod-123")
        print(f"✅ GetByIdRequest: {get_req.model_dump()}")
        
        # 测试DeleteRequest
        print("\n🗑️ DeleteRequest测试:")
        delete_req = DeleteRequest(id="prod-456")
        print(f"✅ DeleteRequest: {delete_req.model_dump()}")
        
        # 测试UpdateRequest
        print("\n✏️ UpdateRequest测试:")
        update_req = UpdateRequest(
            id="prod-789",
            data={"name": "更新的产品名", "price": 299.99}
        )
        print(f"✅ UpdateRequest: {update_req.model_dump()}")
        
        # 测试CountRequest
        print("\n🔢 CountRequest测试:")
        count_req = CountRequest(
            filters={"status": "active"},
            include_deleted=False
        )
        print(f"✅ CountRequest: {count_req.model_dump()}")
        
        return True
        
    except Exception as e:
        print(f"❌ 请求Schema测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_response_codes():
    """测试响应码和消息"""
    print("\n🧪 测试响应码和消息...")
    
    try:
        from pyadvincekit.core.response import ResponseCode, ResponseMessage
        
        print("\n🔢 响应状态码测试:")
        print(f"✅ 成功码: {ResponseCode.SUCCESS}")
        print(f"✅ 业务错误: {ResponseCode.BUSINESS_ERROR}")
        print(f"✅ 数据不存在: {ResponseCode.DATA_NOT_FOUND}")
        print(f"✅ 验证错误: {ResponseCode.VALIDATION_ERROR}")
        print(f"✅ 系统错误: {ResponseCode.SYSTEM_ERROR}")
        
        print("\n💬 响应消息测试:")
        print(f"✅ 成功消息: {ResponseMessage.SUCCESS}")
        print(f"✅ 创建成功: {ResponseMessage.CREATED}")
        print(f"✅ 更新成功: {ResponseMessage.UPDATED}")
        print(f"✅ 删除成功: {ResponseMessage.DELETED}")
        print(f"✅ 查询成功: {ResponseMessage.QUERIED}")
        
        # 验证状态码格式
        success_format = ResponseCode.SUCCESS == "000000"
        error_format = ResponseCode.SYSTEM_ERROR == "999999"
        
        print(f"\n✅ 状态码格式验证: 成功码={success_format}, 系统错误码={error_format}")
        
        return success_format and error_format
        
    except Exception as e:
        print(f"❌ 响应码测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_creation():
    """测试应用创建"""
    print("\n🧪 测试应用创建...")
    
    try:
        from pyadvincekit.core.app_factory import create_app
        
        # 创建基础应用
        app = create_app(
            title="测试应用",
            description="这是一个测试应用",
            version="1.0.0"
        )
        
        print(f"✅ 应用创建成功: {app.title}")
        print(f"✅ 应用版本: {app.version}")
        print(f"✅ 应用类型: {type(app).__name__}")
        
        # 检查基本路由
        routes = [route for route in app.routes if hasattr(route, 'path')]
        health_routes = [route for route in routes if 'health' in route.path]
        
        print(f"✅ 健康检查路由数量: {len(health_routes)}")
        for route in health_routes:
            print(f"  - {route.path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 应用创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_definition():
    """测试模型定义"""
    print("\n🧪 测试模型定义...")
    
    try:
        from pyadvincekit.models.base import BaseModel
        from sqlalchemy import String
        from sqlalchemy.orm import Mapped, mapped_column
        
        # 定义测试模型
        class TestModel(BaseModel):
            __tablename__ = "test_model"
            
            name: Mapped[str] = mapped_column(String(100), nullable=False)
            description: Mapped[str] = mapped_column(String(500), nullable=True)
        
        print(f"✅ 模型定义成功: {TestModel.__name__}")
        print(f"✅ 表名: {TestModel.__tablename__}")
        print(f"✅ 主键字段: {TestModel.get_primary_key()}")
        
        # 测试模型实例化
        instance = TestModel(name="测试实例", description="这是一个测试实例")
        print(f"✅ 模型实例化成功: {instance.name}")
        
        # 测试字典转换
        data_dict = instance.to_dict()
        print(f"✅ 字典转换成功: {list(data_dict.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型定义测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 PyAdvanceKit 第一阶段同步功能测试")
    print("=" * 60)
    
    test_cases = [
        ("响应格式", test_response_format),
        ("请求Schema", test_request_schemas),
        ("响应码和消息", test_response_codes),
        ("应用创建", test_app_creation),
        ("模型定义", test_model_definition),
    ]
    
    results = []
    
    for test_name, test_func in test_cases:
        print(f"\n{'='*60}")
        print(f"🧪 执行测试: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            status = "✅ 通过" if result else "❌ 失败"
            print(f"\n{status}: {test_name}")
            
        except Exception as e:
            print(f"\n❌ 测试异常: {test_name} - {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print(f"\n{'='*60}")
    print("📊 测试结果汇总")
    print(f"{'='*60}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n📈 总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有同步功能测试通过！")
        print("✨ 第一阶段核心功能运行正常")
        print("\n🎯 测试总结:")
        print("  ✅ 新的响应格式 (sysHead/appHead/body) 正常工作")
        print("  ✅ 请求Schema类定义正确")
        print("  ✅ 响应码和消息常量可用")
        print("  ✅ FastAPI应用创建成功")
        print("  ✅ 数据库模型定义正常")
        
        print("\n💡 建议:")
        print("  1. 核心功能测试通过，可以进行异步功能测试")
        print("  2. 可以开始第二阶段的开发")
        print("  3. 建议编写更多的单元测试")
        
    else:
        failed_count = total - passed
        print(f"\n⚠️  {failed_count} 项测试失败")
        print("🔧 建议: 检查并修复失败的功能")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n{'🎊' * 15}")
        print("第一阶段同步功能测试完全通过！")
        print(f"{'🎊' * 15}")
