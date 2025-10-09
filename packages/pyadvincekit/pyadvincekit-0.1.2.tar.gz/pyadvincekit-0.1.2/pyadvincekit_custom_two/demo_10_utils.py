#!/usr/bin/env python3
"""
第二阶段工具类测试

测试新增的日期、HTTP通讯、金额计算工具类
"""

import asyncio
import sys
from datetime import datetime, date
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_date_utils():
    """测试日期工具类"""
    print("📅 测试日期工具类")
    print("-" * 40)
    
    try:
        from pyadvincekit import now, utc_now, format_duration
        from pyadvincekit.utils.date_utils import DateUtils
        
        # 测试当前时间
        current_time = now()
        utc_time = utc_now()
        print(f"✅ 当前时间: {current_time}")
        print(f"✅ UTC时间: {utc_time}")
        
        # 测试日期格式化
        formatted = DateUtils.format_datetime(current_time, DateUtils.FORMAT_CN_DATETIME)
        print(f"✅ 中文格式: {formatted}")
        
        # 测试时间计算
        tomorrow = DateUtils.add_days(current_time, 1)
        print(f"✅ 明天: {tomorrow.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 测试时长格式化
        duration = format_duration(3661.5)  # 1小时1分1.5秒
        print(f"✅ 时长格式化: {duration}")
        
        # 测试工作日判断
        is_workday = DateUtils.is_workday(current_time)
        weekday_name = DateUtils.get_weekday_name(current_time, "cn")
        print(f"✅ 今天是{weekday_name}, {'工作日' if is_workday else '休息日'}")
        
        # 测试年龄计算
        birthday = date(1990, 5, 15)
        age = DateUtils.age_from_birthday(birthday)
        print(f"✅ 1990-05-15出生的年龄: {age}岁")
        
        print("✅ 日期工具类测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 日期工具类测试失败: {e}")
        return False


def test_money_utils():
    """测试金额工具类"""
    print("\n💰 测试金额工具类")
    print("-" * 40)
    
    try:
        from pyadvincekit import Money, MoneyUtils, Currency, money, cny, usd
        
        # 测试基本金额操作
        amount1 = cny("100.50")
        amount2 = cny(50.25)
        total = amount1 + amount2
        print(f"✅ 金额计算: {amount1} + {amount2} = {total}")
        
        # 测试金额格式化
        formatted = total.format(show_symbol=True, thousands_separator=",")
        print(f"✅ 格式化显示: {formatted}")
        
        # 测试金额比较
        print(f"✅ 金额比较: {amount1} > {amount2} = {amount1 > amount2}")
        
        # 测试百分比计算
        discount = MoneyUtils.calculate_percentage(total, 10)  # 10%折扣
        final_price = total - discount
        print(f"✅ 10%折扣: 原价{total}, 折扣{discount}, 实付{final_price}")
        
        # 测试税额计算
        tax_amount, total_with_tax = MoneyUtils.calculate_tax(cny(100), 13)  # 13%增值税
        print(f"✅ 税额计算: 不含税价100元, 税额{tax_amount}, 含税总价{total_with_tax}")
        
        # 测试金额分配
        total_money = cny(100)
        ratios = [3, 2, 5]  # 按3:2:5分配
        allocated = MoneyUtils.allocate_money(total_money, ratios)
        print(f"✅ 金额分配: 100元按3:2:5分配 = {[str(a) for a in allocated]}")
        
        # 测试中文大写
        chinese_amount = MoneyUtils.format_chinese_amount(cny(12345.67))
        print(f"✅ 中文大写: 12345.67元 = {chinese_amount}")
        
        # 测试货币转换
        usd_amount = usd(100)
        cny_converted = MoneyUtils.convert_currency(usd_amount, Currency.CNY, 7.2)
        print(f"✅ 货币转换: {usd_amount} × 7.2 = {cny_converted}")
        
        print("✅ 金额工具类测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 金额工具类测试失败: {e}")
        return False


def test_http_utils():
    """测试HTTP工具类"""
    print("\n🌐 测试HTTP工具类")
    print("-" * 40)
    
    try:
        from pyadvincekit import HTTPClient, HTTPUtils, create_http_client, create_api_client
        
        # 测试URL解析
        url = "https://api.example.com:8080/v1/users?page=1&size=10#section"
        parsed = HTTPUtils.parse_url(url)
        print(f"✅ URL解析: {url}")
        print(f"   - 域名: {parsed['hostname']}")
        print(f"   - 端口: {parsed['port']}")
        print(f"   - 路径: {parsed['path']}")
        print(f"   - 查询参数: {parsed['query_dict']}")
        
        # 测试URL验证
        valid_urls = [
            "https://www.example.com",
            "http://localhost:8080",
            "ftp://files.example.com"
        ]
        invalid_urls = [
            "not-a-url",
            "http://",
            "just-text"
        ]
        
        print("✅ URL验证:")
        for url in valid_urls:
            is_valid = HTTPUtils.is_valid_url(url)
            print(f"   - {url}: {'有效' if is_valid else '无效'}")
        
        for url in invalid_urls:
            is_valid = HTTPUtils.is_valid_url(url)
            print(f"   - {url}: {'有效' if is_valid else '无效'}")
        
        # 测试查询字符串构建
        params = {"page": 1, "size": 10, "status": "active"}
        query_string = HTTPUtils.build_query_string(params)
        print(f"✅ 查询字符串构建: {params} -> {query_string}")
        
        # 测试HTTP客户端创建
        http_client = create_http_client(timeout=30, verify_ssl=True)
        print(f"✅ HTTP客户端创建: {type(http_client).__name__}")
        
        # 测试API客户端创建
        api_client = create_api_client("https://api.example.com", api_key="test-key")
        print(f"✅ API客户端创建: {type(api_client).__name__}")
        
        # 测试JSON解析
        json_text = '{"name": "test", "value": 123}'
        parsed_json = HTTPUtils.safe_json_decode(json_text)
        print(f"✅ JSON解析: {json_text} -> {parsed_json}")
        
        invalid_json = 'not-json-text'
        parsed_invalid = HTTPUtils.safe_json_decode(invalid_json)
        print(f"✅ 无效JSON解析: {invalid_json} -> {parsed_invalid}")
        
        print("✅ HTTP工具类测试通过")
        return True
        
    except Exception as e:
        print(f"❌ HTTP工具类测试失败: {e}")
        return False


async def test_async_http():
    """测试异步HTTP功能"""
    print("\n🔄 测试异步HTTP功能")
    print("-" * 40)
    
    try:
        from pyadvincekit import HTTPClient
        
        # 创建HTTP客户端
        client = HTTPClient(timeout=10)
        print("✅ 异步HTTP客户端创建成功")
        
        # 注意: 这里只是测试客户端创建和方法存在性
        # 实际的HTTP请求需要真实的服务器
        print("✅ 异步方法可用:")
        print(f"   - async_get: {hasattr(client, 'async_get')}")
        print(f"   - async_post: {hasattr(client, 'async_post')}")
        print(f"   - async_put: {hasattr(client, 'async_put')}")
        print(f"   - async_delete: {hasattr(client, 'async_delete')}")
        
        print("✅ 异步HTTP功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 异步HTTP功能测试失败: {e}")
        return False


def test_integration():
    """测试工具类集成使用"""
    print("\n🔗 测试工具类集成使用")
    print("-" * 40)
    
    try:
        from pyadvincekit import now, cny, format_duration, HTTPUtils
        from pyadvincekit.utils.date_utils import DateUtils
        
        # 模拟一个业务场景：订单处理
        print("📋 模拟订单处理场景:")
        
        # 1. 创建订单时间
        order_time = now()
        print(f"   订单创建时间: {DateUtils.format_datetime(order_time, DateUtils.FORMAT_CN_DATETIME)}")
        
        # 2. 计算订单金额
        item_price = cny(99.99)
        quantity = 3
        subtotal = item_price * quantity
        
        # 3. 计算税额
        from pyadvincekit.utils.money_utils import MoneyUtils
        tax_amount, total_amount = MoneyUtils.calculate_tax(subtotal, 13)
        
        print(f"   商品单价: {item_price}")
        print(f"   购买数量: {quantity}")
        print(f"   小计: {subtotal}")
        print(f"   税额(13%): {tax_amount}")
        print(f"   总计: {total_amount}")
        
        # 4. 模拟API调用准备
        api_url = "https://payment.example.com/api/v1/orders"
        order_data = {
            "order_id": "ORD-20250923-001",
            "amount": str(total_amount.amount),
            "currency": total_amount.currency.code,
            "created_at": DateUtils.format_datetime(order_time, DateUtils.FORMAT_ISO)
        }
        
        query_params = {"merchant_id": "12345", "version": "v1"}
        query_string = HTTPUtils.build_query_string(query_params)
        full_url = f"{api_url}?{query_string}"
        
        print(f"   API调用URL: {full_url}")
        print(f"   请求数据: {order_data}")
        
        # 5. 计算处理时长
        import time
        time.sleep(0.1)  # 模拟处理时间
        processing_time = 0.1
        duration_text = format_duration(processing_time)
        print(f"   处理耗时: {duration_text}")
        
        print("✅ 工具类集成使用测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 工具类集成使用测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 PyAdvanceKit 第二阶段工具类测试")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        ("日期工具类", test_date_utils),
        ("金额工具类", test_money_utils),
        ("HTTP工具类", test_http_utils),
        ("异步HTTP功能", test_async_http),
        ("工具类集成", test_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有测试通过！第二阶段工具类功能正常")
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
