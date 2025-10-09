#!/usr/bin/env python3
"""
模拟服务 - 为 test_multi_service.py 提供测试端点
启动三个服务：service-a (8001), service-b (8002), service-c (8003)
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import threading

# 请求和响应模型
class ProcessRequest(BaseModel):
    message: str = ""
    type: str = ""

class CalculateRequest(BaseModel):
    value: float = 0
    operation: str = ""

class ValidateRequest(BaseModel):
    input: str = ""
    type: str = ""

class ServiceResponse(BaseModel):
    service: str
    result: str
    timestamp: str
    request_data: Dict[str, Any]

# 服务A - 文本处理服务 (端口 8001)
def create_service_a():
    app = FastAPI(title="Service A - 文本处理", version="1.0.0")
    
    @app.get("/")
    async def root():
        return {"service": "A", "status": "running", "description": "文本处理服务"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "service-a", "timestamp": datetime.now().isoformat()}
    
    @app.post("/process")
    async def process_text(request: ProcessRequest):
        """处理文本数据"""
        await asyncio.sleep(0.1)  # 模拟处理时间
        
        processed_message = f"[PROCESSED] {request.message.upper()}"
        
        return ServiceResponse(
            service="A",
            result=processed_message,
            timestamp=datetime.now().isoformat(),
            request_data=request.dict()
        )
    
    return app

# 服务B - 计算服务 (端口 8002)
def create_service_b():
    app = FastAPI(title="Service B - 计算服务", version="1.0.0")
    
    @app.get("/")
    async def root():
        return {"service": "B", "status": "running", "description": "计算服务"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "service-b", "timestamp": datetime.now().isoformat()}
    
    @app.post("/calculate")
    async def calculate(request: CalculateRequest):
        """执行计算操作"""
        await asyncio.sleep(0.2)  # 模拟处理时间
        
        value = request.value
        operation = request.operation.lower()
        
        # 执行不同的计算操作
        if operation == "multiply":
            result = value * 2
        elif operation == "add":
            result = value + 10
        elif operation == "square":
            result = value ** 2
        elif operation == "sqrt":
            result = value ** 0.5
        else:
            result = value  # 默认返回原值
        
        return ServiceResponse(
            service="B",
            result=f"计算结果: {value} ({operation}) = {result}",
            timestamp=datetime.now().isoformat(),
            request_data=request.dict()
        )
    
    return app

# 服务C - 验证服务 (端口 8003)
def create_service_c():
    app = FastAPI(title="Service C - 验证服务", version="1.0.0")
    
    @app.get("/")
    async def root():
        return {"service": "C", "status": "running", "description": "验证服务"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "service-c", "timestamp": datetime.now().isoformat()}
    
    @app.post("/validate")
    async def validate_input(request: ValidateRequest):
        """验证输入数据"""
        await asyncio.sleep(0.15)  # 模拟处理时间
        
        input_value = request.input
        validation_type = request.type.lower()
        
        # 执行不同的验证
        if validation_type == "email":
            is_valid = "@" in input_value and "." in input_value
            result = f"邮箱 '{input_value}' {'有效' if is_valid else '无效'}"
        elif validation_type == "phone":
            is_valid = input_value.replace("-", "").replace(" ", "").isdigit()
            result = f"电话 '{input_value}' {'有效' if is_valid else '无效'}"
        elif validation_type == "url":
            is_valid = input_value.startswith(("http://", "https://"))
            result = f"URL '{input_value}' {'有效' if is_valid else '无效'}"
        else:
            result = f"输入 '{input_value}' 已通过通用验证"
        
        return ServiceResponse(
            service="C",
            result=result,
            timestamp=datetime.now().isoformat(),
            request_data=request.dict()
        )
    
    return app

# 在单独线程中运行服务
def run_service(app, port: int, service_name: str):
    """在单独线程中运行服务"""
    print(f"🚀 启动 {service_name} 在端口 {port}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

# 主函数
async def main():
    """启动所有三个服务"""
    print("🎯 启动模拟服务集群")
    print("=" * 60)
    
    # 创建三个服务应用
    service_a_app = create_service_a()
    service_b_app = create_service_b()
    service_c_app = create_service_c()
    
    # 在单独的线程中启动每个服务
    threads = []
    
    # 服务A - 端口 8001
    thread_a = threading.Thread(
        target=run_service, 
        args=(service_a_app, 8001, "Service A (文本处理)"),
        daemon=True
    )
    thread_a.start()
    threads.append(thread_a)
    
    # 服务B - 端口 8002  
    thread_b = threading.Thread(
        target=run_service,
        args=(service_b_app, 8002, "Service B (计算服务)"),
        daemon=True
    )
    thread_b.start()
    threads.append(thread_b)
    
    # 服务C - 端口 8003
    thread_c = threading.Thread(
        target=run_service,
        args=(service_c_app, 8003, "Service C (验证服务)"),
        daemon=True
    )
    thread_c.start()
    threads.append(thread_c)
    
    # 等待所有服务启动
    await asyncio.sleep(2)
    
    print("\n✅ 所有服务已启动！")
    print("📋 服务信息:")
    print("  - Service A (文本处理): http://localhost:8001")
    print("  - Service B (计算服务): http://localhost:8002") 
    print("  - Service C (验证服务): http://localhost:8003")
    print("\n📖 API 文档:")
    print("  - Service A: http://localhost:8001/docs")
    print("  - Service B: http://localhost:8002/docs")
    print("  - Service C: http://localhost:8003/docs")
    print("\n🧪 现在可以运行 test_multi_service.py 进行测试")
    print("💡 按 Ctrl+C 停止所有服务")
    
    try:
        # 保持主线程运行
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 正在停止所有服务...")
        print("👋 所有服务已停止")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
