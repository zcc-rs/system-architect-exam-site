const bank = window.QUESTION_BANK;
const app = document.querySelector("#app");
const toast = document.querySelector("#toast");

const objectivePapers = bank.papers.filter((paper) => paper.type === "objective");
const subjectivePapers = bank.papers.filter((paper) => paper.type !== "objective");
const caseGuidance = window.CASE_GUIDANCE || {};
const optionKeys = ["A", "B", "C", "D"];
const UI_STATE_KEY = "sa-ui-state-v1";
const studyFilters = new Set(["all", "wrong", "unmastered"]);
const chineseNumbers = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"];
const caseFieldGroups = {
  "case1-1": [[0, 1], [2, 3, 4, 5], [6, 7, 8]],
  "case1-2": [[0, 1, 2], [3, 4, 5], [6]],
  "case1-3": [[0, 1, 2, 3], [4], [5, 6, 7, 8]],
  "case1-4": [[0, 1], [2, 3, 4, 5], [6]],
  "case1-5": [[0, 1, 2], [3], [4], [5]],
  "case2-1": [[0, 1, 2], [3, 4, 5, 6], [7]],
  "case2-2": [[0], [1, 2, 3, 4, 5, 6], [7]],
  "case2-3": [[0, 1, 2, 3], [4]],
  "case2-4": [[0], [1], [2]],
  "case2-5": [[0], [1], [2]],
};

const savedUiState = loadJson(UI_STATE_KEY, {});
const initialObjectivePaper = objectivePapers.find((paper) => paper.id === savedUiState.paperId) || objectivePapers[0];
const initialSubjectivePaper = subjectivePapers.find((paper) => paper.id === savedUiState.subjectiveId) || subjectivePapers[0];
const initialMode = ["exam", "study", "subjective"].includes(savedUiState.mode) ? savedUiState.mode : "exam";
const initialQuestionNumber = Math.min(
  initialObjectivePaper.questions.length,
  Math.max(1, Number(savedUiState.questionNumber) || 1)
);
const initialExamState = loadExamState(initialObjectivePaper);
const initialCaseCount = initialSubjectivePaper.caseItems?.length || 0;
const initialSubjectiveItemIndex = initialCaseCount
  ? Math.min(initialCaseCount - 1, Math.max(0, Number(savedUiState.subjectiveItemIndex) || 0))
  : 0;

const state = {
  mode: initialMode,
  paperId: initialObjectivePaper.id,
  subjectiveId: initialSubjectivePaper.id,
  questionNumber: initialQuestionNumber,
  pageIndex: Math.max(0, Number(savedUiState.pageIndex) || 0),
  subjectivePageIndex: Math.max(0, Number(savedUiState.subjectivePageIndex) || 0),
  subjectiveItemIndex: initialSubjectiveItemIndex,
  answers: loadJson(answerKey(initialObjectivePaper.id), {}),
  result: loadJson(resultKey(initialObjectivePaper.id), null),
  startedAt: initialExamState.startedAt,
  deadline: initialExamState.deadline,
  finished: Boolean(loadJson(resultKey(initialObjectivePaper.id), null)),
  studyFilter: studyFilters.has(savedUiState.studyFilter) ? savedUiState.studyFilter : "all",
  revealMap: {},
  mastered: loadJson("sa-mastered", {}),
  showReference: Boolean(savedUiState.showReference),
};

let timerId = null;
let toastId = null;

const topicHints = {
  操作系统: "先识别题干里的资源、调度、存储或并发条件，再套用操作系统基本机制；这类题常把定义特征和实现手段混在一起考。",
  软件工程: "先判断题目问的是过程、模型、文档、测试还是设计原则，再回到标准定义和适用边界。",
  系统架构: "先抓质量属性、架构风格、构件关系或评估术语，再看选项是否同时满足场景约束。",
  数据库: "先定位数据模型、事务、范式、完整性或查询语义，再排除只满足局部条件的选项。",
  网络与安全: "先确定层次、协议、威胁或防护目标；网络题尤其注意协议所在层和适用场景。",
  项目管理: "先把题干中的时间、成本、资源和风险信息结构化，再判断属于估算、控制还是决策。",
  知识产权: "先区分权利客体、权利归属、保护条件和例外规则，避免把一般表述当成绝对结论。",
  数学与运筹: "先把文字条件转为公式或约束，再检查选项是否满足目标函数和边界条件。",
  英文综合题: "先读空格所在句，再结合段落标题和上下文层次判断；不要只按单词熟悉程度选。",
  综合知识: "先提炼题干关键词，再用定义、适用条件和排除法逐项验证。",
};

const topicExamples = {
  操作系统: "例如分时系统的典型特征是多路性、独立性、交互性、及时性；题目若问“多路性之外还缺什么”，不要把共享性误当成分时系统基本特征。",
  软件工程: "例如白盒覆盖标准中，语句覆盖只保证语句执行过，不保证每个判定分支都被覆盖；比较强弱时要看覆盖对象是语句、判定还是条件组合。",
  系统架构: "例如质量属性场景通常包含刺激源、刺激、环境、制品、响应、响应度量；做题时先把题干事件放进这六个位置。",
  数据库: "例如候选码判断要看属性闭包是否能推出全部属性；若 AB+ 能推出 U 且 A+ 不能、B+ 不能，则 AB 才可能是候选码。",
  网络与安全: "例如 SYN Flood 是大量伪造 TCP SYN 请求占满半连接队列；若题干出现“三次握手无法完成”，优先想到 SYN 洪水攻击。",
  项目管理: "例如关键路径题先画出前驱关系，再算最早/最迟时间；不能只看单个活动工期大小。",
  知识产权: "例如商业秘密属于知识产权的客体，保护条件通常包括秘密性、价值性和保密措施。",
  数学与运筹: "例如阿姆达尔定律题要先找可优化部分占比，再用整体加速比公式反推局部加速倍数。",
  英文综合题: "例如段落标题是 Physical layer security 时，空格一般围绕物理设备、线路、机房等实体安全，而不是应用或数据库。",
  综合知识: "例如看到“最适合”“不正确”“核心技术”等限定词，先圈出题干问法，再逐项排除泛化、偷换或只说一半的选项。",
};

function answerKey(paperId) {
  return `sa-answers-${paperId}`;
}

function examStateKey(paperId) {
  return `sa-exam-state-${paperId}`;
}

function resultKey(paperId) {
  return `sa-result-${paperId}`;
}

function draftKey(paperId) {
  return `sa-draft-${paperId}`;
}

function scoreKey(paperId) {
  return `sa-score-${paperId}`;
}

function caseDraftKey(paperId, itemId) {
  return `sa-case-draft-${paperId}-${itemId}`;
}

function expandCaseField(field, fieldIndex) {
  const normalized = String(field).replace(/[～－—]/g, "~");
  const match = normalized.match(/^(.*?)[（(](\d+)[)）]\s*~\s*[（(](\d+)[)）](.*)$/);
  if (!match) {
    return [{ key: String(fieldIndex), label: field, original: field, fieldIndex, isRange: false }];
  }

  const start = Number(match[2]);
  const end = Number(match[3]);
  if (!Number.isInteger(start) || !Number.isInteger(end) || end <= start || end - start > 30) {
    return [{ key: String(fieldIndex), label: field, original: field, fieldIndex, isRange: false }];
  }

  const prefix = match[1].trim();
  const suffix = match[4].trim();
  return Array.from({ length: end - start + 1 }, (_, offset) => {
    const number = start + offset;
    return {
      key: `${fieldIndex}-${number}`,
      label: `${prefix}（${number}）${suffix}`,
      original: field,
      fieldIndex,
      isRange: true,
    };
  });
}

function expandedCaseFields(fields) {
  return fields.flatMap((field, index) => expandCaseField(field, index));
}

function questionHeading(index) {
  return `问题${chineseNumbers[index] || index + 1}`;
}

function groupedCaseFields(item) {
  const configuredGroups = caseFieldGroups[item.id];
  if (!configuredGroups) {
    return [{ title: questionHeading(0), fields: expandedCaseFields(item.fields) }];
  }
  return configuredGroups.map((fieldIndexes, index) => ({
    title: questionHeading(index),
    fields: fieldIndexes.flatMap((fieldIndex) => expandCaseField(item.fields[fieldIndex], fieldIndex)),
  }));
}

function renderCaseFieldGuidance(itemId, field) {
  const guidance = caseGuidance[itemId]?.[field.key] || caseGuidance[itemId]?.[String(field.fieldIndex)];
  if (!guidance) {
    return `<div class="case-guidance"><p><strong>参考答案：</strong>见本题整题评分要点。</p><p><strong>为什么：</strong>此处属于综合说明题，需要结合题干场景组织答案。</p><p><strong>知识点：</strong>先定位题目考查的架构概念，再写清定义、场景依据和结论。</p></div>`;
  }
  return `<div class="case-guidance">
    <p><strong>参考答案：</strong>${escapeHtml(guidance.answer)}</p>
    <p><strong>为什么这样填：</strong>${escapeHtml(guidance.why)}</p>
    <p><strong>相关知识：</strong>${escapeHtml(guidance.knowledge)}</p>
  </div>`;
}

function loadJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch (_error) {
    return fallback;
  }
}

function saveJson(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function loadExamState(paper) {
  const saved = loadJson(examStateKey(paper.id), null);
  if (saved && Number.isFinite(saved.startedAt) && Number.isFinite(saved.deadline) && saved.deadline > saved.startedAt) {
    return saved;
  }
  const now = Date.now();
  return {
    startedAt: now,
    deadline: now + paper.durationMinutes * 60 * 1000,
  };
}

function saveExamState(paperId = state.paperId) {
  saveJson(examStateKey(paperId), {
    startedAt: state.startedAt,
    deadline: state.deadline,
  });
}

function persistUiState() {
  saveJson(UI_STATE_KEY, {
    mode: state.mode,
    paperId: state.paperId,
    subjectiveId: state.subjectiveId,
    questionNumber: state.questionNumber,
    pageIndex: state.pageIndex,
    subjectivePageIndex: state.subjectivePageIndex,
    subjectiveItemIndex: state.subjectiveItemIndex,
    studyFilter: state.studyFilter,
    showReference: state.showReference,
  });
}

function currentObjectivePaper() {
  return objectivePapers.find((paper) => paper.id === state.paperId) || objectivePapers[0];
}

function currentSubjectivePaper() {
  return subjectivePapers.find((paper) => paper.id === state.subjectiveId) || subjectivePapers[0];
}

function currentQuestion() {
  return currentObjectivePaper().questions[state.questionNumber - 1];
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function extractResourceDemandTable(stemText) {
  const lines = String(stemText || "")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  const rowPattern = /^P(\d+)[：:]\s*最大需求\s*(\d+)[，,]\s*已分配\s*(\d+)[，,]\s*尚需\s*(\d+)/;
  const rows = [];

  for (const line of lines) {
    const match = line.match(rowPattern);
    if (!match) {
      continue;
    }
    rows.push({
      process: `P${match[1]}`,
      maxDemand: match[2],
      allocated: match[3],
      needed: match[4],
    });
  }

  if (rows.length !== 4) {
    return null;
  }

  const captionLine = lines.find((line) => /^表\s*1/.test(line)) || "表 1 T0 时刻进程对资源的需求情况";
  return {
    caption: captionLine,
    rows,
  };
}

function renderQuestionStem(question) {
  const fallback = "OCR 未能稳定识别本题文字，请查看题库数据修正。";
  const source = String(question.stem || fallback);
  const table = extractResourceDemandTable(source);

  let textOnly = source;
  if (table) {
    textOnly = textOnly
      .replace(/\n?表\s*1[^\n]*/g, "")
      .replace(/\n?P\d+[：:]\s*最大需求\s*\d+[，,]\s*已分配\s*\d+[，,]\s*尚需\s*\d+/g, "")
      .trim();
  }

  const paragraphHtml = textOnly
    .split(/\n{2,}/)
    .map((paragraph) => paragraph.replace(/\n+/g, " ").trim())
    .filter(Boolean)
    .map((paragraph) => `<p class="stem-paragraph">${escapeHtml(paragraph)}</p>`)
    .join("");

  if (!table) {
    return paragraphHtml || `<p class="stem-paragraph">${escapeHtml(fallback)}</p>`;
  }

  const tableRows = table.rows
    .map(
      (row) => `<tr>
        <td>${escapeHtml(row.process)}</td>
        <td>${escapeHtml(row.maxDemand)}</td>
        <td>${escapeHtml(row.allocated)}</td>
        <td>${escapeHtml(row.needed)}</td>
      </tr>`
    )
    .join("");

  return `${paragraphHtml}
    <div class="stem-table-wrap">
      <div class="stem-table-caption">${escapeHtml(table.caption)}</div>
      <table class="stem-table">
        <thead>
          <tr>
            <th>进程</th>
            <th>最大需求数</th>
            <th>已分配资源数</th>
            <th>尚需资源数</th>
          </tr>
        </thead>
        <tbody>
          ${tableRows}
        </tbody>
      </table>
    </div>`;
}

function formatDuration(totalSeconds) {
  const safeSeconds = Math.max(0, Math.floor(totalSeconds));
  const hours = Math.floor(safeSeconds / 3600);
  const minutes = Math.floor((safeSeconds % 3600) / 60);
  const seconds = safeSeconds % 60;
  if (hours > 0) {
    return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  }
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("is-visible");
  clearTimeout(toastId);
  toastId = setTimeout(() => toast.classList.remove("is-visible"), 2200);
}

function setActiveTab() {
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.mode === state.mode);
  });
}

function startTimerIfNeeded() {
  clearInterval(timerId);
  if (state.mode !== "exam" || state.finished) {
    return;
  }
  timerId = setInterval(updateTimer, 1000);
  updateTimer();
}

function updateTimer() {
  if (state.mode !== "exam" || state.finished) {
    return;
  }
  const remainingMs = state.deadline - Date.now();
  const timerElement = document.querySelector("[data-timer]");
  if (timerElement) {
    timerElement.textContent = formatDuration(remainingMs / 1000);
    timerElement.closest(".timer")?.classList.toggle("is-low", remainingMs <= 10 * 60 * 1000);
  }
  if (remainingMs <= 0) {
    submitPaper(true);
  }
}

function answeredCount(paper = currentObjectivePaper()) {
  return paper.questions.filter((question) => state.answers[question.number]).length;
}

function computeResult(autoSubmitted = false) {
  const paper = currentObjectivePaper();
  const wrongNumbers = [];
  const unansweredNumbers = [];
  let correct = 0;

  for (const question of paper.questions) {
    const selected = state.answers[question.number];
    if (!selected) {
      unansweredNumbers.push(question.number);
    } else if (selected === question.answer) {
      correct += 1;
    } else {
      wrongNumbers.push(question.number);
    }
  }

  const usedSeconds = Math.max(0, Math.floor((Date.now() - state.startedAt) / 1000));
  return {
    paperId: paper.id,
    score: correct,
    correct,
    wrong: wrongNumbers.length,
    unanswered: unansweredNumbers.length,
    wrongNumbers,
    unansweredNumbers,
    usedSeconds,
    autoSubmitted,
    submittedAt: new Date().toISOString(),
  };
}

function submitPaper(autoSubmitted = false) {
  const paper = currentObjectivePaper();
  const unanswered = paper.questions.length - answeredCount(paper);
  if (!autoSubmitted && unanswered > 0) {
    const confirmed = window.confirm(`还有 ${unanswered} 道题未作答，确认交卷吗？`);
    if (!confirmed) {
      return;
    }
  }
  state.result = computeResult(autoSubmitted);
  state.finished = true;
  saveJson(resultKey(paper.id), state.result);
  clearInterval(timerId);
  render();
  showToast(autoSubmitted ? "时间到，已自动交卷。" : "已交卷，系统完成判分。可以逐题复盘。");
}

function resetCurrentPaper() {
  const paper = currentObjectivePaper();
  const confirmed = window.confirm("确认清空本卷作答并重新计时吗？");
  if (!confirmed) {
    return;
  }
  state.answers = {};
  state.result = null;
  state.finished = false;
  state.questionNumber = 1;
  state.pageIndex = 0;
  state.startedAt = Date.now();
  state.deadline = Date.now() + paper.durationMinutes * 60 * 1000;
  saveExamState(paper.id);
  localStorage.removeItem(answerKey(paper.id));
  localStorage.removeItem(resultKey(paper.id));
  render();
  showToast("已重置本卷。新的一轮开始了。 ");
}

function exportAnswers() {
  const paper = currentObjectivePaper();
  const exportData = {
    paperTitle: paper.title,
    exportTime: new Date().toLocaleString('zh-CN'),
    totalScore: paper.totalScore,
    questions: []
  };
  
  // 为每个题目收集数据
  for (const q of paper.questions) {
    const userAnswer = state.answers[q.number] || "";
    const isCorrect = userAnswer === q.answer;
    
    exportData.questions.push({
      number: q.number,
      stem: q.stem,
      options: q.options,
      correctAnswer: q.answer,
      correctOptionText: q.correctOptionText,
      userAnswer: userAnswer,
      isCorrect: isCorrect,
      explanation: q.explanation || {}
    });
  }
  
  // 生成JSON文件
  const fileName = `${paper.id}_answers_${new Date().getTime()}.json`;
  const jsonStr = JSON.stringify(exportData, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json;charset=utf-8' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(link.href);
  
  showToast(`已导出答题记录到 ${fileName}`);
}

function switchObjectivePaper(paperId) {
  const paper = objectivePapers.find((item) => item.id === paperId);
  if (!paper) {
    return;
  }
  state.paperId = paper.id;
  state.questionNumber = 1;
  state.pageIndex = 0;
  state.answers = loadJson(answerKey(paper.id), {});
  state.result = loadJson(resultKey(paper.id), null);
  state.finished = Boolean(state.result);
  const examState = loadExamState(paper);
  state.startedAt = examState.startedAt;
  state.deadline = examState.deadline;
  render();
}

function setQuestion(number) {
  const paper = currentObjectivePaper();
  const safeNumber = Math.min(paper.questions.length, Math.max(1, Number(number)));
  state.questionNumber = safeNumber;
  render();
}

function setPage(index, subjective = false) {
  if (subjective) {
    state.subjectivePageIndex = Math.max(0, Number(index));
  } else {
    state.pageIndex = Math.max(0, Number(index));
  }
  render();
}

function selectAnswer(questionNumber, answer) {
  if (state.mode === "exam" && state.finished) {
    return;
  }
  const paper = currentObjectivePaper();
  state.answers[questionNumber] = answer;
  saveJson(answerKey(state.paperId), state.answers);
  if (state.questionNumber === questionNumber && questionNumber < paper.questions.length) {
    state.questionNumber = questionNumber + 1;
  }
  render();
}

function getWrongSet(paperId = state.paperId) {
  const result = state.result?.paperId === paperId ? state.result : loadJson(resultKey(paperId), null);
  return new Set(result?.wrongNumbers || []);
}

function getMasteredSet(paperId = state.paperId) {
  return new Set(state.mastered[paperId] || []);
}

function toggleMastered(questionNumber) {
  const set = getMasteredSet();
  if (set.has(questionNumber)) {
    set.delete(questionNumber);
  } else {
    set.add(questionNumber);
  }
  state.mastered[state.paperId] = Array.from(set).sort((a, b) => a - b);
  saveJson("sa-mastered", state.mastered);
  render();
}

function visibleQuestionsForGrid(paper) {
  if (state.mode !== "study") {
    return paper.questions;
  }
  const wrongSet = getWrongSet(paper.id);
  const masteredSet = getMasteredSet(paper.id);
  if (state.studyFilter === "wrong") {
    return paper.questions.filter((question) => wrongSet.has(question.number));
  }
  if (state.studyFilter === "unmastered") {
    return paper.questions.filter((question) => !masteredSet.has(question.number));
  }
  return paper.questions;
}

function renderPaperOptions(papers, selectedId) {
  return papers
    .map((paper) => `<option value="${paper.id}" ${paper.id === selectedId ? "selected" : ""}>${escapeHtml(paper.title)}</option>`)
    .join("");
}

function renderAnswerGrid(paper) {
  const visibleQuestions = visibleQuestionsForGrid(paper);
  const wrongSet = getWrongSet(paper.id);
  if (visibleQuestions.length === 0) {
    return `<p class="muted">当前筛选没有题目。完成一次交卷后，错题会自动进入错题筛选。</p>`;
  }
  return `<div class="answer-grid">${visibleQuestions
    .map((question) => {
      const selected = state.answers[question.number];
      const classes = ["answer-cell"];
      if (question.number === state.questionNumber) classes.push("is-current");
      if (selected) classes.push("is-answered");
      if ((state.finished || state.mode === "study") && selected) {
        classes.push(selected === question.answer ? "is-correct" : "is-wrong");
      } else if (state.mode === "study" && wrongSet.has(question.number)) {
        classes.push("is-wrong");
      }
      return `<button class="${classes.join(" ")}" type="button" data-action="jump-question" data-number="${question.number}" title="第 ${question.number} 题">${question.number}</button>`;
    })
    .join("")}</div>`;
}

function renderTimerBlock(paper) {
  const remainingSeconds = Math.max(0, Math.floor((state.deadline - Date.now()) / 1000));
  return `<div class="timer ${remainingSeconds <= 600 ? "is-low" : ""}">
    <span>剩余时间</span>
    <strong data-timer>${formatDuration(remainingSeconds)}</strong>
    <span>考试时长</span>
    <span>${paper.durationMinutes} 分钟</span>
  </div>`;
}

function renderFinishedBlock(result) {
  return `<div class="timer">
    <span>交卷状态</span>
    <strong>已提交</strong>
    <span>判分结果</span>
    <span>${result ? `${result.score}/75 分 · 用时 ${formatDuration(result.usedSeconds)}` : "可查看逐题解析"}</span>
  </div>`;
}

function renderResultSummary(result, paper) {
  if (!result) {
    return "";
  }
  const accuracy = Math.round((result.correct / paper.questions.length) * 100);
  const passed = result.score >= paper.passingScore;
  return `<div class="result-summary">
    <div class="result-box"><span>得分</span><strong>${result.score}/${paper.totalScore}</strong></div>
    <div class="result-box"><span>正确率</span><strong>${accuracy}%</strong></div>
    <div class="result-box"><span>错题</span><strong>${result.wrong}</strong></div>
    <div class="result-box"><span>用时</span><strong>${formatDuration(result.usedSeconds)}</strong></div>
  </div>
  <div class="result-toolbar">
    <span class="status-badge ${passed ? "pass" : "fail"}">${passed ? "达到 45 分合格线" : "未达到 45 分合格线"}</span>
    <span class="muted">未答 ${result.unanswered} 题${result.autoSubmitted ? " · 时间到自动交卷" : ""}</span>
  </div>`;
}

function renderChoices(question, selected, reveal) {
  return `<div class="choice-list">${optionKeys
    .map((key) => {
      const text = question.options[key] || "见原卷对应选项";
      const classes = ["choice-item"];
      if (selected === key) classes.push("is-selected");
      if (reveal && question.answer === key) classes.push("is-correct");
      if (reveal && selected === key && selected !== question.answer) classes.push("is-wrong");
      const disabled = state.mode === "exam" && state.finished ? "disabled" : "";
      return `<label class="${classes.join(" ")}">
        <span class="choice-key">${key}</span>
        <span class="choice-text">${escapeHtml(text)}</span>
        <input class="choice-radio" type="radio" name="choice-${question.number}" value="${key}" data-action="answer-choice" data-question="${question.number}" ${selected === key ? "checked" : ""} ${disabled} />
      </label>`;
    })
    .join("")}</div>`;
}

function renderExplanation(question, selected) {
  const selectedText = selected ? question.options[selected] || "见原卷对应选项" : "未作答";
  const correctText = question.correctOptionText || question.options[question.answer] || "见原卷对应选项";
  const topicHint = topicHints[question.topic] || topicHints.综合知识;
  const isCorrect = selected === question.answer;
  const verdict = isCorrect ? "本题作答正确。" : selected ? `你选择了 ${selected}，需要回到题干限定条件重新辨析。` : "本题未作答，复盘时先独立完成一次再看答案。";
  // 使用新的explanation字段（如果存在）
  const expl = question.explanation || {};
  const keyPts = expl.keyPoints || [question.topic];
  const analysisText = expl.analysis || `正确答案：${question.answer} - ${correctText}`;
  
  // 生成知识点标签HTML
  const kpHtml = keyPts.map(kp => `<span class="key-point-tag">${escapeHtml(kp)}</span>`).join(" ");
  
  // 格式化分析文本
  const formattedAnalysis = analysisText
    .split('\n')
    .map(line => line.trim())
    .filter(l => l)
    .map(line => `<p>${escapeHtml(line)}</p>`)
    .join('');
  
  return `<section class="explanation">
    <h3>第 ${question.number} 题解析</h3>
    <div class="answer-feedback">
      <p><strong>正确答案：</strong><span class="answer-label">${question.answer}</span> - ${escapeHtml(correctText)}</p>
      <p><strong>你的答案：</strong>${selected || "未作答"}${selected && selectedText ? ` - ${escapeHtml(selectedText)}` : ""}　${verdict}</p>
    </div>
    ${kpHtml ? `<div class="key-points"><strong>知识点：</strong>${kpHtml}</div>` : ''}
    <div class="detailed-analysis">
      ${formattedAnalysis}
    </div>
  </section>`;
}

function renderObjective() {
  const paper = currentObjectivePaper();
  const question = currentQuestion();
  const selected = state.answers[question.number];
  const reveal = state.finished || state.mode === "study" || state.revealMap[`${paper.id}-${question.number}`];
  const masteredSet = getMasteredSet(paper.id);
  const result = state.finished ? state.result : null;

  app.innerHTML = `<div class="workspace">
    <aside class="panel side-panel">
      <div class="panel-title"><h2>${state.mode === "exam" ? "考试控制" : "学习控制"}</h2></div>
      <label class="small-label" for="paper-select">试卷</label>
      <select id="paper-select" data-action="select-paper">
        ${renderPaperOptions(objectivePapers, paper.id)}
      </select>
      ${state.mode === "exam" ? (state.finished ? renderFinishedBlock(state.result) : renderTimerBlock(paper)) : renderStudyControls()}
      <div class="metric-grid">
        <div class="metric"><span>已答</span><strong>${answeredCount(paper)}/${paper.questions.length}</strong></div>
        <div class="metric"><span>当前</span><strong>${question.number}</strong></div>
        <div class="metric"><span>合格线</span><strong>${paper.passingScore}</strong></div>
        <div class="metric"><span>题数</span><strong>${paper.questions.length}</strong></div>
      </div>
      <div class="exam-note">原卷与答案页已隐藏；交卷后才显示答案和解析。</div>
      ${renderAnswerGrid(paper)}
      <div class="toolbar-group" style="margin-top: 14px; width: 100%; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
        <button class="secondary-button" type="button" data-action="reset-paper">重做本卷</button>
        ${state.mode === "exam" && !state.finished ? `<button class="primary-button" type="button" data-action="submit-paper">提交试卷</button>` : ""}
        ${(state.mode === "exam" && state.finished) || state.mode === "study" ? `<button class="secondary-button" type="button" data-action="export-answers">导出答题记录</button>` : ""}
      </div>
    </aside>

    <section class="panel question-panel">
      <div class="panel-title">
        <div>
          <h2>${escapeHtml(paper.title)}</h2>
          <span class="muted">模拟答题区</span>
        </div>
      </div>
      ${renderResultSummary(result, paper)}
      <div class="question-toolbar">
        <div class="toolbar-group">
          <span class="question-number">${question.number}</span>
          <span class="topic-badge">${escapeHtml(question.topic)}</span>
          ${masteredSet.has(question.number) ? `<span class="status-badge pass">已掌握</span>` : ""}
        </div>
        <div class="toolbar-group">
          <button class="icon-button" type="button" data-action="prev-question" title="上一题">‹</button>
          <button class="icon-button" type="button" data-action="next-question" title="下一题">›</button>
        </div>
      </div>
      <div class="question-stem">${renderQuestionStem(question)}</div>
      ${renderChoices(question, selected, reveal)}
      <div class="toolbar-group" style="justify-content: space-between; width: 100%; margin-top: 12px;">
        ${state.mode === "study" ? `<button class="secondary-button" type="button" data-action="toggle-reveal" data-question="${question.number}">${reveal ? "隐藏解析" : "显示解析"}</button>` : `<span class="muted">${state.finished ? "已交卷，可逐题查看解析" : "选择答案会自动保存"}</span>`}
        ${state.mode === "study" ? `<button class="secondary-button" type="button" data-action="toggle-mastered" data-question="${question.number}">${masteredSet.has(question.number) ? "取消掌握" : "标记掌握"}</button>` : ""}
      </div>
      ${reveal ? renderExplanation(question, selected) : ""}
    </section>
  </div>`;
}

function renderStudyControls() {
  return `<div style="margin-top: 14px;">
    <span class="small-label">刷题筛选</span>
    <div class="segmented" role="group" aria-label="学习筛选">
      <button type="button" data-action="study-filter" data-filter="all" class="${state.studyFilter === "all" ? "is-active" : ""}">全部</button>
      <button type="button" data-action="study-filter" data-filter="wrong" class="${state.studyFilter === "wrong" ? "is-active" : ""}">错题</button>
      <button type="button" data-action="study-filter" data-filter="unmastered" class="${state.studyFilter === "unmastered" ? "is-active" : ""}">未掌握</button>
    </div>
  </div>`;
}

function renderSubjective() {
  const paper = currentSubjectivePaper();
  if (paper.caseItems?.length) {
    renderCasePaper(paper);
    return;
  }
  const draft = localStorage.getItem(draftKey(paper.id)) || "";
  const score = localStorage.getItem(scoreKey(paper.id)) || "";
  app.innerHTML = `<div class="subject-workspace">
    <section class="panel document-panel">
      <div class="panel-title">
        <div>
          <h2>${escapeHtml(paper.title)}</h2>
          <span class="muted">建议限时 ${paper.durationMinutes} 分钟 · 题面已从原卷 OCR 提取，答案默认隐藏</span>
        </div>
      </div>
      <label class="small-label" for="subject-paper-select">训练卷</label>
      <select id="subject-paper-select" data-action="select-subjective-paper">
        ${renderPaperOptions(subjectivePapers, paper.id)}
      </select>
      <section class="reference question-text-panel"><h3>题目正文</h3>${escapeHtml(paper.paperText)}</section>
    </section>

    <section class="panel subject-panel">
      <div class="panel-title">
        <h2>${paper.type === "essay" ? "论文写作区" : "案例作答区"}</h2>
        <span class="topic-badge">${paper.totalScore} 分</span>
      </div>
      <label class="small-label" for="subject-answer">作答草稿</label>
      <textarea id="subject-answer" data-action="subject-draft" placeholder="在这里限时作答。草稿会自动保存在本机浏览器。">${escapeHtml(draft)}</textarea>
      <div class="check-list">
        <label><input type="checkbox" /> <span>逐条回应了题目中的所有小问。</span></label>
        <label><input type="checkbox" /> <span>使用了系统架构师考试常见术语，并结合题干场景展开。</span></label>
        <label><input type="checkbox" /> <span>案例题写出依据、过程和结论；论文题有项目背景、方法和效果。</span></label>
      </div>
      <label class="small-label" for="self-score">自评分</label>
      <input id="self-score" class="score-input" data-action="subject-score" type="number" min="0" max="75" value="${escapeHtml(score)}" placeholder="0-75" />
      <div class="toolbar-group" style="justify-content: space-between; width: 100%; margin: 12px 0;">
        <button class="secondary-button" type="button" data-action="toggle-reference">${state.showReference ? "隐藏参考答案" : "显示参考答案"}</button>
        <button class="ghost-button" type="button" data-action="clear-subjective">清空草稿</button>
      </div>
      ${state.showReference ? `<section class="reference"><h3>参考答案 / 评分要点</h3>${escapeHtml(paper.reference)}</section>` : `<section class="reference"><h3>作答提示</h3>先按考试节奏完成草稿，再打开参考答案对照。重点检查：是否覆盖所有小问、是否给出架构术语和场景依据、是否写出结论与理由。</section>`}
    </section>
  </div>`;
}

function renderCasePaper(paper) {
  const item = paper.caseItems[Math.min(state.subjectiveItemIndex, paper.caseItems.length - 1)];
  const draft = loadJson(caseDraftKey(paper.id, item.id), {});
  const fieldGroups = groupedCaseFields(item);
  app.innerHTML = `<div class="case-workspace">
    <aside class="panel side-panel">
      <div class="panel-title"><h2>案例训练</h2></div>
      <label class="small-label" for="subject-paper-select">训练卷</label>
      <select id="subject-paper-select" data-action="select-subjective-paper">
        ${renderPaperOptions(subjectivePapers, paper.id)}
      </select>
      <div class="exam-note">案例题已按题面重排成结构化填空页，原卷答案不会直接暴露。</div>
      <div class="case-nav">
        ${paper.caseItems
          .map((caseItem, index) => `<button class="case-nav-item ${index === state.subjectiveItemIndex ? "is-active" : ""}" type="button" data-action="select-case-item" data-index="${index}">
            <span>案例 ${index + 1}</span>
            <strong>${escapeHtml(caseItem.title.replace(/^试题[一二三四五六七八九十]：?/, ""))}</strong>
          </button>`)
          .join("")}
      </div>
    </aside>
    <section class="panel subject-panel case-panel">
      <div class="panel-title">
        <div>
          <h2>${escapeHtml(item.title)}</h2>
          <span class="muted">建议先独立作答，再查看参考答案</span>
        </div>
        <span class="topic-badge">案例 ${state.subjectiveItemIndex + 1}/${paper.caseItems.length}</span>
      </div>
      <section class="case-section">
        <h3>题目说明</h3>
        <p>${escapeHtml(item.scenario)}</p>
      </section>
      <section class="case-section">
        <h3>问题</h3>
        <ol>${item.questions.map((question) => `<li>${escapeHtml(question)}</li>`).join("")}</ol>
      </section>
      <section class="case-section">
        <h3>需要填写的内容</h3>
        <div class="field-groups compact-field-groups">
          ${fieldGroups
            .map(
              (group) => `<div class="field-group">
                <h4>${escapeHtml(group.title)}</h4>
                <div class="fill-grid">${group.fields.map((field) => `<span>${escapeHtml(field.label)}</span>`).join("")}</div>
              </div>`
            )
            .join("")}
        </div>
      </section>
      <section class="case-section">
        <h3>逐项作答</h3>
        <div class="field-groups">
          ${fieldGroups
            .map(
              (group) => `<section class="field-group answer-field-group">
                <h4>${escapeHtml(group.title)}</h4>
                <div class="field-answer-grid">
                  ${group.fields
                    .map(
                      (field) => `<div class="field-answer ${field.isRange ? "" : "field-answer-wide"}">
                        <label for="case-${escapeHtml(item.id)}-${escapeHtml(field.key)}">${escapeHtml(field.label)}</label>
                        <textarea id="case-${escapeHtml(item.id)}-${escapeHtml(field.key)}" data-action="case-field-draft" data-item="${item.id}" data-field="${field.key}" placeholder="填写${escapeHtml(field.label)}">${escapeHtml(draft[field.key] || "")}</textarea>
                        ${state.showReference ? renderCaseFieldGuidance(item.id, field) : ""}
                      </div>`
                    )
                    .join("")}
                </div>
              </section>`
            )
            .join("")}
        </div>
      </section>
      <div class="toolbar-group" style="justify-content: space-between; width: 100%; margin: 12px 0;">
        <button class="secondary-button" type="button" data-action="toggle-reference">${state.showReference ? "隐藏参考答案" : "显示参考答案"}</button>
        <button class="ghost-button" type="button" data-action="clear-case-draft" data-item="${item.id}">清空本题草稿</button>
      </div>
      ${state.showReference ? `<section class="reference"><h3>整题评分要点</h3>${escapeHtml(item.reference)}</section>` : `<section class="reference"><h3>作答提示</h3>先覆盖所有填写项，再检查答案是否包含定义、示例编号、分类依据和结论。案例题最好按“题号 - 答案 - 理由”组织。</section>`}
    </section>
  </div>`;
}

function render() {
  saveExamState();
  persistUiState();
  setActiveTab();
  if (state.mode === "subjective") {
    clearInterval(timerId);
    renderSubjective();
    return;
  }
  renderObjective();
  startTimerIfNeeded();
}

document.addEventListener("click", (event) => {
  const modeButton = event.target.closest("[data-mode]");
  if (modeButton) {
    state.mode = modeButton.dataset.mode;
    render();
    return;
  }

  const actionElement = event.target.closest("[data-action]");
  if (!actionElement) {
    return;
  }
  const action = actionElement.dataset.action;
  const paper = currentObjectivePaper();
  const question = currentQuestion();

  if (action === "jump-question") setQuestion(actionElement.dataset.number);
  if (action === "prev-question") setQuestion(question.number - 1);
  if (action === "next-question") setQuestion(question.number + 1);
  if (action === "page-prev") setPage(state.pageIndex - 1);
  if (action === "page-next") setPage(state.pageIndex + 1);
  if (action === "submit-paper") submitPaper(false);
  if (action === "reset-paper") resetCurrentPaper();
  if (action === "export-answers") exportAnswers();
  if (action === "toggle-reveal") {
    const key = `${paper.id}-${question.number}`;
    state.revealMap[key] = !state.revealMap[key];
    render();
  }
  if (action === "toggle-mastered") toggleMastered(question.number);
  if (action === "study-filter") {
    state.studyFilter = actionElement.dataset.filter;
    render();
  }
  if (action === "subject-page-prev") setPage(state.subjectivePageIndex - 1, true);
  if (action === "subject-page-next") setPage(state.subjectivePageIndex + 1, true);
  if (action === "toggle-reference") {
    state.showReference = !state.showReference;
    render();
  }
  if (action === "select-case-item") {
    state.subjectiveItemIndex = Number(actionElement.dataset.index || 0);
    state.showReference = false;
    render();
  }
  if (action === "clear-case-draft") {
    const itemId = actionElement.dataset.item;
    const confirmed = window.confirm("确认清空当前案例草稿吗？");
    if (confirmed) {
      localStorage.removeItem(caseDraftKey(currentSubjectivePaper().id, itemId));
      render();
    }
  }
  if (action === "clear-subjective") {
    const subjectPaper = currentSubjectivePaper();
    const confirmed = window.confirm("确认清空当前主观题草稿吗？");
    if (confirmed) {
      localStorage.removeItem(draftKey(subjectPaper.id));
      localStorage.removeItem(scoreKey(subjectPaper.id));
      render();
    }
  }
});

document.addEventListener("change", (event) => {
  const actionElement = event.target.closest("[data-action]");
  if (!actionElement) {
    return;
  }
  const action = actionElement.dataset.action;
  if (action === "select-paper") switchObjectivePaper(actionElement.value);
  if (action === "answer-choice") selectAnswer(Number(actionElement.dataset.question), actionElement.value);
  if (action === "select-subjective-paper") {
    state.subjectiveId = actionElement.value;
    state.subjectivePageIndex = 0;
    state.subjectiveItemIndex = 0;
    state.showReference = false;
    render();
  }
  if (action === "subject-score") {
    localStorage.setItem(scoreKey(currentSubjectivePaper().id), actionElement.value);
    showToast("自评分已保存。");
  }
});

document.addEventListener("input", (event) => {
  const actionElement = event.target.closest("[data-action]");
  if (!actionElement) {
    return;
  }
  if (actionElement.dataset.action === "subject-draft") {
    localStorage.setItem(draftKey(currentSubjectivePaper().id), actionElement.value);
  }
  if (actionElement.dataset.action === "case-field-draft") {
    const key = caseDraftKey(currentSubjectivePaper().id, actionElement.dataset.item);
    const draft = loadJson(key, {});
    draft[actionElement.dataset.field] = actionElement.value;
    saveJson(key, draft);
  }
});

render();