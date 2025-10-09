#!/usr/bin/env python3
"""
定时任务功能测试
"""

import time
import asyncio
from datetime import datetime
from pyadvincekit import (
    schedule_once, schedule_interval, schedule_cron,
    start_scheduler, stop_scheduler, get_task_status, list_tasks,
    TaskStatus, TaskType, get_scheduler
)


def simple_task(name: str = "SimpleTask"):
    """简单任务"""
    print(f"🔄 执行任务: {name} - {datetime.now().strftime('%H:%M:%S')}")
    return f"Task {name} completed"


async def async_task(name: str = "AsyncTask"):
    """异步任务"""
    print(f"🔄 执行异步任务: {name} - {datetime.now().strftime('%H:%M:%S')}")
    await asyncio.sleep(0.1)  # 模拟异步操作
    return f"Async task {name} completed"


def failing_task(name: str = "FailingTask"):
    """会失败的任务"""
    print(f"🔄 执行会失败的任务: {name} - {datetime.now().strftime('%H:%M:%S')}")
    raise Exception(f"Task {name} intentionally failed")


def test_basic_scheduling():
    """测试基本调度功能"""
    print("🎯 测试基本调度功能")
    print("=" * 50)
    
    # 启动调度器
    start_scheduler()
    print("✅ 调度器已启动")
    
    # 添加一次性任务
    task_id1 = schedule_once(simple_task, name="一次性任务")
    print(f"✅ 添加一次性任务: {task_id1}")
    
    # 添加间隔任务（每3秒执行一次）
    task_id2 = schedule_interval(
        simple_task, 
        interval_seconds=3, 
        name="间隔任务"
    )
    print(f"✅ 添加间隔任务: {task_id2}")
    
    # 添加异步任务
    task_id3 = schedule_once(async_task, name="异步任务")
    print(f"✅ 添加异步任务: {task_id3}")
    
    # 添加会失败的任务
    task_id4 = schedule_once(failing_task, name="失败任务", max_retries=2)
    print(f"✅ 添加失败任务: {task_id4}")
    
    # 等待任务执行
    print("\n⏳ 等待任务执行...")
    time.sleep(8)
    
    # 检查任务状态
    print("\n📊 任务状态:")
    tasks = list_tasks()
    for task in tasks:
        print(f"  - {task.name}: {task.status.value}")
        if task.error_message:
            print(f"    错误: {task.error_message}")
    
    # 停止调度器
    stop_scheduler()
    print("✅ 调度器已停止")


def test_decorator_scheduling():
    """测试装饰器调度"""
    print("\n🎯 测试装饰器调度")
    print("=" * 50)
    
    from pyadvincekit import interval_task, cron_task
    
    # 使用装饰器定义任务
    @interval_task(seconds=2, name="装饰器间隔任务")
    def decorated_interval_task():
        print(f"🔄 装饰器间隔任务执行 - {datetime.now().strftime('%H:%M:%S')}")
        return "Decorated interval task completed"
    
    @cron_task(cron_expression="*/5 * * * * *", name="装饰器Cron任务")
    def decorated_cron_task():
        print(f"🔄 装饰器Cron任务执行 - {datetime.now().strftime('%H:%M:%S')}")
        return "Decorated cron task completed"
    
    # 启动调度器
    start_scheduler()
    print("✅ 调度器已启动（装饰器模式）")
    
    # 等待任务执行
    print("⏳ 等待装饰器任务执行...")
    time.sleep(6)
    
    # 检查任务状态
    print("\n📊 装饰器任务状态:")
    tasks = list_tasks()
    for task in tasks:
        if "装饰器" in task.name:
            print(f"  - {task.name}: {task.status.value}")
    
    stop_scheduler()
    print("✅ 调度器已停止")


def test_task_management():
    """测试任务管理功能"""
    print("\n🎯 测试任务管理功能")
    print("=" * 50)
    
    scheduler = get_scheduler()
    
    # 添加多个任务
    task_ids = []
    for i in range(3):
        task_id = schedule_interval(
            simple_task, 
            interval_seconds=2, 
            name=f"管理任务{i+1}"
        )
        task_ids.append(task_id)
    
    start_scheduler()
    print("✅ 调度器已启动")
    
    # 等待一段时间
    time.sleep(3)
    
    # 列出所有任务
    print("\n📋 所有任务:")
    all_tasks = list_tasks()
    for task in all_tasks:
        print(f"  - {task.name} ({task.task_id[:8]}): {task.status.value}")
    
    # 列出运行中的任务
    print("\n🏃 运行中的任务:")
    running_tasks = list_tasks(TaskStatus.RUNNING)
    for task in running_tasks:
        print(f"  - {task.name}: {task.status.value}")
    
    # 移除一个任务
    if task_ids:
        removed = scheduler.remove_task(task_ids[0])
        print(f"\n🗑️ 移除任务: {removed}")
    
    # 获取特定任务状态
    if len(task_ids) > 1:
        status = get_task_status(task_ids[1])
        print(f"📊 任务状态: {status}")
    
    # 等待更多执行
    time.sleep(4)
    
    stop_scheduler()
    print("✅ 调度器已停止")


def main():
    """主测试函数"""
    print("🚀 定时任务功能测试")
    print("=" * 60)
    
    try:
        # 测试基本调度
        test_basic_scheduling()
        
        # # 测试装饰器调度
        # test_decorator_scheduling()
        #
        # # 测试任务管理
        # test_task_management()
        
        print("\n🎉 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
