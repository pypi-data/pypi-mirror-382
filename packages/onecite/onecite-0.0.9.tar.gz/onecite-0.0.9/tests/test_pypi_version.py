#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试从 PyPI 安装的新版本 onecite 0.0.6
"""

import subprocess
import sys

def test_pypi_version():
    """测试 PyPI 版本的功能"""

    print("=== 测试 PyPI 版本 onecite 0.0.6 ===")

    # 测试版本号
    try:
        import onecite
        print(f"✅ 版本: {onecite.__version__}")
        print(f"✅ 作者: {onecite.__author__}")
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

    # 测试命令行工具
    print("\n--- 测试命令行工具 ---")

    # 测试帮助信息
    try:
        result = subprocess.run([sys.executable, "-m", "onecite.cli", "--help"],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CLI 帮助信息正常")
            print("帮助信息预览:")
            print(result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
        else:
            print(f"❌ CLI 帮助失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ CLI 测试失败: {e}")
        return False

    # 测试智能搜索功能
    print("\n--- 测试智能搜索功能 ---")

    test_input = """10.1038/nature14539
Attention is all you need
BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding"""

    try:
        with open("test_refs.txt", "w", encoding="utf-8") as f:
            f.write(test_input)

        # 测试处理功能
        result = subprocess.run([
            sys.executable, "-m", "onecite.cli",
            "process", "test_refs.txt",
            "--quiet"
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ 智能搜索功能正常")
            print("输出预览:")
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines[:5]:  # 只显示前5行
                print(f"  {line}")
            if len(output_lines) > 5:
                print(f"  ... (总共 {len(output_lines)} 行)")
        else:
            print(f"❌ 搜索功能失败: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ 搜索测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        try:
            import os
            if os.path.exists("test_refs.txt"):
                os.remove("test_refs.txt")
        except:
            pass

    # 测试 Python API
    print("\n--- 测试 Python API ---")

    try:
        from onecite import process_references

        def simple_callback(candidates):
            return 0 if candidates else -1

        result = process_references(
            input_content="10.1038/nature14539",
            input_type="txt",
            template_name="journal_article_full",
            output_format="bibtex",
            interactive_callback=simple_callback
        )

        if result and result.get('results'):
            print("✅ Python API 正常")
            print("API 输出示例:")
            print(result['results'][0][:200] + "..." if len(result['results'][0]) > 200 else result['results'][0])
        else:
            print("❌ Python API 失败")
            return False

    except Exception as e:
        print(f"❌ API 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n🎉 所有测试通过！PyPI 版本 onecite 0.0.6 工作正常！")
    return True

if __name__ == "__main__":
    success = test_pypi_version()
    if not success:
        sys.exit(1)



