#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import onecite

# 设置详细日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    print("🔍 开始分析33个引用的测试结果...")
    
    # 读取测试文件
    with open('test_33_references.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 测试文件包含 {len(content.strip().split(chr(10)+chr(10)))} 个引用")
    
    # 处理引用
    result = onecite.process_references(
        content, 
        'txt', 
        'journal_article_full', 
        'bibtex', 
        lambda x: 0  # 自动选择第一个候选
    )
    
    # 分析结果
    total = result["report"]["total"]
    succeeded = result["report"]["succeeded"]
    failed = total - succeeded
    
    print(f"\n📊 处理结果:")
    print(f"总计: {total}")
    print(f"成功: {succeeded} ({succeeded/total*100:.1f}%)")
    print(f"失败: {failed} ({failed/total*100:.1f}%)")
    
    # 分析失败的引用
    if "failed_entries" in result["report"]:
        print(f"\n❌ 失败的引用分析:")
        for i, failed_entry in enumerate(result["report"]["failed_entries"][:5]):  # 只显示前5个
            print(f"{i+1}. {failed_entry.get('raw_text', 'Unknown')[:100]}...")
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    main()
