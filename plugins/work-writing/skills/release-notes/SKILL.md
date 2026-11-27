---
name: release-notes
description: Write release-note lines in Traditional Chinese (e.g. "新增PE underspending 報表欄位 (SR0827)") for Jason's systems (HRMIS, MSGBOX, RFQ, MOS, TSMS, RFP2.0 ...), based on the change details, SR number, LOG number, background or email in the current conversation. Use when the user runs /release-notes or asks to write release notes / 更新內容.
argument-hint: "[change description, SR / LOG number, background or pasted email]"
---

# /release-notes

Write one release-note line per change, in Traditional Chinese, based on `$ARGUMENTS` and the current conversation.

## Inputs

Look in `$ARGUMENTS` and the conversation (including pasted emails, tickets, code diffs, investigation results) for:

- What changed (feature, report, field, logic, permission, bug fix).
- SR number, e.g. `SR0827`, `sr 827`, `SR-0883`.
- LOG number, e.g. `LOG/IT/038520`, `#LOG/IT/040904`.
- Background that tells you the change type (new / update / fix / remove ...).

Do not invent facts, SR numbers or LOG numbers.

## When to interview the user

Ask (short questions, in Traditional Chinese) before writing when:

- It is unclear **what** changed, or what object it affects (which report / page / field / function).
- It is unclear whether it is a new feature, an enhancement, or a bug fix.
- An email or ticket mentions several issues and it is unclear which ones were actually released.
- Both an SR and a LOG number appear for one change, and it is unclear which one to cite.

Do **not** ask when the only missing piece is the reference number. No number means the line has no suffix (format 3).

## Output format

Each line is one of:

1. `<內容> (#LOG/IT/xxxxxx)` — when a LOG number is given
2. `<內容> (SRxxxx)` — when an SR number is given
3. `<內容>` — when no number is given

Rules:

- Half-width brackets `( )`, with one space before `(`.
- LOG number: always `#LOG/IT/` + digits exactly as given, e.g. `(#LOG/IT/038520)`.
- SR number: uppercase `SR` + 4 digits, zero-padded, e.g. `sr 827` → `(SR0827)`.
- One change per line. Several changes → several lines; each line carries its own number.
- Output the content lines only: no title line (system name / version / 推出日期), no bullet `-`, no numbering.
- Print in the reply as plain text inside a code block, ready to copy. Do not save to a file.
- After the block, add at most 1-2 short notes in Traditional Chinese only when needed (e.g. an assumption you made). No notes if nothing needs attention.

## Writing style

- One short sentence, no full stop at the end.
- Start with a verb that states the change type:
  - `新增` — new feature / field / report / function
  - `更新` — change data, settings or logic
  - `優化` — improve display or usability
  - `更改` — change wording / layout
  - `修正` — bug fix, usually `修正……的問題` or `修正……之功能`
  - `移除` — remove a report / function
  - `開放` — grant a permission to a user group, e.g. `開放 X 功能權限予 SD用戶`
  - `實施` — introduce a mechanism, e.g. security
- Keep system terms and English names as they appear in the system (e.g. `PE underspending`, `budget`, `ECS`). Do not wrap function names, page names, field names or quoted wording in `「」` (or any other quote marks); write them directly, with a space between English names and the surrounding Chinese text.
- Use `之` / `中` / `內` for connectors as in the examples (`報表之原始數據列表邏輯`, `報表中金額數值`).
- Describe the result for the user, not the code (no table names, SQL, class names).
- Traditional Chinese, Hong Kong / Taiwan wording.

## Examples (from past release notes)

```
新增PE underspending 報表欄位 (SR0827)
更新PE underspending 報表之原始數據列表邏輯 (SR0827)
更新PE underspending 報表之中心訪問權限列表邏輯 (SR0827)
優化PE underspending 報表中金額數值增加千分位逗號顯示 (SR0883)
更改PE underspending 系統版面及報表中所有的 budget 字眼 (SR0883)
移除 PE Underspending (Actuals) 報表 (SR0845)
開放 Major PE Underspending Tools 功能權限予 SD用戶
修正PE歷史紀錄表內修改或建立用戶名稱顯示錯誤的問題
新增功能 : 上載規格說明的附件 (SR0690)
修正無法編輯報價記錄，因為編號已存在的問題 (#LOG/IT/027749)
實施數據庫欄位加密機制以提升安全性
更新銀行入帳中的戶口號碼共用ECS長者中心系統的銀行戶口號碼 (#LOG/IT/038520)
修正計算連續性合約（468 條例）之功能 (#LOG/IT/038785)
財務文件設置更新 (#LOG/IT/039551)
更新稅務年份及在個人稅單列印頁面中更新重要提示 (SR0826)
修正同工假期資料 (#LOG/IT/040904)
```
