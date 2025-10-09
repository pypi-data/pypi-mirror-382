#!/usr/bin/env python3
"""
完整的 Cron 表达式支持演示
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from pyadvincekit.utils.cron_parser import (
    CronExpression, CronParseError, parse_cron_expression,
    get_next_cron_time, validate_cron_expression
)
from pyadvincekit import (
    schedule_cron, start_scheduler, stop_scheduler,
    get_task_status, list_tasks, TaskStatus, get_scheduler,
    cron_task, interval_task, scheduled_task, TaskType
)
from pyadvincekit.logging import get_logger

logger = get_logger(__name__)

def get_task_info(task_id: str):
    """获取完整的任务信息"""
    all_tasks = list_tasks()
    return next((task for task in all_tasks if task.task_id == task_id), None)

def demo_task(name: str = "Demo"):
    """演示任务"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"🔄 [{current_time}] 执行任务: {name}")
    logger.info(f"Task executed: {name} at {current_time}")

def demo_cron_parsing():
    """演示 Cron 表达式解析"""
    print("🕐 Cron 表达式解析演示")
    print("=" * 60)
    
    # 测试各种 cron 表达式
    test_expressions = [
        # 标准5字段格式
        "0 9 * * *",           # 每天9点
        "30 14 * * 1-5",       # 工作日下午2:30
        "0 0 1 * *",           # 每月1号午夜
        "0 */6 * * *",         # 每6小时
        "15,45 * * * *",       # 每小时的15分和45分
        "0 9-17/2 * * 1-5",    # 工作日9-17点每2小时
        
        # 6字段格式（包含秒）
        "30 0 9 * * *",        # 每天9:00:30
        "0,30 0 */2 * * *",    # 每2小时的整点和30秒
        
        # 特殊表达式
        "@daily",              # 每天午夜
        "@hourly",             # 每小时
        "@weekly",             # 每周
        "@monthly",            # 每月
        "@yearly",             # 每年
        
        # 错误表达式（用于测试）
        "invalid expression",   # 无效表达式
        "0 25 * * *",          # 无效小时
    ]
    
    for expr in test_expressions:
        print(f"\n📝 表达式: {expr}")
        try:
            cron = parse_cron_expression(expr)
            next_time = cron.get_next_run_time()
            description = cron.get_description()
            
            print(f"   ✅ 解析成功")
            print(f"   📅 下次执行: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   📝 描述: {description}")
            
            # 验证是否匹配当前时间
            if cron.matches(datetime.now()):
                print(f"   🎯 当前时间匹配此表达式")
                
        except CronParseError as e:
            print(f"   ❌ 解析失败: {e}")

def demo_cron_validation():
    """演示 Cron 表达式验证"""
    print("\n🔍 Cron 表达式验证演示")
    print("=" * 60)
    
    expressions = [
        "0 9 * * *",           # 有效
        "invalid",             # 无效
        "0 0 32 * *",          # 无效日期
        "60 * * * *",          # 无效分钟
        "@daily",              # 有效特殊表达式
        "* * * * * *",         # 有效6字段
        "0 0 0 1 1 * extra",   # 字段过多
    ]
    
    for expr in expressions:
        is_valid = validate_cron_expression(expr)
        status = "✅ 有效" if is_valid else "❌ 无效"
        print(f"   {expr:<20} -> {status}")

def demo_next_run_calculation():
    """演示下次执行时间计算"""
    print("\n⏰ 下次执行时间计算演示")
    print("=" * 60)
    
    now = datetime.now()
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    expressions = [
        "*/5 * * * *",         # 每5分钟
        "0 */1 * * *",         # 每小时
        "0 9,12,18 * * *",     # 每天的9点、12点、18点
        "0 9 * * 1",           # 每周一9点
        "0 0 1,15 * *",        # 每月1号和15号
    ]
    
    for expr in expressions:
        try:
            next_time = get_next_cron_time(expr, now)
            diff = next_time - now
            
            print(f"   {expr:<20} -> {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   {' ' * 21}   (还有 {diff})")
            
        except CronParseError as e:
            print(f"   {expr:<20} -> 错误: {e}")

def demo_decorator_usage():
    """演示装饰器用法"""
    print("\n🎨 装饰器用法演示")
    print("=" * 60)
    
    # 定义装饰器任务
    @cron_task("*/1 * * * *", name="装饰器每分钟任务")
    def minute_decorator_task():
        """使用 @cron_task 装饰器的任务"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"🎯 [{current_time}] 装饰器任务: 每分钟执行")
        logger.info(f"Decorator cron task executed at {current_time}")
    
    @cron_task("*/3 * * * *", name="装饰器每3分钟任务")
    def three_minute_decorator_task():
        """每3分钟执行的装饰器任务"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"🔥 [{current_time}] 装饰器任务: 每3分钟执行")
        logger.info(f"Decorator 3-minute task executed at {current_time}")
    
    @cron_task("@hourly", name="装饰器小时任务")
    def hourly_decorator_task():
        """使用特殊表达式的装饰器任务"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"⏰ [{current_time}] 装饰器任务: 每小时执行")
        logger.info(f"Decorator hourly task executed at {current_time}")
    
    @interval_task(seconds=120, name="装饰器间隔任务")  
    def interval_decorator_task():
        """使用 @interval_task 装饰器的任务"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"🔄 [{current_time}] 装饰器任务: 每2分钟间隔执行")
        logger.info(f"Decorator interval task executed at {current_time}")
    
    @scheduled_task(
        name="装饰器复杂任务",
        task_type=TaskType.CRON,
        cron_expression="0,30 * * * *",  # 每小时的0分和30分
        max_retries=5
    )
    def complex_decorator_task():
        """使用 @scheduled_task 装饰器的复杂任务"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"⚙️ [{current_time}] 装饰器任务: 复杂定时规则")
        logger.info(f"Decorator complex task executed at {current_time}")
    
    @cron_task("*/2 * * * * *", name="装饰器每2秒任务")  # 6字段格式：每2秒
    def two_second_decorator_task():
        """使用 @cron_task 装饰器的每2秒任务"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 包含毫秒
        print(f"⚡ [{current_time}] 装饰器任务: 每2秒执行")
        logger.info(f"Decorator 2-second task executed at {current_time}")
    
    @interval_task(seconds=2, name="装饰器间隔2秒任务")
    def two_second_interval_task():
        """使用 @interval_task 装饰器的每2秒间隔任务"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 包含毫秒
        print(f"🔥 [{current_time}] 装饰器任务: 间隔2秒执行")
        logger.info(f"Decorator 2-second interval task executed at {current_time}")
    
    print("✅ 装饰器任务已定义和注册")
    print("📝 定义的装饰器任务:")
    print("   - @cron_task('*/1 * * * *'): 每分钟任务")
    print("   - @cron_task('*/3 * * * *'): 每3分钟任务") 
    print("   - @cron_task('@hourly'): 每小时任务")
    print("   - @interval_task(seconds=120): 每2分钟间隔任务")
    print("   - @scheduled_task(...): 复杂定时任务")
    print("   - @cron_task('*/2 * * * * *'): 每2秒任务 (6字段格式)")
    print("   - @interval_task(seconds=2): 每2秒间隔任务")
    
    # 启动调度器以便装饰器任务能够执行
    scheduler = get_scheduler()
    if not scheduler.running:
        start_scheduler()
        print("✅ 调度器已启动，装饰器任务开始生效")
    
    # 显示所有任务
    print("\n📋 当前所有任务:")
    all_tasks = list_tasks()
    decorator_tasks = [task for task in all_tasks if "装饰器" in task.name]
    
    for task in decorator_tasks:
        next_run_str = task.next_run.strftime('%Y-%m-%d %H:%M:%S') if task.next_run else 'N/A'
        print(f"   - {task.name}: {task.status.value} (下次: {next_run_str})")
    
    return decorator_tasks

def demo_cron_scheduler_integration():
    """演示 Cron 调度器集成"""
    print("\n🔧 Cron 调度器集成演示")
    print("=" * 60)
    
    # 启动调度器
    scheduler = get_scheduler()
    if not scheduler.running:
        start_scheduler()
        print("✅ 调度器已启动")
    
    # 添加各种 cron 任务
    tasks = []
    
    # 每分钟执行一次（测试用）
    task_id1 = schedule_cron(
        lambda: demo_task("每分钟任务"),
        cron_expression="* * * * *",  # 每分钟
        name="分钟任务"
    )
    tasks.append(task_id1)
    print(f"✅ 添加任务: 每分钟执行 (ID: {task_id1[:8]})")
    
    # 每2分钟执行一次
    task_id2 = schedule_cron(
        lambda: demo_task("每2分钟任务"), 
        cron_expression="*/2 * * * *",  # 每2分钟
        name="2分钟任务"
    )
    tasks.append(task_id2)
    print(f"✅ 添加任务: 每2分钟执行 (ID: {task_id2[:8]})")
    
    # 使用特殊表达式
    task_id3 = schedule_cron(
        lambda: demo_task("小时任务"),
        cron_expression="@hourly",      # 每小时
        name="小时任务"
    )
    tasks.append(task_id3)
    print(f"✅ 添加任务: 每小时执行 (ID: {task_id3[:8]})")
    
    # 添加每2秒执行的任务（使用6字段cron表达式）
    task_id4 = schedule_cron(
        lambda: demo_task("每2秒任务"),
        cron_expression="*/2 * * * * *",  # 每2秒
        name="每2秒任务"
    )
    tasks.append(task_id4)
    print(f"✅ 添加任务: 每2秒执行 (ID: {task_id4[:8]})")
    
    # 显示任务状态
    print("\n📋 当前任务列表:")
    for task_id in tasks:
        task_info = get_task_info(task_id)
        if task_info:
            next_run_str = task_info.next_run.strftime('%Y-%m-%d %H:%M:%S') if task_info.next_run else 'N/A'
            print(f"   - {task_info.name}: {task_info.status.value} (下次: {next_run_str})")
    
    print(f"\n⏳ 观察任务执行 (运行15秒)...")
    print("   (观察控制台输出的任务执行日志)")
    
    # 运行15秒观察任务执行
    time.sleep(15)
    
    # 清理任务
    print(f"\n🧹 清理测试任务...")
    all_tasks = list_tasks()
    for task_info in all_tasks:
        task_name = task_info.name
        if task_name in ['分钟任务', '2分钟任务', '小时任务', '每2秒任务'] or '装饰器' in task_name:
            scheduler.remove_task(task_info.task_id)
            print(f"   删除任务: {task_name}")

def demo_advanced_cron_features():
    """演示高级 Cron 功能"""
    print("\n🚀 高级 Cron 功能演示")
    print("=" * 60)
    
    # 复杂表达式测试
    advanced_expressions = [
        # 工作时间
        ("工作时间", "0 9-17 * * 1-5", "工作日9-17点"),
        # 周末
        ("周末", "0 10 * * 6,0", "周末10点"),
        # 月末
        ("月末", "0 23 28-31 * *", "每月28-31号23点"),
        # 季度
        ("季度", "0 0 1 1,4,7,10 *", "每季度第一天"),
        # 秒级精度
        ("秒级", "0,30 * * * * *", "每30秒"),
    ]
    
    for name, expr, desc in advanced_expressions:
        print(f"\n📊 {name} ({desc})")
        print(f"   表达式: {expr}")
        
        try:
            cron = parse_cron_expression(expr)
            
            # 计算接下来3次执行时间
            current_time = datetime.now()
            next_times = []
            
            for i in range(3):
                next_time = cron.get_next_run_time(current_time)
                next_times.append(next_time)
                current_time = next_time + timedelta(seconds=1)
            
            print(f"   接下来3次执行:")
            for i, nt in enumerate(next_times, 1):
                print(f"     {i}. {nt.strftime('%Y-%m-%d %H:%M:%S %A')}")
                
        except CronParseError as e:
            print(f"   ❌ 错误: {e}")

class CronUsageGuide:
    """Cron 使用指南"""
    
    @staticmethod
    def print_usage_guide():
        """打印使用指南"""
        print("\n📖 PyAdvanceKit Cron 表达式使用指南")
        print("=" * 70)
        
        print("\n📝 标准格式:")
        print("   5字段: 分钟 小时 日期 月份 星期")
        print("   6字段: 秒 分钟 小时 日期 月份 星期")
        
        print("\n🔤 字段范围:")
        print("   秒:   0-59")
        print("   分钟: 0-59") 
        print("   小时: 0-23")
        print("   日期: 1-31")
        print("   月份: 1-12")
        print("   星期: 0-7 (0和7都表示周日)")
        
        print("\n🔣 特殊字符:")
        print("   *      任意值")
        print("   ,      值列表 (1,3,5)")
        print("   -      值范围 (1-5)")
        print("   /      步长 (*/5, 1-10/2)")
        
        print("\n⭐ 特殊表达式:")
        print("   @yearly   每年 (0 0 1 1 *)")
        print("   @monthly  每月 (0 0 1 * *)")
        print("   @weekly   每周 (0 0 * * 0)")
        print("   @daily    每天 (0 0 * * *)")
        print("   @hourly   每小时 (0 * * * *)")
        
        print("\n💡 使用示例:")
        print("   # 基础用法")
        print("   from pyadvincekit import schedule_cron, start_scheduler")
        print("   ")
        print("   def my_task():")
        print("       print('任务执行了！')")
        print("   ")
        print("   # 每天9点执行")
        print("   schedule_cron(my_task, '0 9 * * *', name='每日任务')")
        print("   ")
        print("   # 每2秒执行 (6字段格式)")
        print("   schedule_cron(my_task, '*/2 * * * * *', name='每2秒任务')")
        print("   ")
        print("   start_scheduler()")
        
        print("\n   # 装饰器用法")
        print("   from pyadvincekit import cron_task, interval_task, scheduled_task, TaskType")
        print("   ")
        print("   # Cron 装饰器")
        print("   @cron_task('*/5 * * * *', name='定期任务')  # 每5分钟")
        print("   def periodic_task():")
        print("       print('定期任务执行了！')")
        print("   ")
        print("   @cron_task('*/2 * * * * *', name='高频任务')  # 每2秒")
        print("   def high_frequency_task():")
        print("       print('高频任务执行了！')")
        print("   ")
        print("   # 间隔装饰器")  
        print("   @interval_task(seconds=300, name='间隔任务')  # 每5分钟")
        print("   def interval_task_example():")
        print("       print('间隔任务执行了！')")
        print("   ")
        print("   # 通用装饰器")
        print("   @scheduled_task(")
        print("       name='复杂任务',")
        print("       task_type=TaskType.CRON,")
        print("       cron_expression='0 9-17 * * 1-5',  # 工作时间")
        print("       max_retries=3")
        print("   )")
        print("   def business_hours_task():")
        print("       print('工作时间任务执行了！')")
        print("   ")
        print("   # 特殊表达式装饰器")
        print("   @cron_task('@daily', name='每日任务')")
        print("   def daily_task():")
        print("       print('每日任务执行了！')")
        
        print("\n   # 表达式验证")
        print("   from pyadvincekit.utils import validate_cron_expression")
        print("   ")
        print("   if validate_cron_expression('0 9 * * *'):")
        print("       print('表达式有效')")

def main():
    """主演示函数"""
    print("🎯 PyAdvanceKit 完整 Cron 表达式支持演示")
    print("=" * 80)
    
    try:
        # 基础解析演示
        demo_cron_parsing()
        
        # 验证演示
        demo_cron_validation()
        
        # 下次执行时间计算
        demo_next_run_calculation()
        
        # 高级功能演示
        demo_advanced_cron_features()
        
        # 装饰器用法演示
        decorator_tasks = demo_decorator_usage()
        
        # 调度器集成演示
        demo_cron_scheduler_integration()
        
        # 使用指南
        CronUsageGuide.print_usage_guide()
        
        print("\n🎉 Cron 表达式支持演示完成！")
        print("\n💡 总结:")
        print("   ✅ 完整支持标准 cron 表达式 (5字段)")
        print("   ✅ 支持扩展 cron 表达式 (6字段，包含秒)")
        print("   ✅ 支持特殊表达式 (@daily, @hourly 等)")
        print("   ✅ 与 PyAdvanceKit 调度器无缝集成")
        print("   ✅ 提供表达式验证和下次执行时间计算")
        print("   ✅ 支持复杂的时间规则和步长")
        print("   ✅ 支持三种装饰器: @cron_task, @interval_task, @scheduled_task")
        print("   ✅ 优雅的装饰器语法，简化任务定义")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保停止调度器
        try:
            stop_scheduler()
            print("\n🛑 调度器已停止")
        except:
            pass

if __name__ == "__main__":
    main()
