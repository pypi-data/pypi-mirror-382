#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基本的 OneCite 测试脚本
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_import():
    """测试基本导入"""
    try:
        from onecite import process_references
        print("✅ OneCite 模块导入成功")
        return True
    except Exception as e:
        print(f"❌ OneCite 模块导入失败: {e}")
        return False

def test_readme_example():
    """测试 README 中的基本示例"""
    try:
        from onecite import process_references
        
        # README 中的示例内容
        input_content = """10.1038/nature14539

Attention is all you need
Vaswani et al.
NIPS 2017"""
        
        # 定义非交互式回调函数
        def auto_select_callback(candidates):
            # 自动选择第一个候选项
            return 0 if candidates else -1
        
        print("🔄 开始处理 README 示例...")
        
        result = process_references(
            input_content=input_content,
            input_type="txt",
            template_name="journal_article_full",
            output_format="bibtex",
            interactive_callback=auto_select_callback
        )
        
        print("✅ README 示例处理成功")
        print(f"📊 处理报告:")
        print(f"  - 总条目: {result['report']['total']}")
        print(f"  - 成功: {result['report']['succeeded']}")
        print(f"  - 失败: {len(result['report']['failed_entries'])}")
        
        if result['results']:
            print("\n📄 生成的引用:")
            for i, citation in enumerate(result['results'], 1):
                print(f"\n{i}. {citation}")
        
        return True
        
    except Exception as e:
        print(f"❌ README 示例处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_apa_format():
    """测试 APA 格式输出"""
    try:
        from onecite import process_references
        
        input_content = "10.1038/nature14539"
        
        def auto_select_callback(candidates):
            return 0 if candidates else -1
        
        print("🔄 测试 APA 格式...")
        
        result = process_references(
            input_content=input_content,
            input_type="txt",
            template_name="journal_article_full",
            output_format="apa",
            interactive_callback=auto_select_callback
        )
        
        print("✅ APA 格式测试成功")
        if result['results']:
            print(f"📄 APA 格式引用: {result['results'][0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ APA 格式测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始 OneCite 基本功能测试\n")
    
    tests = [
        ("基本导入测试", test_basic_import),
        ("README 示例测试", test_readme_example),
        ("APA 格式测试", test_apa_format),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 {test_name}")
        print('='*50)
        
        if test_func():
            passed += 1
        
    print(f"\n{'='*50}")
    print(f"📈 测试总结: {passed}/{total} 通过")
    print('='*50)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
