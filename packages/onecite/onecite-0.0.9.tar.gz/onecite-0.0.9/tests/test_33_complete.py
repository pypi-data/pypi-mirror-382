#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整的33个引用测试脚本
测试改进后的OneCite系统的性能
"""

import logging
import time
import onecite
from typing import Dict, List

# 设置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_33_results.log'),
        logging.StreamHandler()
    ]
)

def load_test_references() -> str:
    """加载33个测试引用"""
    references = [
        "AbouZahr, C., & Boerma, T. (2005). Health information systems: the foundations of public health. Bulletin of the World Health Organization, 83(8), 578–583.",
        "Aqil, A., Lippeveld, T., & Hozumi, D. (2016). PRISM framework: a paradigm shift for designing, strengthening and evaluating routine health information systems. Health Policy and Planning, 31(5), 623-631.",
        "Baker, M. (2016). 1,500 scientists lift the lid on reproducibility. Nature, 533(7604), 452–454.",
        "Byrne, E., et al. (2022). Routine use of data from the District Health Information System 2 (DHIS2): a scoping review. BMC Health Services Research, 22(1), 1234.",
        "Clopper, C. J., & Pearson, E. S. (1934). The use of confidence or fiducial limits illustrated in the case of the binomial. Biometrika, 26(4), 404–413.",
        "Dean, J., & Barroso, L. A. (2013). The Tail at Scale. Communications of the ACM, 56(2), 74–80.",
        "Dehnavieh, R., et al. (2019). The District Health Information System (DHIS2): A literature review and meta-synthesis of its strengths and operational challenges. Health Information Management Journal, 48(2), 55-67.",
        "Feng, S., Hategeka, C., & Grépin, K. A. (2021). Addressing missing values in routine health information system data: an evaluation of imputation methods using data from the Democratic Republic of the Congo during the COVID-19 pandemic. Population Health Metrics, 19(1), 47.",
        "Gilbert, S., & Lynch, N. (2002). Brewer's conjecture and the feasibility of consistent, available, partition-tolerant web services. ACM SIGACT News, 33(2), 51-59.",
        "Gimbel, S., et al. (2017). An assessment of routine health information system data quality in Sofala Province, Mozambique. Population Health Metrics, 15(1), 3.",
        "Hellerstein, J. L., et al. (2012). Feedback Control of Computing Systems. John Wiley & Sons.",
        "Hong, Y. A. (2017). The digital divide and health. Health Care Informatics: A Skills-Based Resource, 225-236.",
        "Hoxha, K., et al. (2022). Understanding the challenges in the production and use of routine health information system data in low- and middle-income countries: A systematic review. Health Information Management Journal, 51(1), 3-15.",
        "Hung, Y. W., Grépin, K. A., et al. (2020). Using routine health information data for research in low- and middle-income countries: A systematic review. BMC Health Services Research, 20(1), 790.",
        "Ince, D. C., Hatton, L., & Graham-Cumming, J. (2012). The case for open computer programs. Nature, 482(7386), 485–488.",
        "IETF. (2022). HTTP Semantics. RFC 9110.",
        "Kurose, J. F., & Ross, K. W. (2021). Computer Networking: A Top-Down Approach (8th ed.). Pearson.",
        "Kyomba, G. K., et al. (2022). Assessing routine health information system performance during the 10th Ebola outbreak in the Democratic Republic of the Congo: A qualitative study in North Kivu. PLOS Global Public Health, 2(5), e0000429.",
        "Little, R. J., & Rubin, D. B. (2019). Statistical Analysis with Missing Data (3rd ed.). Wiley.",
        "Maina, T., et al. (2019). A systematic review of the operational challenges of the district health information system 2 (DHIS2) in sub-Saharan Africa. BMC Public Health, 19(1), 1-10.",
        "Mars, M. (2013). Telemedicine and advances in urban and rural healthcare delivery in Africa. Progress in Cardiovascular Diseases, 56(3), 326-335.",
        "Moucheraud, C., et al. (2017). Quality of routine health data: a comparison of data from facilities and a population-based survey in Malawi. Global Health Action, 10(1), 1294813.",
        "Mutale, W., et al. (2013). Improving health information systems for decision making across five sub-Saharan African countries: implementation strategies from the African Health Initiative. BMC Health Services Research, 13(2), S9.",
        "Nosek, B. A., et al. (2015). Promoting an open research culture. Science, 348(6242), 1422-1425.",
        "Oppenheimer, D., Ganapathi, A., & Patterson, D. A. (2003). Why do internet services fail, and what can be done about it?. SIGOPS Operating Systems Review, 37(3), 1-1.",
        "Peng, R. D. (2011). Reproducible Research in Computational Science. Science, 334(6060), 1226-1227.",
        "Ramalho, L. (2022). Fluent Python: Clear, Concise, and Effective Programming (2nd ed.). O'Reilly Media.",
        "Sterne, J. A. C., et al. (2009). Multiple imputation for missing data in epidemiological and clinical research: potential and pitfalls. BMJ, 338, b2393.",
        "Tanenbaum, A. S., & Wetherall, D. J. (2021). Computer Networks (6th ed.). Pearson.",
        "Weber, K., Otto, B., & Österle, H. (2009). One size does not fit all—a contingency approach to data governance. Journal of Data and Information Quality, 1(1), 1-27.",
        "Wilkinson, M. D., et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. Scientific Data, 3, 160018.",
        "World Health Organization. (2017). DQR: Data Quality Review: A modular approach. Geneva: World Health Organization.",
        "World Health Organization. (2018). Data Quality Review (DQR) Toolkit. Geneva: World Health Organization."
    ]

    return '\n\n'.join(references)

def analyze_results(results: Dict, test_references: List[str]) -> Dict:
    """分析测试结果"""
    analysis = {
        'total': len(test_references),
        'successful': 0,
        'failed': 0,
        'success_rate': 0.0,
        'failed_references': [],
        'success_details': [],
        'processing_time': 0,
        'average_time_per_ref': 0
    }

    if 'report' in results:
        report = results['report']
        analysis['successful'] = report.get('succeeded', 0)
        analysis['failed'] = analysis['total'] - analysis['successful']
        analysis['success_rate'] = (analysis['successful'] / analysis['total']) * 100

        if 'failed_entries' in report:
            analysis['failed_references'] = [entry.get('raw_text', '') for entry in report['failed_entries']]

    # 分析成功处理的引用
    if 'results' in results and results['results']:
        for i, result in enumerate(results['results']):
            if result and result.strip():
                analysis['success_details'].append({
                    'index': i + 1,
                    'bibtex': result,
                    'length': len(result)
                })

    return analysis

def print_analysis(analysis: Dict):
    """打印分析结果"""
    print("\n🎯 OneCite 改进版测试结果分析")
    print("=" * 60)
    print(f"📊 总体统计:")
    print(f"   总引用数: {analysis['total']}")
    print(f"   成功处理: {analysis['successful']}")
    print(f"   失败处理: {analysis['failed']}")
    print(f"   成功率: {analysis['success_rate']:.1f}%")
    if analysis['processing_time'] > 0:
        print(f"   处理时间: {analysis['processing_time']:.2f}秒")
        print(f"   平均每条时间: {analysis['average_time_per_ref']:.2f}秒")
    print("\n✅ 成功处理的引用详情:")
    for detail in analysis['success_details'][:10]:  # 只显示前10个
        print(f"   {detail['index']}. {detail['bibtex'][:100]}...")

    if analysis['failed_references']:
        print(f"\n❌ 失败的引用 ({len(analysis['failed_references'])}个):")
        for i, ref in enumerate(analysis['failed_references'][:5]):  # 只显示前5个
            print(f"   {i+1}. {ref[:100]}...")

    print("\n🔧 改进点总结:")
    print("   ✅ 增强的CrossRef搜索策略")
    print("   ✅ 智能Google Scholar重试机制")
    print("   ✅ 改进的候选者评分算法")
    print("   ✅ 健康信息系统领域优化")
    print("   ✅ 更好的错误处理和超时管理")

def main():
    print("🚀 开始OneCite改进版完整测试...")

    # 加载测试数据
    test_content = load_test_references()
    print(f"📚 已加载 {len(test_content.split(chr(10)+chr(10)))} 个测试引用")

    # 记录开始时间
    start_time = time.time()

    try:
        # 执行测试
        print("\n⚙️ 正在处理引用...")
        result = onecite.process_references(
            test_content,
            'txt',
            'journal_article_full',
            'bibtex',
            lambda x: 0  # 自动选择第一个候选
        )

        # 计算处理时间
        processing_time = time.time() - start_time

        # 分析结果
        analysis = analyze_results(result, test_content.split('\n\n'))
        analysis['processing_time'] = processing_time
        analysis['average_time_per_ref'] = processing_time / analysis['total']

        # 输出结果
        print_analysis(analysis)

        # 保存详细结果
        with open('test_33_detailed_results.txt', 'w', encoding='utf-8') as f:
            f.write("OneCite 改进版测试详细结果\n")
            f.write("=" * 50 + "\n")
            f.write(f"成功率: {analysis['success_rate']:.1f}%\n")
            f.write(f"处理时间: {processing_time:.2f}秒\n")
            f.write(f"平均每条时间: {analysis['average_time_per_ref']:.2f}秒\n\n")

            f.write("成功处理的引用:\n")
            for detail in analysis['success_details']:
                f.write(f"{detail['index']}. {detail['bibtex']}\n\n")

            if analysis['failed_references']:
                f.write("\n失败的引用:\n")
                for i, ref in enumerate(analysis['failed_references']):
                    f.write(f"{i+1}. {ref}\n")

        print("\n💾 详细结果已保存到 test_33_detailed_results.txt")

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
