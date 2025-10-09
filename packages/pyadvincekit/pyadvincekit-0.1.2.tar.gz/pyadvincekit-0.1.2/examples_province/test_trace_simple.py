#!/usr/bin/env python3
"""
最简单的TraceId测试

测试核心跟踪功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_basic_trace():
    """测试基本跟踪功能"""
    print("🔍 测试基本跟踪功能")
    print("-" * 40)
    
    try:
        from pyadvincekit.core.trace import TraceContext, TraceManager
        
        # 测试基本跟踪上下文
        with TraceContext(user_id="user123", request_id="req456") as trace:
            print(f"✅ TraceId: {trace.trace_id}")
            print(f"✅ SpanId: {trace.span_id}")
            print(f"✅ UserId: {trace.user_id}")
            print(f"✅ RequestId: {trace.request_id}")
            
            # 测试获取当前上下文
            current_trace_id = TraceManager.get_current_trace_id()
            current_span_id = TraceManager.get_current_span_id()
            context = TraceManager.get_current_context()
            
            print(f"✅ 当前TraceId: {current_trace_id}")
            print(f"✅ 当前SpanId: {current_span_id}")
            print(f"✅ 当前上下文: {context}")
        
        print("✅ 基本跟踪功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 基本跟踪功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trace_generation():
    """测试ID生成"""
    print("\n🎯 测试ID生成")
    print("-" * 40)
    
    try:
        from pyadvincekit.core.trace import TraceManager
        
        # 测试ID生成
        trace_id = TraceManager.generate_trace_id()
        span_id = TraceManager.generate_span_id()
        
        print(f"✅ 生成的TraceId: {trace_id}")
        print(f"✅ 生成的SpanId: {span_id}")
        
        # 验证ID格式
        assert len(trace_id) == 36, "TraceId应该是36位UUID"
        assert len(span_id) == 16, "SpanId应该是16位"
        
        print("✅ ID生成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ ID生成测试失败: {e}")
        return False


def test_trace_context():
    """测试跟踪上下文"""
    print("\n📊 测试跟踪上下文")
    print("-" * 40)
    
    try:
        from pyadvincekit.core.trace import TraceContext, TraceManager
        
        # 测试嵌套上下文
        with TraceContext(user_id="user123") as parent:
            print(f"✅ 父上下文 - TraceId: {parent.trace_id}")
            
            with TraceContext(parent_span_id=parent.span_id) as child:
                print(f"✅ 子上下文 - TraceId: {child.trace_id}")
                print(f"✅ 子上下文 - 父SpanId: {child.parent_span_id}")
                
                # 验证父子关系
                assert child.trace_id == parent.trace_id, "子跟踪应该继承父跟踪的TraceId"
                assert child.parent_span_id == parent.span_id, "子跟踪的父SpanId应该是父跟踪的SpanId"
                print("✅ 父子关系验证通过")
        
        print("✅ 跟踪上下文测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 跟踪上下文测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 PyAdvanceKit TraceId 简单测试")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        ("基本跟踪功能", test_basic_trace),
        ("ID生成", test_trace_generation),
        ("跟踪上下文", test_trace_context)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
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
        print("🎉 所有测试通过！TraceId跟踪功能正常")
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
