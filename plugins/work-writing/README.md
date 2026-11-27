# work-writing

Writing skills for day-to-day system support work.

## Install

```
/plugin install work-writing --marketplace jltz1207/jason-plugins
```

## Skills

| Skill | Command | Output |
|---|---|---|
| email-report | `/work-writing:email-report [recipient] [extra instructions]` | Short English root-cause report email ("Dear Cody, After checking, I have found the cause. ...") |
| release-notes | `/work-writing:release-notes [change, SR / LOG no., background]` | One Traditional Chinese release-note line per change, e.g. `新增PE underspending 報表欄位 (SR0827)` |

Both skills print plain text in the reply and never write files.
