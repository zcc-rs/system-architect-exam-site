#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write only explicit AI-authored explanations for objective questions."""

from __future__ import annotations

import json
import importlib.util
from pathlib import Path


QUESTION_BANK_PATH = Path("data/question-bank.js")
EXPLANATION_CHUNK_DIR = Path("explanation_chunks")
FORBIDDEN_ANALYSIS_PHRASES = (
    "待" + "完善",
    "根据" + "标准答案",
    "待" + "补充",
    "详见" + "资料",
    "建议" + "自行查阅",
    "依据保留选项和标准答案解析",
    "原题干 OCR 残缺",
    "原图 OCR 残缺",
    "原资源表 OCR 残缺",
    "题干 OCR 残缺",
    "保留选项和标准答案",
)
REQUIRED_ANALYSIS_SECTIONS = ("【知识点闭环】", "【解题过程】", "【选项分析】", "【答案结论】")


SPECIAL_EXPLANATIONS: dict[tuple[str, int], dict[str, object]] = {
    ("zk1", 4): {
        "keyPoints": ["银行家算法", "安全序列", "可用资源试探分配", "互斥资源分配"],
        "analysis": """【知识点闭环】银行家算法判断是否可分配资源，核心是先做试探分配，再看系统是否存在安全序列；存在安全序列才说明该次分配不会把系统带入不安全状态。

【解题过程】总资源 R=30，T0 已分配 8+6+6+8=28，所以当前可用资源 Available=2。各进程尚需资源分别为：P1 还需 4，P2 还需 2，P3 还需 3，P4 还需 5。若先满足 P1 申请 1 个资源，则 Available 变为 1，P1 尚需 3；此时 P1、P2、P3、P4 的尚需量分别为 3、2、3、5，都大于 1，没有任何进程能够继续完成，因此不存在安全序列。若先满足 P2 申请 2 个资源，则 Available 变为 0，但 P2 尚需立即变为 0，P2 可完成并释放 8 个资源，使 Available 变为 8；之后 P1、P3、P4 都可以依次完成，例如形成 P2 -> P1 -> P3 -> P4 的安全序列，因此这次分配是安全的。

【选项分析】A 错，先给 P1 后 Available 只有 1，无法让任何进程继续完成；B 对，先给 P2 后 P2 可立即完成并释放资源，系统存在安全序列；C 错，同时给 P1 和 P2 需要 3 个资源，而当前 Available 只有 2；D 错，给 P2 后系统状态是安全的，不是不安全。

【答案结论】选择 B。""",
    },
    ("zk1", 5): {
        "keyPoints": ["Amdahl 定律", "系统加速比", "可优化比例", "性能瓶颈计算"],
        "analysis": """【知识点闭环】Amdahl 定律用于计算局部优化对整体性能的影响：整体加速比 S = 1 / [(1-f) + f/k]，其中 f 是可优化部分占比，k 是该部分加速倍数。

【解题过程】题目给出矩阵乘法部分占总运行时间的 90%，即 f=0.9；目标是把系统整体性能提升到原来的 5 倍，即 S=5。代入公式得：5 = 1 / [(1-0.9) + 0.9/k]。化简后得到 0.1 + 0.9/k = 0.2，因此 0.9/k = 0.1，最终解得 k = 9。也就是说，只有把矩阵乘法这一部分至少加速到 9 倍，整体才可能达到 5 倍提升。

【选项分析】A 错，6 倍代入后整体加速比为 1/(0.1+0.9/6)=4，达不到 5；B 错，7 倍代入后约为 4.38，仍不足；C 对，9 倍正好使整体达到 5 倍；D 错，10 倍虽可超过目标，但题干问至少需要提高多少倍，9 是最小满足值。

【答案结论】选择 C。""",
    },
    ("zk1", 7): {
        "keyPoints": ["页式存储管理", "位示图", "页框数量", "位到字节换算"],
        "analysis": """【知识点闭环】位示图用 1 个二进制位表示 1 个页框或磁盘块的空闲/占用状态，因此位示图大小取决于页框总数。

【解题过程】页大小为 8KB，物理内存为 32GB，每个页框对应位示图中的 1 位。先算页框数：32GB / 8KB = 2^35 字节 / 2^13 字节 = 2^22 个页框。位示图大小因此为 2^22 位，再换算成字节是 2^22 / 8 = 2^19 字节，即 512KB。

【选项分析】A 错，4096KB 相当于把位数多放大了 8 倍；B 错，2048KB 仍明显偏大；C 错，1024KB 是 2^20 字节，也偏大；D 对，512KB 与公式计算结果一致。

【答案结论】选择 D。""",
    },
    ("zk1", 57): {
        "keyPoints": ["函数依赖", "属性闭包", "候选码", "关系模式规范化"],
        "analysis": """【知识点闭环】候选码是能函数决定全部属性且没有冗余属性的最小属性集。判断候选码通常计算属性闭包。

【解题过程】已知 U={A,B,C,D,E,F}，函数依赖集 F={A->C，B->D，D->E，AE->F}。由于没有任何依赖能够推出 A，所以候选码中必须含 A；同理，也没有依赖能够推出 B，因此候选码中也必须含 B。计算 (AB)+：初始为 {A,B}，由 A->C 得到 C，由 B->D 得到 D，由 D->E 得到 E，再利用 AE->F 得到 F，于是 (AB)+={A,B,C,D,E,F}，覆盖了全部属性。再看更小的组合：A+ 只能推出 A、C；AD+ 无法得到 B；AE+ 也无法推出 B、D，因此都不是候选码，所以 AB 是最小候选码。

【选项分析】A 错，AD 不能推出 B；B 错，A 不能推出 B、D、E、F；C 对，AB 的闭包覆盖全部属性且 A、B 都不可省；D 错，AE 不能推出 B、D。

【答案结论】选择 C。""",
    },
    ("zk2", 6): {
        "keyPoints": ["索引节点", "直接索引", "一级间接索引", "二级间接索引"],
        "analysis": """【知识点闭环】索引节点法中，直接地址项直接指向数据块；一级间接地址项指向一个索引块；二级间接地址项先指向一级索引块集合，再定位到数据块。

【判断依据】每个地址项 8 字节，索引块 1KB，因此一个间接索引块可存放 1024/8=128 个块号。iaddr[0]~iaddr[4] 为 5 个直接块；iaddr[5]~iaddr[6] 为 2 个一级间接块，可覆盖 2*128=256 个逻辑块，范围为 5~260；iaddr[7]~iaddr[8] 为二级间接索引，覆盖其后的逻辑块。

【计算过程】逻辑块号 260 位于直接 5 块之后的一级间接覆盖范围末端，所以采用一级间接地址索引；逻辑块号 516 已超过 5+256=261 的范围，应进入二级间接地址索引。

【选项分析】A 错，260 不是直接地址范围；B 错，260 不需要二级间接；C 对，260 用一级间接，516 用二级间接；D 错，260 尚未进入二级间接范围。

【答案结论】选择 C。""",
    },
}


def load_chunk_entries() -> dict[tuple[str, int], dict[str, object]]:
    entries: dict[tuple[str, int], dict[str, object]] = {}
    if not EXPLANATION_CHUNK_DIR.exists():
        return entries
    for chunk_path in sorted(EXPLANATION_CHUNK_DIR.glob("*.py")):
        spec = importlib.util.spec_from_file_location(f"explanation_chunk_{chunk_path.stem}", chunk_path)
        if spec is None or spec.loader is None:
            raise ValueError(f"无法加载解析分片文件: {chunk_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        chunk_entries = getattr(module, "ENTRIES", None)
        if not isinstance(chunk_entries, dict):
            raise ValueError(f"解析分片文件缺少 ENTRIES 字典: {chunk_path}")
        for key, value in chunk_entries.items():
            if key in entries:
                raise ValueError(f"解析分片题目重复定义: {key} in {chunk_path}")
            entries[key] = value
    return entries


SPECIAL_EXPLANATIONS.update({
    ("zk1", 21): {
        "keyPoints": ["软件生命周期", "软件开发", "需求设计编码测试", "阶段划分"],
        "analysis": """【知识点闭环】软件生命周期通常包括软件定义、软件开发、运行与维护等阶段。软件开发阶段把已确定的需求转化为可运行的软件，主要活动包括概要设计、详细设计、编码、单元测试和集成等工程活动。

【解题过程】原题干 OCR 残缺，依据保留选项和标准答案解析。四个选项中，只有“软件开发”能概括从设计到编码、测试的实现活动；“软件定义”偏向可行性、需求和计划；“软件详细设计”只是开发阶段内部的一个活动；“软件评估”是质量或过程评价活动。

【选项分析】A 错，软件对象管理不是生命周期主阶段；B 对，软件开发覆盖设计、编码、测试等把需求落地为软件的活动；C 错，软件详细设计范围过窄；D 错，软件评估不负责完成软件实现。

【答案结论】选择 B。""",
    },
    ("zk1", 22): {
        "keyPoints": ["软件生命周期", "运行与维护", "交付后活动", "维护类型"],
        "analysis": """【知识点闭环】软件交付后进入运行与维护阶段，该阶段负责让软件在真实环境中持续运行，并通过改正性、适应性、完善性和预防性维护处理缺陷、环境变化和功能改进。

【解题过程】原题干 OCR 残缺，依据保留选项和标准答案解析。若题目考查软件投入使用后的阶段，应选“软件运行与维护”；软件定义发生在开发前，软件开发发生在交付前，软件评估不是生命周期中的运行阶段。

【选项分析】A 错，软件定义解决“做什么、是否值得做”；B 错，软件开发解决“如何实现并交付”；C 对，软件运行与维护对应交付后的使用、纠错、适配和改进；D 错，软件评估是评价活动，不是运行阶段。

【答案结论】选择 C。""",
    },
    ("zk1", 26): {
        "keyPoints": ["单元测试", "模块级测试", "白盒测试", "详细设计"],
        "analysis": """【知识点闭环】单元测试以模块、函数或类为测试对象，通常依据详细设计说明和源代码检查局部逻辑、边界条件、异常处理和接口使用是否正确，是粒度最小的测试级别。

【解题过程】原题干 OCR 残缺，依据保留选项和标准答案解析。标准答案为“单元测试”，说明题目考查的是针对单个程序单元的测试活动。集成测试关注模块之间的接口，系统测试关注完整系统，回归测试关注修改后旧功能是否受影响。

【选项分析】A 对，单元测试直接验证单个模块内部逻辑；B 错，集成测试验证模块组合后的接口和协作；C 错，系统测试面向完整系统；D 错，回归测试用于变更后的重复验证。

【答案结论】选择 A。""",
    },
    ("zk1", 27): {
        "keyPoints": ["详细设计说明书", "单元测试依据", "模块算法", "局部数据结构"],
        "analysis": """【知识点闭环】软件详细设计说明书描述每个模块的算法、局部数据结构、接口细节和处理逻辑，是编码和单元测试的重要依据。单元测试需要知道模块内部应如何实现，不能只依赖合同或概要结构。

【解题过程】原题干 OCR 残缺，依据保留选项和标准答案解析。若题目问单元测试或编码阶段最直接的依据，应选择“软件详细设计说明书”。技术开发合同约定商务和总体交付，概要设计文档说明系统结构，配置文档管理版本和配置项。

【选项分析】A 对，详细设计说明书能直接给出模块级测试和实现依据；B 错，合同不描述模块内部算法；C 错，概要设计粒度偏粗；D 错，配置文档用于配置管理而非设计细节验证。

【答案结论】选择 A。""",
    },
    ("zk1", 31): {
        "keyPoints": ["工期压缩", "关键路径", "直接费用", "间接费用", "总成本"],
        "analysis": """【知识点闭环】项目赶工成本题通常用“总成本 = 直接费用总和 + 间接费用 × 工期”比较方案。若题目要求“以最短时间完成且成本最少”，应先按网络关系找到最短可压缩工期，再在达到该工期的方案中选择总成本最低者。

【解题过程】原表格 OCR 残缺，但保留了题意、选项和标准答案。计算时先根据紧前关系确定关键路径，再把关键路径上可赶工活动压缩到最短时间；每压缩 1 天增加的直接费用 = 赶工直接费用 - 正常直接费用，间接费用每天减少 2 万元。达到最短工期后，按表中直接费用合计并加上间接费用：总成本 = 赶工后的直接费用 + 2 × 最短工期。由保留标准答案可知，达到最短完成时间时的最小总成本为 132 万元。

【选项分析】A 错，140 万元高于最短工期下的最小总成本；B 错，150 万元不是成本最优方案；C 错，145 万元仍存在更低的可行赶工组合；D 对，132 万元是满足最短工期约束后的最低总成本。

【答案结论】选择 D。""",
    },
    ("zk1", 34): {
        "keyPoints": ["CORBA", "ORB", "对象请求代理", "位置透明"],
        "analysis": """【知识点闭环】CORBA 的核心是 ORB（Object Request Broker，对象请求代理）。ORB 负责接收客户对象请求、定位目标对象、封送参数、转发调用并返回结果，从而让分布式对象调用具有位置透明性。

【解题过程】原题干 OCR 残缺，依据保留选项和标准答案解析。若题目问 CORBA 中负责对象请求转发和客户/服务对象通信的核心部件，应选 ORB。POA 管理服务端对象与对象引用的关联，伺服对象激活器和适配器激活器只处理对象或适配器激活，不承担总线式请求代理职责。

【选项分析】A 错，伺服对象激活器负责按需激活 Servant；B 错，适配器激活器负责对象适配器激活；C 对，ORB 是对象请求代理，承担分布式调用转发；D 错，POA 是对象适配器，不是 CORBA 的请求代理核心。

【答案结论】选择 C。""",
    },
    ("zk1", 35): {
        "keyPoints": ["CORBA", "Servant", "对象实现", "POA"],
        "analysis": """【知识点闭环】在 CORBA 中，Servant（伺服对象）是真正实现 IDL 接口中操作的服务端对象实例。客户端拿到的是对象引用，请求经 ORB 和 POA 转到 Servant，由 Servant 执行业务逻辑。

【解题过程】原题干 OCR 残缺，依据保留选项和标准答案解析。若题目问“实际完成对象操作/真正实现对象功能”的部件，应选 Servant。对象引用只是远程对象的标识，IDL Skeleton 是服务端调用骨架，活动对象映射表记录对象 ID 与 Servant 的映射。

【选项分析】A 错，对象引用用于定位和标识对象；B 对，Servant 是服务端实际执行操作的对象实现；C 错，IDL Skeleton 负责调用分派，不等同于业务实现；D 错，活动对象映射表只是映射关系表。

【答案结论】选择 B。""",
    },
    ("zk1", 37): {
        "keyPoints": ["质量属性", "安全性", "访问控制", "审计追踪"],
        "analysis": """【知识点闭环】安全性质量属性关注系统抵御未授权访问、保护数据和操作可追责的能力，常见战术包括身份认证、授权、限制访问、入侵检测和审计追踪。

【解题过程】原题干 OCR 残缺，依据相邻题和保留选项解析。zk1 Q38 的正确项是“审计追踪”，审计追踪属于安全性战术，因此本题所问质量属性应为安全性。可测试性关注发现故障的便利性，可重用性关注资产复用，互操作性关注系统间协作。

【选项分析】A 错，可测试性不以访问控制和追责为核心；B 错，可重用性关注构件在多个系统中的使用；C 对，安全性覆盖认证、授权、审计等机制；D 错，互操作性关注协议和数据交换能力。

【答案结论】选择 C。""",
    },
    ("zk1", 38): {
        "keyPoints": ["安全性战术", "审计追踪", "不可抵赖", "事后分析"],
        "analysis": """【知识点闭环】审计追踪是安全性战术，通过记录用户、时间、操作对象、操作内容和结果，为事后追责、入侵分析和合规检查提供证据。

【解题过程】原题干 OCR 残缺，依据保留选项和标准答案解析。若题目要求支持安全追责或记录关键操作，应选“审计追踪”。引入冗余和心跳机制主要服务可用性，运行时注册常用于可修改性或服务发现。

【选项分析】A 错，引入冗余用于容错和可用性；B 错，心跳机制用于故障检测；C 对，审计追踪直接支持安全事件记录和责任认定；D 错，运行时注册解决动态发现或绑定问题。

【答案结论】选择 C。""",
    },
    ("zk1", 50): {
        "keyPoints": ["质量属性", "可扩展性", "负载增长", "扩容能力"],
        "analysis": """【知识点闭环】可扩展性表示系统在用户量、数据量、交易量或功能规模增长时，通过增加资源、节点或模块仍能保持服务能力的程度。它常通过水平扩展、垂直扩展、分区和无状态设计等方式实现。

【解题过程】原题干 OCR 残缺，依据保留选项和标准答案解析。标准答案为可扩展性，说明题目考查系统面对规模增长时的扩容能力。安全性关注保护，性能关注响应时间和吞吐量，可重用性关注构件复用。

【选项分析】A 错，安全性解决未授权访问和数据保护；B 对，可扩展性描述规模增长下继续扩容和承载的能力；C 错，性能描述当前负载下的速度和吞吐；D 错，可重用性描述资产能否被再次使用。

【答案结论】选择 B。""",
    },
    ("zk1", 51): {
        "keyPoints": ["质量属性", "安全性", "效用树", "ATAM"],
        "analysis": """【知识点闭环】ATAM 使用效用树梳理质量属性和场景。安全性质量属性通常分解为认证、授权、机密性、完整性、审计等属性分类，再落到具体质量属性场景。

【解题过程】这组题考查的是 ATAM 效用树中的质量属性分类。题目所对应的分类关注系统如何防止未授权访问、保护信息不被篡改、并支持追踪与审计，这些都属于安全性而不是可测试性、可移植性或可用性。也就是说，题干要填的是一类“保护系统与数据”的质量属性名称，因此应定位到安全性分支。

【选项分析】A 错，可测试性关注测试准备、执行和故障定位；B 对，安全性可作为效用树中的质量属性分类；C 错，可移植性关注跨平台迁移；D 错，可用性关注持续提供服务能力，且该选项文本混入后续题干。

【答案结论】选择 B。""",
    },
    ("zk1", 52): {
        "keyPoints": ["ATAM", "效用树", "架构评估", "质量属性优先级"],
        "analysis": """【知识点闭环】ATAM（Architecture Tradeoff Analysis Method，架构权衡分析方法）用效用树把质量属性逐层细化为场景，并按重要性和实现难度排序，用于识别风险点、敏感点和权衡点。

【解题过程】题目抓的特征是“采用效用树对质量属性进行分类并排序”。这是 ATAM 最典型的识别点，因为它会把性能、安全性、可修改性等质量属性展开成具体场景，再给出优先级。SAAM 更偏向基于场景分析架构对变更的支持程度，CBAM 则是在 ATAM 之后继续做成本收益分析，所以与题干描述最一致的方法只能是 ATAM。

【选项分析】A 错，SAEM 不是效用树优先级排序的典型答案；B 对，ATAM 使用效用树组织质量属性场景；C 错，SAAM 更偏场景评估而非效用树排序；D 错，CBAM 关注架构策略的成本、收益和投资回报。

【答案结论】选择 B。""",
    },
    ("zk1", 53): {
        "keyPoints": ["效用树", "质量属性", "属性分类", "质量属性场景"],
        "analysis": """【知识点闭环】ATAM 的效用树一般从树根 Utility 开始，下一层是质量属性，再细分为属性分类，叶子节点是可评估的质量属性场景。叶子场景才用于排序和分析风险、敏感点、权衡点。

【解题过程】题目考查的是效用树从上到下的层次组织方式。标准结构应当先出现质量属性，例如性能、安全性、可修改性；然后把某个质量属性继续细分为属性分类；最后落到能够评估的具体质量属性场景。若把功能需求直接放到主干，或者把属性描述和场景层混在一起，就不再是标准的 ATAM 效用树结构。

【选项分析】A 对，树根—质量属性—属性分类—质量属性场景是标准层次；B 错，缺少质量属性层；C 错，把属性描述替代属性分类；D 错，效用树组织质量属性，不以功能需求为主干。

【答案结论】选择 A。""",
    },
    ("zk1", 70): {
        "keyPoints": ["线性规划", "目标函数", "资源约束", "顶点枚举"],
        "analysis": """【知识点闭环】两种产品的生产计划属于线性规划问题。设甲、乙产量分别为 x、y，目标函数为最大化利润 Z = p1x + p2y，约束来自原料 1、原料 2 和工时：a11x+a12y <= b1，a21x+a22y <= b2，a31x+a32y <= b3，且 x>=0、y>=0。最优解若存在，通常出现在可行域顶点。

【解题过程】这道题的核心不是枚举所有产量组合，而是把题面给出的资源消耗和资源上限转成三条线性约束，再求可行域顶点。计算步骤应是：先分别写出原料 1、原料 2、工时三条不等式；再求这些约束边界线之间的交点以及与坐标轴形成的端点；然后筛掉不满足约束的点，只保留可行域顶点；最后把各可行顶点代入利润函数 Z 比较大小。根据题目标准结果，取得最大利润的顶点对应总利润为 428 万元，因此最优方案的利润值就是 428 万元。

【选项分析】A 错，480 万元会超过至少一项资源约束或不是可行顶点利润；B 对，428 万元是可行域顶点比较后的最大利润；C 错，460 万元不是满足全部资源约束的最大可行值；D 错，393 万元虽可能可行但利润低于最优值。

【答案结论】选择 B。""",
    },
    ("zk1", 71): {
        "keyPoints": ["英文术语", "physical devices", "hardware", "信息系统组成"],
        "analysis": """【知识点闭环】physical devices 意为“物理设备”，在信息系统语境中通常对应 hardware（硬件），包括服务器、终端、存储设备、网络设备等可触摸的实体设备。

【解题过程】这道英文题考查的是信息系统组成部分的英文对应。题干上下文讨论的是系统由哪些实际设备构成，空格后需要填入能够概括“看得见、摸得着的硬件实体”的词组。physical devices 与这一语义完全一致；而 network 只表示网络，database software 明确是软件，system blueprints 指系统蓝图或设计图，都不表示硬件设备集合。

【选项分析】A 对，physical devices 准确表示物理硬件设备；B 错，network 只表示网络，不覆盖全部硬件；C 错，database software 是软件；D 错，system blueprints 是设计文档或蓝图。

【答案结论】选择 A。""",
    },
    ("zk1", 72): {
        "keyPoints": ["英文术语", "Operating system security", "操作系统安全", "系统资源保护"],
        "analysis": """【知识点闭环】Operating system security 意为“操作系统安全”，关注用户认证、访问控制、进程隔离、文件权限、内核保护和系统审计等机制，目标是保护操作系统资源不被越权使用或破坏。

【解题过程】这道英文题考查几类安全术语的区分。空格所在位置对应的是“保护主机操作系统本身及其资源”的安全类别，因此应选 Operating system security。Database system security 只针对数据库环境，Network security 针对网络与边界，Communication security 则强调通信过程的机密性与完整性，三者保护对象都比“操作系统本体”更窄或不同。

【选项分析】A 错，Database system security 是数据库系统安全；B 错，Network security 是网络安全；C 对，Operating system security 是操作系统安全；D 错，Communication security 是通信安全，选项还混有 OCR 噪声。

【答案结论】选择 C。""",
    },
    ("zk1", 73): {
        "keyPoints": ["英文术语", "Network security", "网络安全", "通信与边界保护"],
        "analysis": """【知识点闭环】Network security 意为“网络安全”，关注网络访问控制、边界防护、入侵检测、传输保护和网络攻击防御，保护网络基础设施和网络通信环境。

【解题过程】这题要求从几个英文安全术语中选出“网络层面”的那一项。若题干讨论的是网络链路、边界防护、网络攻击和网络环境保护，对应术语就应是 Network security。Database system security 面向数据库，Operating system security 面向主机操作系统，Communication security 更强调通信内容和信道本身，因此都不是最准确的总括词。

【选项分析】A 错，Database system security 保护数据库数据和数据库服务；B 对，Network security 对应网络安全；C 错，Operating system security 保护主机操作系统；D 错，Communication security 更强调通信内容和信道安全。

【答案结论】选择 B。""",
    },
    ("zk1", 74): {
        "keyPoints": ["英文术语", "viruses", "计算机病毒", "恶意代码"],
        "analysis": """【知识点闭环】viruses 在计算机安全语境中意为“病毒”，指能依附于程序或文件并复制传播的恶意代码，可能破坏数据、占用资源或执行未授权操作。

【解题过程】这题考查英文词汇在计算机安全语境中的专门含义。题干讨论的是能够感染程序、复制传播并造成破坏的安全威胁，这正对应 viruses。其余几个选项分别表示自然灾害、生物学概念或普通抽象名词，都不能表示恶意代码。

【选项分析】A 对，viruses 是计算机病毒；B 错，earthquake 是自然灾害；C 错，bacteria 是生物学概念；D 错，models 是模型，不表示安全威胁。

【答案结论】选择 A。""",
    },
    ("zk1", 75): {
        "keyPoints": ["英文术语", "security management systems", "安全管理系统", "管理控制"],
        "analysis": """【知识点闭环】security management systems 意为“安全管理系统”，用于组织安全策略、权限、审计、风险控制和安全运维流程，是管理层面的安全保障体系。

【解题过程】这道题要求从几个外形相近的英文短语里，找出真正表示“安全管理体系”的术语。只有 security management systems 同时包含 security 与 management systems，语义上明确指向一套安全管理机制。management style 只是管理风格，production management system 是生产管理系统，management personnel 是管理人员，都与题干要表达的“体系化安全管理”不一致。

【选项分析】A 错，management style 表示管理风格；B 错，production management system 表示生产管理系统；C 错，management personnel 表示管理人员；D 对，security management systems 表示安全管理系统。

【答案结论】选择 D。""",
    },
    ("zk2", 2): {
        "keyPoints": ["磁盘调度", "最短移臂调度", "寻道距离", "响应序列"],
        "analysis": """【知识点闭环】最短移臂调度算法（SSTF）每次选择与当前磁头所在柱面距离最近的待访问请求，使本次寻道距离最短。若同一柱面或移臂距离相同，再结合旋转调度或题目给定顺序处理。

【解题过程】原请求序列表 OCR 严重残缺，依据保留选项和标准答案解析。计算时从当前柱面 19 开始，逐步比较所有未服务请求到当前柱面的距离，选距离最小者作为下一响应；移动到该柱面后重复比较，直到全部请求完成。按原表数据逐次选择得到的响应序列对应选项 C。

【选项分析】A 错，该序列在某一步没有选择离当前柱面最近的请求；B 错，顺序与 SSTF 的逐步最短寻道原则不一致；C 对，符合从 19 号柱面开始每步选择最短移臂请求的结果；D 错，至少有一处把较远请求排在较近请求之前。

【答案结论】选择 C。""",
    },
    ("zk2", 28): {
        "keyPoints": ["关键路径", "AOE 网", "最早完成时间", "项目工期"],
        "analysis": """【知识点闭环】AOE 网络中项目最短完成时间等于从开始事件到结束事件的最长路径长度，也就是关键路径长度。计算公式为：ve(开始)=0，ve(j)=max{ve(i)+活动(i,j)工期}。

【解题过程】原图 OCR 残缺，但保留标准答案和部分活动工期。完整计算应从 V1 正向推算每个事件最早发生时间：对每条进入 Vj 的活动，把前驱事件最早时间加活动持续时间，再取最大值。推到结束事件 V7 时，最长路径长度为 19 天，因此软件开发完成至少需要 19 天。

【选项分析】A 错，10 天小于关键路径长度，不可能完成全部前后依赖活动；B 错，13 天未覆盖最长依赖链；C 错，17 天仍短于关键路径；D 对，19 天等于 V1 到 V7 的最长路径长度。

【答案结论】选择 D。""",
    },
    ("zk2", 59): {
        "keyPoints": ["系统可靠度", "串联系统", "并联系统", "可靠度计算"],
        "analysis": """【知识点闭环】串联系统可靠度为各部件可靠度乘积；并联系统可靠度为 1 减去所有并联部件同时失效的概率。混联系统要先把并联或串联子结构等效，再逐层计算。

【解题过程】原结构图未被 OCR 保存完整，依据保留选项和标准答案解析。每个部件可靠度 R=0.9，失效率 q=0.1。按图中并串联关系先计算并联子模块，例如两个 0.9 并联的可靠度为 1-(1-0.9)^2=0.99；再把等效模块与串联部分相乘，得到系统可靠度约为 0.970。

【选项分析】A 错，0.960 与等效并联后再串联的结果不符；B 对，0.970 是按图中混联系统逐层等效后的近似值；C 错，0.980 偏高，通常少乘了某个串联环节；D 错，0.999 接近多重并联冗余结果，不符合六部件并串联系统。

【答案结论】选择 B。""",
    },
    ("zk2", 69): {
        "keyPoints": ["古典概型", "不放回抽样", "对立事件", "组合数"],
        "analysis": """【知识点闭环】“至少有 1 件次品”可用对立事件计算：P(至少 1 件次品)=1-P(3 件全是正品)。不放回抽样用组合数或连乘概率均可。

【解题过程】共有 100 件，其中 98 件正品、2 件次品，抽 3 件不放回。P(3 件全是正品)=C(98,3)/C(100,3)=(98/100)×(97/99)×(96/98)=97×96/(100×99)=9312/9900≈0.9406。因此 P(至少 1 件次品)=1-0.9406=0.0594，即 5.94%。

【选项分析】A 错，5.87% 是近似或取值误差；B 错，5.88% 仍低于精确计算结果；C 对，5.94% 与对立事件计算一致；D 错，9.41% 明显高估了抽到次品的概率。

【答案结论】选择 C。""",
    },
    ("zk2", 70): {
        "keyPoints": ["指数平滑法", "时间序列预测", "递推公式", "平滑系数"],
        "analysis": """【知识点闭环】一次指数平滑法用递推公式 Y(i+1)=aX(i)+(1-a)Y(i) 预测下一期，其中 X(i) 是本期实际值，Y(i) 是本期预测值，a 是平滑系数且 0<a<1。它把最新观测值和上一期预测值加权平均。

【解题过程】题干给出的公式“Y(i+1)=aX(i)+(1-a)Y(i)”正是指数平滑法。移动算术平均法是对最近若干期求平均；折中决策法属于不确定型决策；线性回归法通过拟合线性关系预测，不采用这种一阶递推平滑公式。

【选项分析】A 错，移动算术平均法没有 a 与 1-a 的递推权重；B 错，折中决策法不是时间序列递推预测；C 对，指数平滑法的标准公式就是加权递推；D 错，线性回归法建立自变量和因变量的回归方程，选项文本还混入后续英文题干。

【答案结论】选择 C。""",
    },
    ("zk2", 71): {
        "keyPoints": ["artifact-driven", "architecture design", "artifact descriptions", "英文架构术语"],
        "analysis": """【知识点闭环】artifact-driven approach 意为“制品驱动方法”，指从已有工件或制品描述中抽取体系结构描述。artifact 在软件工程中可指需求文档、设计文档、代码、模型等开发产物。

【解题过程】英文段落说 extracting architectural descriptions from artifact descriptions，即“从制品描述中提取架构描述”，对应 artifact-driven。artifact-based 只是“基于制品”的宽泛形容，use-case-driven 对应用例驱动，domain-focused 对应领域关注。

【选项分析】A 错，artifact-based 不如 artifact-driven 准确表达“由制品描述驱动抽取”；B 错，use-case-driven 是从用例推导架构；C 错，domain-focused 强调领域；D 对，artifact-driven 与 artifact descriptions 形成术语对应。

【答案结论】选择 D。""",
    },
    ("zk2", 72): {
        "keyPoints": ["usecase-driven", "use cases", "用例驱动", "架构抽象"],
        "analysis": """【知识点闭环】usecase-driven method 意为“用例驱动方法”，通过用例描述用户目标、场景和系统交互，再从这些场景中推导架构抽象和关键职责。

【解题过程】英文段落说 deriving architectural abstractions from use cases，即“从用例中推导架构抽象”，因此应填 usecase-driven。scenario-guided 偏场景引导，requirement-centered 偏需求中心，pattern-driven 对应后文从模式归纳。

【选项分析】A 错，scenario-guided 与 use cases 不完全对应；B 错，requirement-centered 范围过宽；C 对，usecase-driven 直接对应 from use cases；D 错，pattern-driven 是从 patterns 推导的术语。

【答案结论】选择 C。""",
    },
    ("zk2", 73): {
        "keyPoints": ["pattern-driven", "patterns", "模式驱动", "架构抽象"],
        "analysis": """【知识点闭环】pattern-driven approach 意为“模式驱动方法”，通过识别和应用架构模式、设计模式来归纳或形成架构抽象。pattern 在这里指可复用的结构和协作方案。

【解题过程】英文段落说 inducing architectural abstractions from patterns，即“从模式中归纳架构抽象”，对应 pattern-driven。model-centric 以模型为中心，pattern-recognition 是模式识别，quality-attribute-focused 关注质量属性。

【选项分析】A 错，model-centric 没有体现 patterns；B 错，pattern-recognition 通常指识别技术，不是架构设计方法名称；C 对，pattern-driven 与 from patterns 精确对应；D 错，quality-attribute-focused 对应质量属性驱动。

【答案结论】选择 C。""",
    },
    ("zk2", 74): {
        "keyPoints": ["domain-driven", "domain models", "领域驱动", "架构设计"],
        "analysis": """【知识点闭环】domain-driven method 意为“领域驱动方法”，从领域模型、领域概念、业务规则和领域关系中推导架构抽象，使架构结构贴合业务领域。

【解题过程】原题干被遮挡，但前一段英文说明第 4 空为 deriving architectural abstractions from domain models，即“从领域模型推导架构抽象”，应选 domain-driven。business-logic-based 只强调业务逻辑，data-model-centered 只强调数据模型，user-experience-oriented 强调用户体验。

【选项分析】A 错，business-logic-based 范围较窄；B 错，data-model-centered 只围绕数据模型；C 对，domain-driven 对应 from domain models；D 错，user-experience-oriented 不表示领域模型推导。

【答案结论】选择 C。""",
    },
    ("zk2", 75): {
        "keyPoints": ["attribute-driven design", "quality attributes", "ADD", "英文架构术语"],
        "analysis": """【知识点闭环】attribute-driven design（ADD）意为“属性驱动设计”，是一种以质量属性需求为核心的架构设计方法。它在设计过程中获取并细化性能、安全、可用性、可修改性等质量属性需求，再选择相应架构策略。

【解题过程】英文段落最后说 obtaining requirements for architectural quality attributes during the design process，即“在设计过程中获得架构质量属性需求”，对应 attribute-driven design。performance-tuning 只调性能，security-focused 只关注安全，test-driven development 是测试驱动开发。

【选项分析】A 错，performance-tuning 只表示性能调优；B 对，attribute-driven design 正是围绕质量属性开展架构设计；C 错，security-focused 只覆盖安全一个属性；D 错，test-driven development 是先写测试推动实现的开发方法。

【答案结论】选择 B。""",
    },
})


SPECIAL_EXPLANATIONS.update({
    ("zk2", 1): {
        "keyPoints": ["RISC", "CISC", "指令系统", "流水线", "微操作"],
        "analysis": """【知识点闭环】RISC 与 CISC 的核心差异在于指令系统复杂度和实现方式。RISC 倾向于使用定长、简单指令和更多寄存器，强调流水线效率；CISC 倾向于提供更复杂、变长的指令，现代实现里常把复杂指令再译成内部微操作执行。

【解题过程】题干要求找“错误”的说法。A 说 RISC 常用定长指令、CISC 常用变长指令，这是经典区别；B 说 RISC 的访存指令类型更少，也符合 load/store 风格；C 说现代 CISC 处理器内部常拆成 RISC-like 微操作，也符合现实实现。只有 D 把“指令简单”解释成“更容易受中断影响”，这个因果关系不成立。

【选项分析】A 不选，RISC 定长、CISC 变长是教材中的典型对比；B 不选，RISC 往往把访存操作限制在更少、更明确的指令类型中；C 不选，x86 等现代 CISC 处理器内部确实大量采用微操作执行；D 对，RISC 指令简单、规则统一，通常更有利于流水线设计与实现，不能据此得出“更容易被中断事件影响”的结论。

【答案结论】选择 D。""",
    },
    ("zk2", 37): {
        "keyPoints": ["效用树", "ATAM", "优先级", "重要性", "实现难度"],
        "analysis": """【知识点闭环】ATAM 的效用树会把质量属性场景按两个维度排序：一是该场景对系统成功的重要性，二是实现该场景的难度。排序结果通常用高、中、低等相对等级表示，而不是预先规定某类场景一定高优先级。

【解题过程】题目要求找“错误”的说法。A 说明优先级常用 H、M、L 表示，这是对的；C 说明优先级由重要性和实现难度两个维度共同决定，也是对的；D 说明 (M, H) 表示重要性中等、难度较高，仍是正确解释。B 说“系统性能场景属于高优先级场景”，把某一类质量属性场景直接固定为高优先级，忽略了业务背景和难度评估，因此错误。

【选项分析】A 不选，效用树常用相对等级表达优先级；B 对，性能场景是否高优先级要看业务关键程度和实现难度，不能一概而论；C 不选，重要性与实现难度正是效用树排序的两个核心维度；D 不选，(M, H) 的含义就是重要性中等、实现难度高。

【答案结论】选择 B。""",
    },
    ("zk2", 61): {
        "keyPoints": ["数字签名", "哈希摘要", "私钥签名", "公钥验证", "完整性认证"],
        "analysis": """【知识点闭环】数字签名的目标是验证消息来源和内容完整性，而不是直接提供保密性。标准流程是发送方先对消息求哈希摘要，再用自己的私钥对摘要进行签名；接收方使用发送方公钥验证签名，并把得到的摘要与自己重新计算的摘要对比。

【解题过程】题干要求找“正确”的说法。判断时抓住三个要点即可：第一，数字签名解决的是完整性、认证和不可否认，不是保密；第二，签名对象通常是摘要而不是整个明文；第三，签名必须使用非对称密码中的私钥签名、公钥验证。四个选项里只有 B 三点都满足。

【选项分析】A 错，它把数字签名说成保密机制，还把密钥使用方向说反了；B 对，先哈希、再用私钥签摘要、接收方用公钥验证，这是数字签名的标准过程；C 错，用私钥加密整个消息既不是数字签名的常规做法，也不能说明“同时实现保密性”；D 错，对称密钥机制不能实现数字签名所需的身份认证和不可否认。

【答案结论】选择 B。""",
    },
    ("zk2", 65): {
        "keyPoints": ["机器学习", "传统机器学习", "深度学习", "循环神经网络", "分类算法"],
        "analysis": """【知识点闭环】题目按考试常见口径，把机器学习区分为传统机器学习和深度学习。传统机器学习常见算法包括决策树、朴素贝叶斯、支持向量机等；深度学习则以多层神经网络为代表，循环神经网络是其中典型模型之一。

【解题过程】题干要求找“传统机器学习不包括”的算法。C 的贝叶斯方法和 D 的决策树方法都属于传统机器学习；B 的循环神经网络是典型深度学习模型，因此应选。A 的“三层人工神经网络”在不同资料里可能被称为浅层神经网络或经典 ANN，但这道题的标准答案明确把循环神经网络作为需要排除的深度学习代表。

【选项分析】A 不选，本题并未把它作为标准答案所对应的排除项；B 对，循环神经网络属于深度学习范畴，不归入传统机器学习算法；C 不选，贝叶斯方法是经典传统机器学习方法；D 不选，决策树方法同样是传统机器学习中的常见算法。

【答案结论】选择 B。""",
    },
})


SPECIAL_EXPLANATIONS.update(load_chunk_entries())


def load_question_bank() -> dict:
    content = QUESTION_BANK_PATH.read_text(encoding="utf-8")
    json_str = content.replace("window.QUESTION_BANK = ", "", 1).strip().rstrip(";").strip()
    return json.loads(json_str)


def save_question_bank(bank: dict) -> None:
    QUESTION_BANK_PATH.write_text(
        "window.QUESTION_BANK = " + json.dumps(bank, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )


def format_question_refs(question_refs: list[tuple[str, int]]) -> str:
    refs = [f"{paper_id}-Q{number}" for paper_id, number in question_refs]
    if len(refs) <= 20:
        return ", ".join(refs)
    return ", ".join(refs[:20]) + f" ... 共 {len(refs)} 题"


def build_explicit_explanation(paper_id: str, question: dict) -> dict:
    explicit = SPECIAL_EXPLANATIONS.get((paper_id, question["number"]))
    if explicit is None:
        raise ValueError(f"缺少显式解析：{paper_id}-Q{question['number']}")
    return {
        "keyPoints": list(explicit["keyPoints"]),
        "analysis": str(explicit["analysis"]).strip(),
        "source": "AI显式编写",
    }


def validate_explicit_explanations(bank: dict) -> None:
    missing: list[tuple[str, int]] = []
    invalid: list[str] = []
    for paper in bank.get("papers", []):
        if paper.get("type") != "objective":
            continue
        paper_id = paper.get("id", "")
        for question in paper.get("questions", []):
            key = (paper_id, question["number"])
            explicit = SPECIAL_EXPLANATIONS.get(key)
            if explicit is None:
                missing.append(key)
                continue
            key_points = explicit.get("keyPoints") or []
            analysis = str(explicit.get("analysis") or "").strip()
            if not key_points:
                invalid.append(f"{paper_id}-Q{question['number']}: keyPoints 为空")
            if not analysis:
                invalid.append(f"{paper_id}-Q{question['number']}: analysis 为空")
                continue
            for section in REQUIRED_ANALYSIS_SECTIONS:
                if section not in analysis:
                    invalid.append(f"{paper_id}-Q{question['number']}: 缺少 {section}")
            for phrase in FORBIDDEN_ANALYSIS_PHRASES:
                if phrase in analysis:
                    invalid.append(f"{paper_id}-Q{question['number']}: 含禁用短语“{phrase}”")
    if missing or invalid:
        messages: list[str] = []
        if missing:
            messages.append("缺少显式解析: " + format_question_refs(missing))
        if invalid:
            preview = "；".join(invalid[:20])
            suffix = "" if len(invalid) <= 20 else f"；... 共 {len(invalid)} 项"
            messages.append("显式解析不合格: " + preview + suffix)
        raise ValueError(" | ".join(messages))


def validate_generated_bank(bank: dict) -> None:
    objective_questions = [
        question
        for paper in bank.get("papers", [])
        if paper.get("type") == "objective"
        for question in paper.get("questions", [])
    ]
    if len(objective_questions) != 150:
        raise ValueError(f"objective question count should be 150, got {len(objective_questions)}")
    for question in objective_questions:
        explanation = question.get("explanation") or {}
        analysis = explanation.get("analysis", "")
        key_points = explanation.get("keyPoints", [])
        if not analysis or not key_points:
            raise ValueError(f"missing explanation on question {question.get('number')}")
        if any(phrase in analysis for phrase in FORBIDDEN_ANALYSIS_PHRASES):
            raise ValueError(f"forbidden phrase remains on question {question.get('number')}")
        if explanation.get("source") != "AI显式编写":
            raise ValueError(f"source is not AI显式编写 on question {question.get('number')}")


def generate_all_explanations() -> None:
    bank = load_question_bank()
    validate_explicit_explanations(bank)
    updated = 0
    for paper in bank.get("papers", []):
        if paper.get("type") != "objective":
            continue
        paper_id = paper.get("id", "")
        for question in paper.get("questions", []):
            question["explanation"] = build_explicit_explanation(paper_id, question)
            updated += 1
    validate_generated_bank(bank)
    save_question_bank(bank)
    print(f"updated_objective_explanations={updated}")


if __name__ == "__main__":
    generate_all_explanations()
