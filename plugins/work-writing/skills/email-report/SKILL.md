---
name: email-report
description: Write a short English email reporting the root cause of an investigated system issue (bug / log ticket), in Jason's fixed style ("Dear Cody, After checking, I have found the cause. ..."). Use when the user runs /email-report or asks to write an issue / root-cause report email.
argument-hint: "[recipient] [extra instructions, e.g. add fix line, Fig. 1 = ..., Fig. 2 = ...]"
---

# /email-report

Write a short root-cause report email in English, based on the investigation in the current conversation (or the details the user gives in the arguments).

## Inputs

- `$ARGUMENTS` may contain: a recipient name, figure descriptions, and extra instructions.
- Recipient: default **Cody**. Use another name only if the user gives one.
- Facts come from the conversation: findings, query results, IDs, dates, error messages. Do not invent facts. If a key fact is missing (e.g. staff no., effective date, exact error text), ask the user before writing.

## Output

- Print the email in the reply only, as plain text ready to copy. Do not save it to a file.
- After the email, add at most 2-3 short notes in Traditional Chinese (per the user's global rules) only when needed, e.g. a placeholder to fill in or a fact you are not sure of. No notes if nothing needs attention.

## Structure (fixed)

```
Dear <Recipient>,

After checking, I have found the cause.

<Paragraph 1: the facts / data state that triggers the issue.>

<Paragraph 2 (optional): how the system logic hits that state and fails, with the exact error.>

<Figure captions, only if figures are used>

Regards,
Jason
```

- Opening line is always exactly: `After checking, I have found the cause.`
- Closing is always `Regards,` then `Jason`.
- Do **not** add a fix / next-step / apology sentence unless the user asks for it. If asked, add one short sentence as the last body paragraph.
- No subject line unless the user asks for one.

## Writing rules

- 1-2 body paragraphs, plain and factual. Short sentences, no jargon beyond table / column / ID names.
- Name the person by role and staff number: "The applicant (staff no. 009743)", "The staff member (staff no. 003832)".
- Cite exact identifiers so the reader can verify: table names (e.g. `HRM_STAFF_SALARY_PACKAGE`), key IDs (`sys_id 100083124`, `LR_SEQ_NUM 1041956`), dates in `YYYY-MM-DD`, and input date when relevant ("effective 2026-09-01 (input on 2026-09-15)").
- Explain the chain: data state -> why it conflicts with the system logic -> visible symptom, ending with the exact error text in quotes (e.g. fails with "NullReferenceException", fails with "Subquery returned more than 1 value").
- Say clearly whether the data is valid or wrong when it matters (e.g. "This setup is valid, because ...").
- Mention where the error is visible if it is not shown to the user (e.g. "it only appears in the event log").
- Do not include code blocks, SQL, or stack traces in the email body. Those go into figures provided by the user.
- Include whatever data the user provides; do not filter it.

## Figures

- Add figure references only when they help, or when the user asks / provides figures. The user supplies the actual images.
- In the body, put `(Fig. 1)`, `(Fig. 2)` right after the statement the figure supports.
- Before `Regards,`, list one caption per figure: `Fig. N: <what it shows>`. Add `(Problem: <short point>)` when the figure shows the defect.
- Number figures in the order they are first referenced.

## Examples

Example 1 (with figures):

```
Dear Cody,

After checking, I have found the cause.

The staff member (staff no. 003832) has two basic salary records in HRM_STAFF_SALARY_PACKAGE effective 2026-09-10: one for cycle SKH-Mth (sys_id 100083124) and one for cycle SKH-OT (sys_id 100083125) (Fig. 1). This setup is valid, because each payroll cycle can have its own salary package.

However, when the Bank Payment Report looks up the basic salary, it does not filter by cycle (Fig. 2), so it finds two records instead of one. The query then fails with "Subquery returned more than 1 value", and the report shows no details. The error is not shown on screen; it only appears in the event log.

Fig. 1: Basic salary record in HRM_STAFF_SALARY_PACKAGE

Fig. 2: Current basic salary subquery in the Bank Payment Report (Problem: no cycle filter)

Regards,
Jason
```

Example 2 (no figures):

```
Dear Cody,

After checking, I have found the cause.

The applicant (staff no. 009743) was moved to rank 100000171 effective 2026-09-01 (input on 2026-09-15). The applicant is full-time, but the only Annual Leave setting of this rank in HRM_LR_LEAVE_RANK (LR_SEQ_NUM 1041956) is for part-time staff only. As a result, the system cannot find a leave policy for the applicant, and the approval fails with the "NullReferenceException".

Regards,
Jason
```
