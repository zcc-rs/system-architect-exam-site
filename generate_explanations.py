#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为所有客观题生成详细的解析
包括：知识点、计算过程、选项分析、原文引用等
"""

import json
import random
from pathlib import Path

# 详细的解析模板库（包含更多题目）
EXPLANATIONS = {
    1: {
        "keyPoints": ["分时操作系统", "系统特性", "多路性/独立性/交互性"],
        "analysis": """【知识点】分时操作系统的四大特点
分时操作系统是将CPU的工作时间划分为许多很短的时间片，轮流为各个终端用户服务。

【四大特点】
1. 多路性 - 多个用户可以同时使用计算机系统
2. 独立性 - 各用户作业独立运行，互不影响  
3. 交互性 - 用户与系统进行人机对话式的交互通信
4. 及时性 - 系统对用户的请求能及时响应和处理

【正确答案分析】B - 独立性、交互性与题干给出的多路性和及时性并列，构成分时系统的四大特点。"""
    },
    
    2: {
        "keyPoints": ["CPU与主存速度不匹配", "高速缓存", "Cache"],
        "analysis": """【知识点】CPU与主存的速度差距问题

【问题背景】CPU速度远快于主存速度（CPU纳秒级，主存微秒级），导致CPU经常等待主存的数据，成为系统瓶颈。

【解决方案】使用高速缓冲存储器（Cache），是位于CPU和主存之间的小容量高速存储器。

【工作原理】
- CPU优先从Cache读取数据（命中率>90%）
- Cache未命中时，从主存取数据并自动复制到Cache
- 存储器三层结构：寄存器 → Cache → 主存

【答案】B"""
    },
    
    5: {
        "keyPoints": ["Amdahl定律", "系统加速比", "可优化比例"],
        "analysis": """【知识点】Amdahl定律（Amdahl's Law）- 系统性能优化的理论极限

【公式】系统加速比 S = 1 / [(1-f) + f/k]
- S = 系统加速比（目标加速倍数）
- f = 可被优化部分所占的比例（0.9）
- k = 该部分的加速倍数（待求）

【求解过程】
5 = 1 / [0.1 + 0.9/k]
0.1 + 0.9/k = 0.2
k = 9

【物理意义】即使矩阵乘法提升9倍，整个系统也只能提升5倍。这体现了优化需要平衡各部分的原理。

【答案】C - 9倍"""
    },
    
    6: {
        "keyPoints": ["进程控制块PCB", "PCB内容", "进程管理"],
        "analysis": """【知识点】进程控制块（Process Control Block, PCB）

【PCB的三部分内容】
1. 进程标识符 - 进程的唯一标识（PID）
2. 控制信息 - 进程状态、优先级、进程队列指针等
3. 现场保护区 - 进程切换时保存的寄存器内容

【关键区分】进程 = 程序块(code) + PCB(管理信息) + 数据块(data)
源代码属于程序块，不属于PCB

【答案】D - 源代码"""
    },
    
    7: {
        "keyPoints": ["页式存储", "位示图", "内存管理"],
        "analysis": """【知识点】页式存储管理中的位示图（Bitmap）

【计算过程】
页框数 = 32GB / 8KB = 2^35字节 / 2^13字节 = 2^22 = 4,194,304个
位示图 = 2^22位 = 2^19字节 = 512KB

【答案】D - 512 KB"""
    },

    13: {
        "keyPoints": ["软件文档体系", "系统文档", "用户文档"],
        "analysis": """【知识点】软件文档分类体系

【文档体系结构】根据IEEE标准，软件文档分为两大类：
1. 系统文档 - 针对开发人员：架构、设计、代码等
2. 用户文档 - 针对使用者：手册、操作指南等

【为什么选A】
- A "用户文档" ✓ 与系统文档平级
- B "测试报告" ✗ 属于系统文档子类
- C "部署指南" ✗ 属于运维文档
- D "设计文档" ✗ 属于系统文档子类

【答案】A - 用户文档"""
    },
}

def generate_default_explanation(question):
    """为没有预定义的题目生成默认解析"""
    correct_opt = question.get('options', {}).get(question['answer'], '')
    topic = question.get('topic', '综合知识')
    
    return {
        'keyPoints': [topic],
        'analysis': f"【题目考查】{topic}\n\n【正确答案】{question['answer']} - {correct_opt}\n\n[根据标准答案，该选项最为准确。详细解析待完善]",
        'source': '标准答案'
    }

def generate_all_explanations():
    """为所有题目生成解析"""
    
    qb_path = Path('data/question-bank.js')
    content = qb_path.read_text(encoding='utf-8')
    json_str = content.replace('window.QUESTION_BANK = ', '').strip().rstrip(';').strip()
    bank = json.loads(json_str)
    
    modified_count = 0
    default_count = 0
    
    for paper in bank['papers'][:2]:  # 只处理前两份（客观题）
        if paper['type'] != 'objective':
            continue
        
        for question in paper['questions']:
            q_num = question['number']
            
            if q_num in EXPLANATIONS:
                exp = EXPLANATIONS[q_num]
                question['explanation'] = {
                    'keyPoints': exp['keyPoints'],
                    'analysis': exp['analysis'].strip(),
                    'source': '知识库'
                }
                modified_count += 1
            else:
                # 生成默认解析
                question['explanation'] = generate_default_explanation(question)
                default_count += 1
    
    # 保存回文件
    output = 'window.QUESTION_BANK = ' + json.dumps(bank, ensure_ascii=False, indent=2) + ';'
    qb_path.write_text(output, encoding='utf-8')
    
    print(f"✓ 成功添加{modified_count}题的详细解析")
    print(f"✓ 为{default_count}题生成了默认框架解析")
    print(f"✓ 总计处理{modified_count + default_count}道题")

if __name__ == '__main__':
    generate_all_explanations()
