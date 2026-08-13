# Task: 建立 `study-notes` Claude Code Plugin

你要從零建立一個名為 `study-notes` 的 Claude Code plugin。這個 plugin 的用途是：
把一個學習主題拆解成結構化的 study plan，然後分批生成 Obsidian 格式的 markdown 筆記。

先完整讀完本文件再動手。**不要**急著寫檔案，先按最後的「執行順序」逐步進行。

---

## 0. 前置查證（必做）

本文件的 schema 描述可能已過時。動手前先確認以下三件事的當前規格：

1. `plugin.json` 的欄位 schema 與必填項
2. `hooks/hooks.json` 的格式與可用的 lifecycle events
3. `agents/*.md` 的 frontmatter 欄位

查證來源優先序：`code.claude.com/docs/en/plugins-reference` > 官方 docs 其他頁 > 你的既有知識。
若查到的規格與本文件衝突，**以查到的為準**，並在完成後的報告中明確指出哪裡不同。

---

## 1. 設計理念（理解這幾點，實作才會對）

| 原則 | 說明 | 違反的後果 |
| --- | --- | --- |
| **State 存在磁碟，不存在 context** | 進度寫進 `PLAN.md` 的 checkbox | session 中斷或 context 壓縮後無法續跑 |
| **Pilot 先行** | 第一篇筆記單獨產出並停下來給 user review | 批次寫完 8 篇才發現風格錯，全部重寫 |
| **每篇筆記獨立 context** | 用 subagent 寫單篇，不在主 context 連續生成 | 寫到第 5 篇時品質遞減、開始自我重複 |
| **冪等（idempotent）** | 重跑不覆蓋已完成的筆記 | 誤觸指令就毀掉既有成果 |
| **規範屬於 vault，不屬於 plugin** | 寫作風格讀自 vault 的 `.study/STYLE.md` | plugin 綁死單一使用者，無法通用 |
| **確定性檢查交給 hook** | frontmatter 格式驗證用 hook，不用 model 判斷 | 浪費 token 且不可靠 |

---

## 2. 目錄結構

```
study-notes/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── study-plan/
│   │   ├── SKILL.md
│   │   └── reference/
│   │       └── plan-schema.md
│   ├── study-build/
│   │   ├── SKILL.md
│   │   └── reference/
│   │       └── note-template.md
│   └── study-status/
│       └── SKILL.md
├── agents/
│   └── note-writer.md
├── hooks/
│   └── hooks.json
├── scripts/
│   └── validate_frontmatter.py
└── README.md
```

**重要**：只有 `plugin.json` 放在 `.claude-plugin/` 裡。
`skills/`、`agents/`、`hooks/`、`scripts/` 一律放在 plugin 根目錄。
把組件目錄放進 `.claude-plugin/` 是官方文件明列的常見錯誤。

---

## 3. `plugin.json`

```jsonc
{
  "name": "study-notes",
  "displayName": "Study Notes Builder",
  "description": "Plan-then-build structured markdown notes for a learning topic",
  "author": { "name": "Jason" },
  "license": "MIT",
  "keywords": ["notes", "learning", "obsidian", "knowledge-base"]
}
```

**刻意省略 `version`** — 開發期走 commit-SHA 版本策略，每次 push 即為新版本。
若宣告了 `version` 又不遞增，`/plugin update` 會因版本相同而略過，使用者永遠拿不到新版。

---

## 4. Context cost 約束（設計 skill 時必須遵守）

Skill 的 frontmatter `description` 是 **always-on** 成本——每個 session 無條件載入。
SKILL.md body 與 `reference/` 檔案是 **on-invoke**，只在觸發時才進 context。

因此：

| 內容 | 放哪 |
| --- | --- |
| 「何時該用這個 skill」 | frontmatter `description`（1–2 行，越短越好） |
| 主流程、決策點 | SKILL.md body |
| `PLAN.md` 完整格式規範、筆記模板、邊界情況 | `reference/*.md` |

**不要**把格式規範塞進 description 想確保 Claude 一定看到——那會讓每個 session 都付費。

---

## 5. 各元件規格

### 5.1 `skills/study-plan/SKILL.md` — Stage 1

**觸發**：使用者要為某個主題建立學習計畫時。

**流程**：

1. 接收 `concept`（主題）與 `goal`（學到什麼程度）。
   - `goal` 決定深度：「能用」與「能教別人」的 plan 結構差很多，必須明確。
   - 若使用者沒給 goal，**必須追問**，不要自行假設。
2. 讀取 `<vault>/.study/STYLE.md`（若不存在，用內建預設並提示使用者建立）。
3. **先查證再規劃**：對主題做 web search，確認近期是否有新增子題。
   憑既有知識直接生成 plan 會漏掉訓練資料截止後才出現的內容。
4. 生成 `PLAN.md` 寫入目標資料夾（格式見 `reference/plan-schema.md`）。
5. 停下來請使用者 review。**明確告知**：要修改直接編輯 `PLAN.md`，不需重跑本 skill。

**關鍵**：plan 必須寫成**檔案**，不是對話訊息。

### 5.2 `skills/study-plan/reference/plan-schema.md`

定義 `PLAN.md` 的格式：

```markdown
---
concept: <主題名稱>
goal: <學習目標>
created: <YYYY-MM-DD>
style: ../.study/STYLE.md
pilot_reviewed: false
---

## 1. <大 topic>
- [ ] 1.1 <子題>
- [ ] 1.2 <子題>

## 2. <大 topic>
- [ ] 2.1 <子題>
```

規則：
- 大 topic 用 `## <序號>. <名稱>`，對應輸出的資料夾名
- 子題用 checkbox，勾選狀態即為進度
- `pilot_reviewed` 控制 Stage 2 是否進入批次模式
- 大 topic 3–8 個，每個大 topic 底下 3–8 個子題；超出範圍表示拆解顆粒度不對

### 5.3 `skills/study-build/SKILL.md` — Stage 2 主控

**觸發**：使用者要根據既有 `PLAN.md` 生成筆記時。

**流程**：

```
讀 PLAN.md
  ↓
frontmatter 的 pilot_reviewed 為 false？
  ├─ 是 → 產出第一個未完成子題的筆記作為 pilot
  │        → 停下來，向使用者提出「具體」的 review 問題（見下）
  │        → 使用者確認後，把 pilot_reviewed 改為 true
  └─ 否 → 進入批次迴圈
  ↓
批次迴圈（逐個未完成子題）：
  1. 檢查目標檔案是否已存在 → 存在則跳過（除非使用者明確要求 --force）
  2. 派給 note-writer subagent（獨立 context）
  3. 寫入 <大topic資料夾>/<子題>.md
  4. 更新 PLAN.md 對應 checkbox 為 [x]
  5. 下一個
  ↓
單一大 topic 全部完成後：
  → 執行「交叉連結 pass」：回頭補 [[ ]] wikilink
     （逐篇寫的當下還不知道後面會有什麼，所以必須最後補）
  → 向使用者回報本 topic 完成，詢問是否有要調整的
  → 繼續下一個大 topic
```

**Pilot 的 review 問題必須具體**，不要問「這樣可以嗎」。要問：
- 表格與敘述的比例合適嗎？
- 深度是太淺還是太深？
- 技術術語的中英文處理方式對嗎？
- frontmatter 欄位需要增減嗎？

含糊的問題只會得到含糊的回饋，pilot 就白做了。

### 5.4 `agents/note-writer.md`

**唯一職責**：生成單篇筆記。

用 subagent 而非在主 context 直接寫，理由只有一個：**context 隔離**。
每篇筆記從乾淨的 context 開始，第 20 篇的品質與第 1 篇一致。

輸入（由 `study-build` 傳入）：
- 子題名稱與所屬大 topic
- `STYLE.md` 的內容
- `note-template.md` 的格式
- 已完成筆記的檔名清單（供 wikilink 參考）

要求：
- 不確定的內容標 `[VERIFY]`，不要編造
- 需要查證的技術細節先 web search
- 只輸出筆記檔案，不做額外說明

### 5.5 `hooks/hooks.json` + `scripts/validate_frontmatter.py`

在筆記寫入前驗證 frontmatter 是否符合規範（必要欄位齊全、日期格式正確、tags 為 array）。

- 驗證失敗 → 阻擋寫入並回報具體缺什麼
- 用 exit code 溝通，不需回傳 JSON
- script 路徑用 `${CLAUDE_PLUGIN_ROOT}` 引用

**重要**：plugin 會被複製到 cache 目錄執行，不是原地執行。
任何指向 plugin 目錄**外**的路徑都會失效。所有資源必須放在 plugin 內。

### 5.6 `skills/study-status/SKILL.md`

輕量 skill：讀 `PLAN.md`，回報完成度（幾 / 幾）、下一個待辦子題、pilot 是否已 review。

---

## 6. 執行順序

1. 完成第 0 節的查證
2. 建立目錄結構與 `plugin.json`
3. 寫 `study-plan` skill + 其 reference
4. 寫 `study-status` skill（最簡單，先驗證 plugin 能被載入）
5. 用 `claude --plugin-dir ./study-notes` 本地掛載測試，確認 skill 出現
6. 寫 `note-writer` agent
7. 寫 `study-build` skill
8. 寫 hook 與 validation script
9. 執行 `claude plugin validate ./study-notes --strict`，修正所有 error 與 warning
10. 寫 `README.md`：安裝方式、`.study/STYLE.md` 的建立說明、三個 skill 的用法

---

## 7. 驗收標準

- [ ] `claude plugin validate ./study-notes --strict` 零錯誤零警告
- [ ] `claude --plugin-dir ./study-notes` 掛載後三個 skill 皆可見
- [ ] 對一個測試主題跑完 Stage 1，`PLAN.md` 格式正確
- [ ] Stage 2 的 pilot 模式會停下來詢問，不會直接批次
- [ ] 重跑 `study-build` 不會覆蓋已存在的筆記
- [ ] frontmatter 缺欄位時 hook 確實阻擋
- [ ] 所有 skill 的 frontmatter `description` 皆在兩行以內

---

## 8. 完成後回報

1. 第 0 節查證中，發現與本文件描述不符之處（若有）
2. 實作過程中的設計取捨
3. 尚未驗證或你沒有把握的部分
4. 下一步建議

**不要**為了讓驗收看起來通過而美化結果。有問題直接說。
