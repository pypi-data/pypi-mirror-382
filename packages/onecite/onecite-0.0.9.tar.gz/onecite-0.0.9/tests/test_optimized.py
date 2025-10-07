#!/usr/bin/env python3

import onecite
import logging
import time

# 设置详细日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 测试几个代表性引用验证优化效果
test_cases = [
    "Kurose, J. F., & Ross, K. W. (2021). Computer Networking: A Top-Down Approach (8th ed.). Pearson.",
    "Hellerstein, J. L., et al. (2012). Feedback Control of Computing Systems. John Wiley & Sons.",
    "Gimbel, S., et al. (2017). An assessment of routine health information system data quality in Sofala Province, Mozambique. Population Health Metrics, 15(1), 3."
]

print("🔧 测试优化后的Google Scholar处理")
print("=" * 60)

success_count = 0
total_time = 0

for i, ref in enumerate(test_cases, 1):
    print(f"\n📝 测试 {i}/{len(test_cases)}")
    print(f"引用: {ref[:60]}...")

    start_time = time.time()
    
    try:
        result = onecite.process_references(ref, 'txt', 'journal_article_full', 'bibtex', lambda x: 0)
        
        elapsed = time.time() - start_time
        total_time += elapsed
        
        if result and result.get('results') and result['results'][0] and result['results'][0].strip():
            success_count += 1
            print(f"✅ 成功 (用时: {elapsed:.1f}s)")
            
            # 显示DOI
            bibtex = result['results'][0]
            if 'doi =' in bibtex:
                doi_line = [line for line in bibtex.split('\n') if 'doi =' in line]
                if doi_line:
                    print(f"   {doi_line[0].strip()}")
        else:
            print(f"❌ 失败 (用时: {elapsed:.1f}s)")

    except Exception as e:
        elapsed = time.time() - start_time
        total_time += elapsed
        print(f"❌ 错误: {str(e)} (用时: {elapsed:.1f}s)")

print(f"\n📊 优化测试结果:")
print(f"成功率: {success_count}/{len(test_cases)} ({success_count/len(test_cases)*100:.1f}%)")
print(f"总用时: {total_time:.1f}s")
print(f"平均用时: {total_time/len(test_cases):.1f}s/条")

if success_count >= 2:
    print("🎉 优化有效！Google Scholar处理更稳定")
else:
    print("⚠️ 需要进一步调整参数")
