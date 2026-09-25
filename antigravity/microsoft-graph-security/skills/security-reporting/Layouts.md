# Layouts

A spec is `{"title", "subtitle"?, "short_title"?, "pages": [...]}`. Pages render in order, numbered
("1. The plan"). Each page type:

| Type | Use for | Fields |
|---|---|---|
| `summary` | Page 1. The whole story | `before_after` {`before_label`, `before_value`, `before_caption`, `after_*`} (optional) · `sections`: [{`heading`, `bullets`[] **or** `text`, `callout`?}] |
| `table` | Inventories, "what happens to each", appendices | `headers`[], `rows`[][], `widths`[]?, `notes`[]?, `answer_column`? (1-based, yellow) |
| `flow` | A before → after diagram in box-drawing characters | `lines`[] (monospace; first line bold), `note`? |
| `steps` | A plan's sequence | `headers` (Step, What, What users notice, How long), `rows` |
| `decisions` | Open questions | `headers` (#, Question, Suggestion, Your answer), `rows` — last column is the yellow answer box |

Every page takes `name` (the tab), and optionally `title` and `subtitle`.

## Which pages for which report

| Report | Pages |
|---|---|
| **Inventory** ("show me the X") | summary · table (one row per item) · table (appendix: every sub-item) |
| **Clean-up / merge plan** | summary · flow · table (each old item → where it goes) · table (the new thing) · steps · decisions |
| **Findings for leadership** | summary · table (findings, most severe first) · decisions |

## Flow diagrams

Keep lines under ~90 characters. Left column = today, right = after; `┐ ┘ ┤ ┴ ├ └ ─ ► →` for joins.
A flow belongs on its own page right after the summary — it is the page people remember.
