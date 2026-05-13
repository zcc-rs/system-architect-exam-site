from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OCR_ROOT = Path("/tmp/sa-ocr")
OCR_TEXT = OCR_ROOT / "texts"


def option_parts(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if re.match(r"^\d{1,2}\s*[、,，]", stripped) or re.fullmatch(r"\d{1,2}\s*", stripped):
        return None
    stripped = re.sub(r"^[人入]\s*(?=[A-D5<《][\s\.．。:：、\u4e00-\u9fff0-9（(])", "", stripped)
    patterns = [
        r"^([A-D])\s*[\.．。:：、]\s*(.*)$",
        r"^([A-D])\s+(.+)$",
        r"^([A-D])(?=[\u4e00-\u9fff0-9（(])(.+)$",
        r"^([A-D])(?=[A-Z]{2,})(.+)$",
    ]
    for pattern in patterns:
        match = re.match(pattern, stripped)
        if match:
            return match.group(1), match.group(2).strip()
    match = re.match(r"^(5)\s*[\.．。:：]\s*(.+)$", stripped)
    if match:
        return "C", match.group(2).strip()
    match = re.match(r"^(5)(?=[\u4e00-\u9fffA-Za-z0-9（(])(.+)$", stripped)
    if match:
        return "C", match.group(2).strip()
    match = re.match(r"^([<《])\s*[\.．。:：、]?\s*(.+)$", stripped)
    if match:
        return "C", match.group(2).strip()
    match = re.match(r"^[\.|。．]\s*(.+)$", stripped)
    if match:
        return "C", match.group(1).strip()
    return None


OBJECTIVE_PAPERS = [
    {
        "id": "zk1",
        "stem": "综合知识",
        "title": "2026 年上半年系统架构设计师第一期模考 综合知识（一）",
        "durationMinutes": 150,
        "answers": list("BBDBCDDABAADACABDCBBBCCCAAABDADACDBBCCBABCCBBDCCCBBBABCCCADADCCBBABBABACBAD"),
        "manualMissing": {11, 24, 34, 69},
    },
    {
        "id": "zk2",
        "stem": "综合知识2",
        "title": "2026 年上半年系统架构设计师第一期模考 综合知识（二）",
        "durationMinutes": 150,
        "answers": list("DCDAACDBCCDDCBBCBBDCADBBBBBDCDBDACCCBCCCAACAABADCADCDADAADBDBCAABCBDCCDCCCB"),
        "manualMissing": {31, 53},
    },
]


ANSWER_FIXES = {
    "zk1": {34: "C"},
}


OBJECTIVE_FIXES = {
    "zk1": {
        3: {
            "stem": "为了测试新系统的性能，用户必须依靠评价程序来评价机器的性能，以下 4 种评价程序，( ) 评测的准确程度最高。",
            "options": {"A": "核心程序", "B": "合成基准程序", "C": "小型基准程序", "D": "真实程序"},
        },
        4: {
            "stem": "假设系统中互斥资源R的可用数为 30。T0 时刻进程 P1、P2、P3、P4 对资源 R 的最大需求数、已分配资源数和尚需资源数的情况如表 1 所示，若 P1 和 P2 分别申请资源 R 数为 1 和 2，则系统 ()。\n\n表 1 T0 时刻进程对资源的需求情况：\nP1：最大需求 12，已分配 8，尚需 4\nP2：最大需求 8，已分配 6，尚需 2\nP3：最大需求 9，已分配 6，尚需 3\nP4：最大需求 13，已分配 8，尚需 5",
            "options": {
                "A": "只能先给 P1 进行分配，因为分配后系统状态是安全的",
                "B": "只能先给 P2 进行分配，因为分配后系统状态是安全的",
                "C": "可以同时给 P1、P2 进行分配，因为分配后系统状态是安全的",
                "D": "不能给 P2 进行分配，因为分配后系统状态是不安全的",
            },
        },
        8: {"options": {"A": "信息", "B": "知识", "C": "应用", "D": "垂直"}},
        11: {"options": {"A": "数据仓库、联机分析和数据挖掘", "B": "数据采集、数据清洗和数据挖掘", "C": "联机分析、多维度分析和跨维度分析", "D": "数据仓库、数据挖掘和业务优化重组"}},
        12: {"options": {"A": "它强调以合理的成本开发出高质量的软件", "B": "它提倡开发者不需要进行单元测试", "C": "其理论基础主要是函数理论和抽样理论", "D": "测试是净室工程的核心，它使软件质量有了极大提高"}},
        14: {"stem": "在软件开发过程中，文档扮演着至关重要的角色，尤其对于软件的可维护性而言。软件的文档体系大致可以划分为系统文档和（1）两大类。第二类更侧重于描述软件的（2）和使用方法，不关心功能具体是怎么实现的。第（2）空应选择（ ）。", "options": {"A": "系统实现", "B": "系统设计", "C": "系统功能", "D": "系统测试"}},
        20: {"options": {"A": "确定系统的总体结构和模块间的层次关系", "B": "设计每个模块的实现算法和所需的局部数据结构", "C": "从数据流图 (DFD) 中导出系统初始的模块结构图 (SC)", "D": "绘制系统的用户界面原型"}},
        25: {"options": {"A": "自适应软件开发 (ASD)", "B": "极限编程 (XP)", "C": "SCRUM 开发", "D": "功用驱动开发 (FDD)"}},
        29: {"options": {"A": "工厂方法模式既是对象模式又是类模式", "B": "适配器模式是纯类模式", "C": "访问者模式是纯类模式", "D": "迭代器模式是纯对象模式"}},
        30: {"options": {"A": "①②", "B": "①③", "C": "②④", "D": "③④"}},
        33: {"options": {"A": "搜索服务", "B": "复制服务", "C": "联邦服务", "D": "转换服务"}},
        34: {"options": {"A": "伺服对象激活器", "B": "适配器激活器", "C": "对象请求代理 ORB", "D": "对象适配器 POA"}},
        36: {"options": {"A": "刺激源", "B": "环境", "C": "制品", "D": "响应"}},
        41: {"options": {"A": "独立构件风格", "B": "调用/返回风格", "C": "虚拟机风格", "D": "数据流风格"}},
        49: {"options": {"A": "建立过程需根据应用领域调整，一般用该领域应用开发者习惯的工具和方法建立模型", "B": "定义领域学围阶段重点是确定领域边界及过程结束时间，主要输出是满足用户需求的应用集合", "C": "定义领域特定的设计和实现需求约束阶段，只需识别出解空间中有差别的特性约束", "D": "DSSA 建立过程是并发、递归、反复的螺旋模型，可能需对每个阶段经历多遍增加细节"}},
        53: {"options": {"A": "树根—质量属性—属性分类—质量属性场景（叶子节点）", "B": "树根—属性分类—属性描述—质量属性场景（叶子节点）", "C": "树根—质量属性—属性描述—质量属性场景（叶子节点）", "D": "树根—功能需求—需求描述—质量属性场景（叶子节点）"}},
        54: {"options": {"A": "关系完整性", "B": "用户定义完整性", "C": "参照完整性", "D": "实体完整性"}},
        58: {"options": {"A": "数据 - 段 - 分组 - 帧 - 比特", "B": "数据 - 分组 - 段 - 帧 - 比特", "C": "数据 - 段 - 帧 - 分组 - 比特", "D": "数据 - 分组 - 帧 - 段 - 比特"}},
        60: {"options": {"A": "星状结构", "B": "环形结构", "C": "总线结构", "D": "树状结构"}},
        66: {"options": {"A": "大数据", "B": "建模", "C": "仿真", "D": "基于数据融合的数字线程"}},
        70: {"options": {"A": "480", "B": "428", "C": "460", "D": "393"}},
    },
    "zk2": {
        11: {"options": {"A": "通讯服务、信息传递与转化服务、流程控制服务、应用连接服务", "B": "通讯服务、流程控制服务、应用连接服务、信息传递与转化服务", "C": "通讯服务、应用连接服务、信息传递与转化服务、流程控制服务", "D": "通讯服务、信息传递与转化服务、应用连接服务、流程控制服务"}},
        12: {"options": {"A": "语句覆盖要求每条语句都被至少一个测试用例覆盖，它比判定覆盖强", "B": "满足条件组合覆盖的测试用例不一定满足判定/条件覆盖", "C": "判定覆盖对程序逻辑的覆盖程度比条件覆盖高", "D": "条件覆盖不一定包含判定覆盖，因为条件覆盖仅关注每个条件的结果，而不一定覆盖所有判定分支"}},
        21: {"options": {"A": "通信内聚", "B": "功能内聚", "C": "逻辑内聚", "D": "顺序内聚"}},
        32: {"options": {"A": "①②", "B": "①②③", "C": "①③④", "D": "①②④"}},
        43: {"options": {"A": "顺序", "B": "层次", "C": "叠加", "D": "循环"}},
        45: {"options": {"A": "独立构件风格", "B": "调用/返回风格", "C": "虚拟机风格", "D": "数据流风格"}},
        47: {"options": {"A": "②", "B": "①②", "C": "③", "D": "①③"}},
        40: {"options": {"A": "大数据", "B": "物联网", "C": "虚拟化", "D": "人工智能"}},
        48: {"options": {"A": "PART", "B": "POST", "C": "PUT", "D": "PATCH"}},
        51: {"options": {"A": "静态全局转储", "B": "动态全局转储", "C": "静态增量转储", "D": "动态增量转储"}},
        58: {"options": {"A": "在 DO-178B 中，根据软件在系统中的重要程度将软件的安全等级分为 A~E 五级，不同安全等级的软件需要达到的目标要求不同。", "B": "CMMI 集成了系统、软件和硬件等视角，内容和措辞需兼顾多个场景；DO-178B 聚焦软件，更容易为软件工程师理解。", "C": "A 等级失效状态是灾难性的，软件异常会导致航空器无法安全飞行和着陆。", "D": "E 等级失效状态是危害性的，软件异常会严重降低航空器或机组克服不利运行情况的能力。"}},
        63: {"options": {"A": "SYN 洪水攻击", "B": "Ping 洪水攻击", "C": "UDP 洪水攻击", "D": "DNS 洪水攻击"}},
        73: {"options": {"A": "model-centric", "B": "pattern-recognition", "C": "pattern-driven", "D": "quality-attribute-focused"}},
        74: {
            "stem": "【考生回忆版】原始资料中该题题干被遮挡，仅保留选项。",
            "options": {"A": "business-logic-based", "B": "data-model-centered", "C": "domain-driven", "D": "user-experience-oriented"},
        },
    },
}


SUBJECTIVE_PAPERS = [
    {"id": "case1", "stem": "案例分析", "title": "案例分析（一）", "durationMinutes": 90, "type": "case"},
    {"id": "case2", "stem": "案例分析2", "title": "案例分析（二）", "durationMinutes": 90, "type": "case"},
    {"id": "essay1", "stem": "论文", "title": "论文写作（一）", "durationMinutes": 120, "type": "essay"},
    {"id": "essay2", "stem": "论文2", "title": "论文写作（二）", "durationMinutes": 120, "type": "essay"},
]


NOISE_PATTERNS = [
    r"内部资料[，,、 ]*禁止传播",
    r"希赛网.*职业教育平台",
    r"客服热线",
    r"软考刷题系统",
    r"刷题打卡",
    r"备考大全",
    r"备考资料",
    r"专业的在线职业教育平台",
]


def is_ocr_noise_line(line: str) -> bool:
    if re.fullmatch(r"\[\[PAGE \d+\]\]", line):
        return True
    if any(re.search(pattern, line) for pattern in NOISE_PATTERNS):
        return True
    if re.fullmatch(r"[0-9]{1,2}", line):
        return True
    if len(line) <= 4 and re.fullmatch(r"[a-zA-Z\\/|()<>©=\- ]+", line):
        return True
    if (
        len(line) <= 16
        and re.search(r"[<>]", line)
        and not re.search(r"[\u4e00-\u9fff]", line)
        and re.fullmatch(r"[A-Za-z0-9\\/|()<>©=\-`'‘’.,;: ]+", line)
    ):
        return True
    return False


def normalize_ocr_artifacts(text: str) -> str:
    text = re.sub(r"([（(])\s*[〈《<]\s*([)）])", r"\1 \2", text)
    text = re.sub(r"[〈《]\s*(?=[（(])", "", text)
    text = re.sub(r"(?<=\s)[〈《](?=[\u4e00-\u9fffA-Za-z0-9])", "（", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\t\u3000]+", " ", text)
    lines: list[str] = []
    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            lines.append("")
            continue
        if is_ocr_noise_line(line):
            continue
        lines.append(line)
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"试题答案\s*[:：]\s*[A-D].*", "", cleaned)
    return normalize_ocr_artifacts(cleaned)


def infer_topic(text: str, number: int) -> str:
    checks = [
        ("操作系统", ["进程", "线程", "页", "CPU", "主存", "缓冲", "互斥", "位示图", "分时"]),
        ("软件工程", ["软件", "测试", "需求", "文档", "模块", "内聚", "耦合", "开发", "净室"]),
        ("系统架构", ["架构", "质量属性", "构件", "风格", "ATAM", "可用性", "可修改性"]),
        ("数据库", ["数据库", "关系模式", "SQL", "事务", "范式", "E-R", "索引", "数据仓库"]),
        ("网络与安全", ["网络", "TCP", "IP", "DHCP", "路由", "安全", "攻击", "防火墙", "加密"]),
        ("项目管理", ["项目", "成本", "进度", "PERT", "关键路径", "风险", "估算"]),
        ("知识产权", ["著作权", "商业秘密", "专利", "商标", "知识产权", "软件著作权"]),
        ("数学与运筹", ["矩阵", "利润", "资源", "概率", "最大", "最小", "线性规划"]),
        ("英文综合题", ["Physical layer", "Network security", "Application security", "security management"]),
    ]
    for topic, keywords in checks:
        if any(keyword.lower() in text.lower() for keyword in keywords):
            return topic
    if number >= 71:
        return "英文综合题"
    return "综合知识"


def parse_options(text: str) -> dict[str, str]:
    options: dict[str, str] = {}
    current: str | None = None
    buffer: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = option_parts(line)
        if parts:
            if current:
                options[current] = " ".join(buffer).strip()
            current, option_text = parts
            buffer = [option_text]
        elif current and not re.match(r"^\d{1,2}\s*[、,，.]", line):
            buffer.append(line)
    if current:
        options[current] = " ".join(buffer).strip()
    return options


def find_option_start(lines: list[str]) -> int | None:
    for index, line in enumerate(lines):
        parts = option_parts(line)
        if not parts:
            continue
        following_keys = {parts[0]}
        for later_line in lines[index + 1 :]:
            later_parts = option_parts(later_line)
            if later_parts:
                following_keys.add(later_parts[0])
        if len(following_keys) >= 2:
            return index
    return None


def strip_edge_blank_lines(lines: list[str]) -> list[str]:
    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def split_question_and_options(text: str) -> tuple[str, dict[str, str]]:
    lines = text.splitlines()
    option_start = find_option_start(lines)
    if option_start is None:
        return text, parse_options(text)
    question_lines = strip_edge_blank_lines(lines[:option_start])
    option_lines = lines[option_start:]
    question_text = "\n".join(question_lines).strip()
    return question_text, parse_options("\n".join(option_lines))


def read_pages(stem: str) -> tuple[str, list[int], list[str]]:
    page_files = sorted(OCR_TEXT.glob(f"{stem}_page_*.txt"))
    offsets: list[int] = []
    page_texts: list[str] = []
    combined_parts: list[str] = []
    cursor = 0
    for index, path in enumerate(page_files, start=1):
        marker = f"\n\n[[PAGE {index}]]\n"
        combined_parts.append(marker)
        cursor += len(marker)
        offsets.append(cursor)
        text = path.read_text(encoding="utf-8")
        page_texts.append(text)
        combined_parts.append(text)
        cursor += len(text)
    return "".join(combined_parts), offsets, page_texts


def page_for_position(position: int, offsets: list[int]) -> int:
    page = 1
    for index, offset in enumerate(offsets, start=1):
        if position >= offset:
            page = index
        else:
            break
    return page


def question_start_positions(text: str) -> dict[int, int]:
    starts: dict[int, int] = {}
    for number in range(1, 76):
        patterns = [
            rf"(?m)^\s*{number}\s*[、,，]\s*",
            rf"(?m)^\s*{number}\s+",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                starts[number] = match.start()
                break
    return starts


def build_objective_paper(config: dict) -> dict:
    answers = config["answers"]
    if len(answers) != 75:
        raise ValueError(f"{config['id']} expected 75 answers, got {len(answers)}")

    combined, offsets, _page_texts = read_pages(config["stem"])
    starts = question_start_positions(combined)
    questions = []

    for number in range(1, 76):
        start = starts.get(number)
        if start is None:
            previous_starts = [position for question_number, position in starts.items() if question_number < number]
            start = max(previous_starts) if previous_starts else 0

        next_starts = [position for question_number, position in starts.items() if question_number > number and position > start]
        end = min(next_starts) if next_starts else len(combined)

        raw = combined[start:end]
        cleaned = clean_text(raw)
        question_text, options = split_question_and_options(cleaned)
        topic = infer_topic(question_text, number)
        correct = ANSWER_FIXES.get(config["id"], {}).get(number, answers[number - 1])
        fix = OBJECTIVE_FIXES.get(config["id"], {}).get(number, {})
        if "stem" in fix:
            question_text = fix["stem"]
        if "options" in fix:
            options = fix["options"]
        correct_text = options.get(correct, "")
        questions.append(
            {
                "number": number,
                "answer": correct,
                "topic": topic,
                "page": page_for_position(start, offsets),
                "stem": question_text,
                "options": options,
                "correctOptionText": correct_text,
            }
        )

    return {
        "id": config["id"],
        "type": "objective",
        "title": config["title"],
        "durationMinutes": config["durationMinutes"],
        "totalScore": 75,
        "passingScore": 45,
        "questions": questions,
    }


def split_reference(text: str) -> dict[str, str]:
    parts = re.split(r"试题答案\s*[:：]?", text, maxsplit=1)
    if len(parts) == 2:
        return {"paperText": clean_text(parts[0]), "reference": clean_text(parts[1])}
    cleaned = clean_text(text)
    return {"paperText": cleaned, "reference": "本卷 OCR 未识别到独立参考答案，请结合原 PDF 页面进行复盘。"}


CASE_ITEMS = {
    "case1": [
        {
            "id": "case1-1",
            "title": "试题一：电子病历管理系统架构评估",
            "scenario": "某医院计划开发电子病历管理系统，需求涉及长文档阅读体验、病历数据保密、500ms 查询响应、7x24 小时运行、100 名医生并发、网络失效 5s 内切换、报表模块 3 人周内变更、防止 99% 黑客攻击、响应时间可接受性、新身份验证机制影响、并发用户数量影响协议和数据格式、业务逻辑不清导致三层架构第二层功能重复、新用户 2 小时内学会使用、提供远程调试接口。",
            "questions": [
                "问题1：在质量属性效用树中填写（1）~（4）的质量属性，并从题干 (a)~(n) 中选择（5）~（10）的示例。",
                "问题2：用 300 字以内说明架构风险点、非风险点、敏感点和权衡点的定义，并分别从 (a)~(n) 中选出对应描述。",
                "问题3：将性能战术 (a) 减少计算开销、(b) 控制采样频率、(c) 增加可用资源、(d) 管理事件率、(e) 先进/先出、(f) 维持多个副本、(g) 固定优先级填入资源需求、资源管理、资源仲裁三类。",
            ],
            "fields": ["（1）~（4）质量属性", "（5）~（10）效用树示例", "敏感点", "风险点", "非风险点", "权衡点", "性能战术（1）", "性能战术（2）", "性能战术（3）"],
            "reference": "问题1：(1) 易用性；(2) 安全性；(3) 可用性；(4) 可修改性；(5)(6) c、e；(7) m；(8) h；(9) d；(10) n。\n问题2：敏感点是影响某个质量属性的构件或关系特性；权衡点是影响多个质量属性的特性；风险点是存在问题的架构决策隐患；非风险点是不带来隐患的分析与描述。敏感点(k)，风险点(l)，非风险点(i)，权衡点(j)。\n问题3：(1) a、b、d；(2) c、f；(3) e、g。",
        },
        {
            "id": "case1-2",
            "title": "试题二：智能图书馆管理系统分析建模",
            "scenario": "某高校拟开发智能图书馆管理系统 ILMS，功能包括图书管理、借阅管理、归还管理、预约管理。管理员维护图书，馆长查看统计报表，读者借阅、归还和预约图书。项目组采用面向对象方法，在系统分析阶段完成用例模型和分析模型设计。",
            "questions": ["问题1：说明分析模型的含义、建立分析模型的五个步骤、分析模型详细程度原则。", "问题2：列举类之间关系中的 4 类；指出“归还图书”和“计算逾期费用”两个用例的关系类型，并说明事件流表现。", "问题3：识别系统参与者并说明依据。"],
            "fields": ["分析模型定义", "五个建模步骤", "详细程度原则", "4 类关系", "用例关系类型", "事件流表现", "参与者及依据"],
            "reference": "分析模型描述系统逻辑结构，展示对象和类如何组成系统以及如何通信实现行为。步骤：定义概念类、确定类之间关系、为类添加职责、建立交互图、确定分析模型详细程度。详细程度满足开发需要并逐步细化即可。类关系可列依赖、关联、聚合、组合、实现、泛化。归还图书与计算逾期费用是扩展关系，仅当图书逾期时触发。参与者：管理员、读者、图书馆长。",
        },
        {
            "id": "case1-3",
            "title": "试题三：人形机器人与嵌入式实时系统",
            "scenario": "人形机器人本体包括感知系统、决策系统和控制系统。题目考查人工智能技术包含关系、具身智能机器人部件归类，以及嵌入式实时操作系统调度算法和典型架构模式。",
            "questions": ["问题1：填写人工智能领域技术包含关系图中的（1）~（4）。", "问题2：将旋转执行器、线性执行器、灵巧手、中央计算单元、ROS、视觉/听觉/温湿度/力/触觉传感器等部件归入感知、决策、控制系统对应空。", "问题3：简述 RMS、EDF、LLF 三种调度算法，并写出嵌入式系统典型架构模式。"],
            "fields": ["AI 技术（1）", "AI 技术（2）", "AI 技术（3）", "AI 技术（4）", "部件归类（1）~（7）", "RMS", "EDF", "LLF", "两种架构模式"],
            "reference": "问题1：机器学习、神经网络、深度学习、大模型。问题2：(1) f/g/h；(2) j；(3) i；(4) d/e；(5) a；(6) b；(7) c。问题3：RMS 按周期确定固定优先级，周期越短优先级越高；EDF 按最早截止时间优先；LLF 按最低松弛度优先。典型架构：层次化模式架构、递归模式架构。",
        },
        {
            "id": "case1-4",
            "title": "试题四：网站集群与负载均衡",
            "scenario": "网站通过增加服务器分担访问和存储压力，使用应用服务器集群提升并发处理能力。题目考查负载均衡工作层次、调度算法，以及选择 NAT 集群模式的理由。",
            "questions": ["问题1：将 Nginx、LVS、HAProxy、HTTP 重定向、反向代理负载均衡、基于 NAT 的负载均衡、基于 DNS 的负载均衡按可工作层次填入（1）~（2）。", "问题2：简述轮询、加权轮询、最少连接、源地址散列四种调度算法。", "问题3：从负载均衡、故障转移、安全性角度说明选择 NAT 集群模式的理由。"],
            "fields": ["应用层相关技术", "传输层/网络层相关技术", "轮询", "加权轮询", "最少连接", "源地址散列", "NAT 集群理由"],
            "reference": "问题1：(1) a、c、d、e；(2) b、c、g、f。问题2：轮询均匀分配请求；加权轮询按服务器能力设置权重；最少连接选择当前连接数最少服务器；源地址散列按用户 IP 哈希映射到目标服务器。问题3：NAT 可均衡分配请求、支持故障转移、隐藏后端真实 IP 并集中处理访问。",
        },
        {
            "id": "case1-5",
            "title": "试题五：设备远程监控与预测性维护系统",
            "scenario": "智慧工厂拟开发基于 Web 的设备远程监控与预测性维护系统，包含实时采集传感器数据、故障预测、工单管理、三级角色权限控制、传感器数据加密传输和 500 台设备并发接入。技术栈为 Spring Boot + Vue，建议使用 WebSocket 推送实时数据、HTTPS 保障传输安全。",
            "questions": ["问题1：比较 HTTP 与 WebSocket 的工作模式，并说明实时状态数据与工单管理数据分别采用哪种通信方式。", "问题2：说明权限控制应采用的访问控制类型。", "问题3：说明传感器数据适合 SQL 还是 NoSQL，并列举两个数据库。", "问题4：列举 7 种 Web 应用架构通用设计原则。"],
            "fields": ["HTTP 工作模式", "WebSocket 工作模式", "通信方式选择", "访问控制类型", "数据库类型与示例", "7 种设计原则"],
            "reference": "HTTP 为请求-响应、短连接通信；WebSocket 建立持久连接，支持全双工实时通信。实时状态数据选 WebSocket，工单管理数据选 HTTP。权限控制采用 RBAC。传感器数据适合 NoSQL，如 InfluxDB、Cassandra。设计原则可写：分离关注点、封装、依赖关系反转、显式依赖关系、单一责任、避免重复、持久性无知、有界上下文等。",
        },
    ],
    "case2": [
        {
            "id": "case2-1",
            "title": "试题一：在线教育平台架构评估",
            "scenario": "在线教育平台支持课程购买、视频点播、在线测试。题干给出 (a)~(s) 质量属性与架构特性场景，用于 ATAM 质量属性效用树、风险/敏感/权衡/非风险点识别，以及可用性质量属性场景填空。",
            "questions": ["问题1：指出 ATAM 效用树 4 大质量属性，并从 (a)~(s) 中找到对应示例；再找出易用性和可测试性示例。", "问题2：定义风险点、非风险点、敏感点、权衡点，并分别选出一个示例。", "问题3：从给定选项中填写可用性质量属性场景要素（1）~（6）。"],
            "fields": ["4 大质量属性及示例", "易用性示例", "可测试性示例", "风险点", "非风险点", "敏感点", "权衡点", "可用性场景（1）~（6）"],
            "reference": "4 大属性示例：性能(a)(d)，可用性(c)(q)，安全性(b)(f)(l)(r)，可修改性(j)(o)。易用性(e)(n)，可测试性(m)(s)。敏感点(k)，权衡点(g)，风险点(h)，非风险点(p)。可用性场景：(1)c，(2)f，(3)a/g，(4)b，(5)e，(6)d。",
        },
        {
            "id": "case2-2",
            "title": "试题二：智能健康监护系统时序与状态建模",
            "scenario": "三甲医院开发慢性病智能健康监护系统，核心组件包括边缘网关、规则引擎、告警服务、消息推送服务、定位服务和设备日志服务。紧急告警数据从可穿戴设备到边缘网关、规则引擎、告警服务和消息服务流转。",
            "questions": ["问题1：补充紧急告警时序图（1）~（10）。", "问题2：说明组合状态，并补充状态转移五要素名称。", "问题3：100 字以内说明状态图与活动图的本质区别。"],
            "fields": ["时序图（1）~（10）", "组合状态定义", "触发事件", "监护条件", "转换", "动作", "目标状态", "状态图与活动图区别"],
            "reference": "时序图参考：(1) 设备日志服务；(2) 解析 ECG 波形滤波后数据；(3) 触发三级告警；(4) 生成告警通知；(5) 推送至主治医生；(6) 启动救援、派救护车；(7) 发送位置信息；(8) 更新实时位置地图坐标；(9) 记录事件流水；(10) 边缘网关。组合状态是包含子状态的状态。状态转移五要素：触发事件、监护条件、转换、动作、目标状态。状态图强调对象状态及转移，活动图强调业务/操作流程的控制流和数据流。",
        },
        {
            "id": "case2-3",
            "title": "试题三：嵌入式软件开放式架构 GOA",
            "scenario": "某软件公司为提升宇航嵌入式软件复用和移植能力，研究 SAE AS4893 通用开放式架构 GOA 框架。题目考查开放式架构特点，以及 GOA 框架直接接口和逻辑接口的填空。",
            "questions": ["问题1：300 字以内说明开放式架构的四个基本特点。", "问题2：根据 GOA 框架图填写表 3-1 的（1）~（8）。"],
            "fields": ["开放式架构特点 1", "开放式架构特点 2", "开放式架构特点 3", "开放式架构特点 4", "GOA 表（1）~（8）"],
            "reference": "开放式架构通常强调模块化、标准接口、可重用/可移植、可扩展/可升级。GOA 表格答案请按参考答案逐项填写，重点区分直接接口 iD 与逻辑接口 iL：直接接口定义信息传输方式，逻辑接口定义对等数据交换要求。",
        },
        {
            "id": "case2-4",
            "title": "试题四：交通流量智能管控系统",
            "scenario": "智慧城市项目开发交通流量智能管控系统，实时分析主干道车流数据并动态调整信号灯策略。题目围绕系统设计、建模和架构决策展开。",
            "questions": ["按题目给出的模型或流程，完成问题 1 至问题 3 的填空与说明。"],
            "fields": ["问题1 填写项", "问题2 填写项", "问题3 作答要点"],
            "reference": "请结合题目参考答案核对。页面已把作答区独立出来，避免直接展示答案。",
        },
        {
            "id": "case2-5",
            "title": "试题五：区块链农产品信息溯源管理系统",
            "scenario": "基于区块链的农产品信息溯源管理系统涉及数据录入、核对、审核、智能合约和上链追溯流程。题目考查系统设计与建模、角色职责、智能合约等知识。",
            "questions": ["按题目要求回答问题 1 至问题 3，重点写清参与者/流程/智能合约相关内容。"],
            "fields": ["问题1 作答区", "问题2 作答区", "问题3 作答区"],
            "reference": "请结合题目参考答案核对。页面已把作答区独立出来，避免直接展示答案。",
        },
    ],
}


def build_subjective_paper(config: dict) -> dict:
    combined, _offsets, _page_texts = read_pages(config["stem"])
    split = split_reference(combined)
    paper = {
        "id": config["id"],
        "type": config["type"],
        "title": config["title"],
        "durationMinutes": config["durationMinutes"],
        "totalScore": 75,
        **split,
    }
    if config["id"] in CASE_ITEMS:
        paper["caseItems"] = CASE_ITEMS[config["id"]]
    return paper


def main() -> None:
    papers = []
    for config in OBJECTIVE_PAPERS:
        papers.append(build_objective_paper(config))
    for config in SUBJECTIVE_PAPERS:
        papers.append(build_subjective_paper(config))

    data = {
        "generatedFrom": "OCR of local PDF mock papers",
        "objectivePaperIds": [paper["id"] for paper in papers if paper["type"] == "objective"],
        "subjectivePaperIds": [paper["id"] for paper in papers if paper["type"] != "objective"],
        "papers": papers,
    }
    output = ROOT / "data" / "question-bank.js"
    output.write_text("window.QUESTION_BANK = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")


if __name__ == "__main__":
    main()