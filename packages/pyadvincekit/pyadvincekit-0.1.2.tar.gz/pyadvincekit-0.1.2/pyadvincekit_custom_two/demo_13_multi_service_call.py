#!/usr/bin/env python3
"""
多服务调用功能测试
"""

import asyncio
import time
from datetime import datetime
from pyadvincekit import (
    register_service, call_service, batch_call_services,
    get_service_stats, health_check_service, health_check_all_services,
    ServiceMethod, get_service_provider, register_service_handler,
    handle_service_request, service_endpoint
)


# 模拟服务A
async def service_a_handler(data: dict) -> dict:
    """服务A的处理器"""
    print(f"🔄 服务A处理请求: {data}")
    await asyncio.sleep(0.1)  # 模拟处理时间
    return {
        "service": "A",
        "result": f"Processed: {data.get('message', '')}",
        "timestamp": datetime.now().isoformat()
    }


# 模拟服务B
async def service_b_handler(data: dict) -> dict:
    """服务B的处理器"""
    print(f"🔄 服务B处理请求: {data}")
    await asyncio.sleep(0.2)  # 模拟处理时间
    return {
        "service": "B",
        "result": f"Calculated: {data.get('value', 0) * 2}",
        "timestamp": datetime.now().isoformat()
    }


# 模拟服务C
async def service_c_handler(data: dict) -> dict:
    """服务C的处理器"""
    print(f"🔄 服务C处理请求: {data}")
    await asyncio.sleep(0.15)  # 模拟处理时间
    return {
        "service": "C",
        "result": f"Validated: {data.get('input', '')}",
        "timestamp": datetime.now().isoformat()
    }


def test_service_registration():
    """测试服务注册"""
    print("🎯 测试服务注册")
    print("=" * 50)
    
    # 注册服务A
    service_a = register_service(
        service_name="service-a",
        base_url="http://localhost:8001",
        timeout=30,
        retry_count=3
    )
    print(f"✅ 注册服务A: {service_a.service_name} at {service_a.base_url}")
    
    # 注册服务B
    service_b = register_service(
        service_name="service-b", 
        base_url="http://localhost:8002",
        timeout=30,
        retry_count=3
    )
    print(f"✅ 注册服务B: {service_b.service_name} at {service_b.base_url}")
    
    # 注册服务C
    service_c = register_service(
        service_name="service-c",
        base_url="http://localhost:8003", 
        timeout=30,
        retry_count=3
    )
    print(f"✅ 注册服务C: {service_c.service_name} at {service_c.base_url}")
    
    return ["service-a", "service-b", "service-c"]


async def test_service_calls():
    """测试服务调用"""
    print("\n🎯 测试服务调用")
    print("=" * 50)
    
    try:
        # 调用服务A
        print("📞 调用服务A...")
        result_a = await call_service(
            service_name="service-a",
            endpoint="/process",
            data={"message": "Hello from A", "type": "greeting"}
        )
        print(f"✅ 服务A响应: {result_a}")
        
        # 调用服务B
        print("📞 调用服务B...")
        result_b = await call_service(
            service_name="service-b",
            endpoint="/calculate",
            data={"value": 42, "operation": "multiply"}
        )
        print(f"✅ 服务B响应: {result_b}")
        
        # 调用服务C
        print("📞 调用服务C...")
        result_c = await call_service(
            service_name="service-c",
            endpoint="/validate",
            data={"input": "test@example.com", "type": "email"}
        )
        print(f"✅ 服务C响应: {result_c}")
        
    except Exception as e:
        print(f"⚠️ 服务调用失败（预期行为，因为服务未实际运行）: {e}")


async def test_batch_calls():
    """测试批量调用"""
    print("\n🎯 测试批量调用")
    print("=" * 50)
    
    # 准备批量调用
    batch_calls = [
        {
            "service_name": "service-a",
            "endpoint": "/process",
            "data": {"message": "Batch call 1", "type": "batch"}
        },
        {
            "service_name": "service-b", 
            "endpoint": "/calculate",
            "data": {"value": 10, "operation": "add"}
        },
        {
            "service_name": "service-c",
            "endpoint": "/validate", 
            "data": {"input": "batch@test.com", "type": "email"}
        }
    ]
    
    try:
        print("📞 执行批量调用...")
        results = await batch_call_services(batch_calls)
        
        print("📊 批量调用结果:")
        for i, result in enumerate(results):
            if result["success"]:
                print(f"  ✅ 调用{i+1}: {result['result']}")
            else:
                print(f"  ❌ 调用{i+1}: {result['error']}")
                
    except Exception as e:
        print(f"⚠️ 批量调用失败（预期行为）: {e}")


def test_service_provider():
    """测试服务提供者"""
    print("\n🎯 测试服务提供者")
    print("=" * 50)
    
    # 获取服务提供者
    provider = get_service_provider("test-service")
    
    # 注册处理器
    handler_a = register_service_handler(
        service_name="test-service",
        method=ServiceMethod.POST,
        endpoint="/process",
        handler=service_a_handler,
        description="处理数据",
        auth_required=False,
        rate_limit=100
    )
    print(f"✅ 注册处理器: {handler_a.method.value} {handler_a.endpoint}")
    
    handler_b = register_service_handler(
        service_name="test-service",
        method=ServiceMethod.POST,
        endpoint="/calculate",
        handler=service_b_handler,
        description="计算数据",
        auth_required=False,
        rate_limit=50
    )
    print(f"✅ 注册处理器: {handler_b.method.value} {handler_b.endpoint}")
    
    # 列出处理器
    handlers = provider.list_handlers()
    print(f"\n📋 已注册的处理器 ({len(handlers)}个):")
    for handler in handlers:
        print(f"  - {handler.method.value} {handler.endpoint}: {handler.description}")
    
    return provider


async def test_service_handling():
    """测试服务处理"""
    print("\n🎯 测试服务处理")
    print("=" * 50)
    
    provider = get_service_provider("test-service")
    
    # 测试处理请求
    test_requests = [
        {
            "method": "POST",
            "endpoint": "/process",
            "data": {"message": "Test processing", "type": "test"}
        },
        {
            "method": "POST", 
            "endpoint": "/calculate",
            "data": {"value": 25, "operation": "square"}
        }
    ]
    
    for i, request in enumerate(test_requests):
        print(f"📥 处理请求 {i+1}: {request['method']} {request['endpoint']}")
        
        try:
            response = await handle_service_request(
                service_name="test-service",
                method=request["method"],
                endpoint=request["endpoint"],
                data=request["data"],
                headers={"X-Trace-Id": f"test-trace-{i+1}"},
                client_ip="127.0.0.1"
            )
            
            print(f"  📤 响应状态: {response.status_code}")
            print(f"  📤 响应数据: {response.data}")
            print(f"  ⏱️ 处理时间: {response.processing_time:.3f}s")
            
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")


def test_service_stats():
    """测试服务统计"""
    print("\n🎯 测试服务统计")
    print("=" * 50)
    
    # 获取服务统计
    stats = get_service_stats("test-service")
    print("📊 服务统计信息:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    
    # 获取请求历史
    provider = get_service_provider("test-service")
    request_history = provider.get_request_history(limit=5)
    print(f"\n📋 最近请求 ({len(request_history)}个):")
    for req in request_history:
        print(f"  - {req.method} {req.endpoint} (ID: {req.request_id[:8]})")
    
    # 获取响应历史
    response_history = provider.get_response_history(limit=5)
    print(f"\n📤 最近响应 ({len(response_history)}个):")
    for resp in response_history:
        print(f"  - 状态: {resp.status_code}, 时间: {resp.processing_time:.3f}s")


async def test_decorator_usage():
    """测试装饰器用法"""
    print("\n🎯 测试装饰器用法")
    print("=" * 50)
    
    # 使用装饰器定义服务端点
    @service_endpoint(
        method=ServiceMethod.POST,
        endpoint="/decorated",
        description="装饰器端点",
        auth_required=False,
        rate_limit=200
    )
    async def decorated_handler(data: dict) -> dict:
        """装饰器处理器"""
        print(f"🔄 装饰器处理器: {data}")
        return {
            "decorated": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    # 注册装饰器处理器
    register_service_handler(
        service_name="test-service",
        method=ServiceMethod.POST,
        endpoint="/decorated",
        handler=decorated_handler,
        description="装饰器端点",
        auth_required=False,
        rate_limit=200
    )
    
    print("✅ 装饰器端点已注册")
    
    # 测试装饰器端点
    try:
        response = await handle_service_request(
            service_name="test-service",
            method="POST",
            endpoint="/decorated",
            data={"test": "decorator", "value": 123}
        )
        print(f"✅ 装饰器端点响应: {response.data}")
    except Exception as e:
        print(f"❌ 装饰器端点测试失败: {e}")


async def main():
    """主测试函数"""
    print("🚀 多服务调用功能测试")
    print("=" * 60)
    
    try:
        # 测试服务注册
        service_names = test_service_registration()
        
        # 测试服务调用
        await test_service_calls()
        
        # 测试批量调用
        await test_batch_calls()
        
        # 测试服务提供者
        test_service_provider()
        
        # 测试服务处理
        await test_service_handling()
        
        # 测试服务统计
        test_service_stats()
        
        # 测试装饰器用法
        await test_decorator_usage()
        
        print("\n🎉 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
