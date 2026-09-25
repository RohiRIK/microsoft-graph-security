# Writing rules

Learned the hard way on a DLP plan that was "good for AI, but very not understandable".

## The reader

A security lead or manager who knows their tenant but not this repo, not PowerShell parameter
names, and not the analysis we did. They read page 1 and maybe one more.

## Rules

1. **Page 1 tells the whole story on one screen**: a before → after in big numbers, "what we
   found" in 3–4 bullets, "the plan in one sentence", "why it is safe". Everything else is detail.
2. **Their words, not ours.** No rule IDs (A1, X1), no internal flags (`DLP_NO_ACTION`), no API or
   cmdlet names (SIT, AccessScope, AdvancedRule). Say "data types", "shared outside the company",
   "only records".
3. **Name the tenant in the title** — every report says which company it is about.
4. **One row per thing the reader already knows** (a policy they can see in the portal), with:
   what it does today · what is wrong · what happens to it · keep or delete.
5. **Say what users will notice** for every step of a plan — usually "nothing".
6. **Decisions are questions with a suggestion** and an empty answer box, never an open list.
7. **Distinguish container from contents** when both appear (policy vs rule) — once, in plain words.
8. **Machine-level detail goes in an appendix tab at the back**, clearly named as such.
9. **Draft means draft.** Say "nothing has been changed" when it is a plan.

## Before handing it over

- Read the rendered file back (tab names, first rows, totals).
- Check totals equal the sum of their rows, and that each item lands in the category its name says.
- Say where it was saved, that it contains tenant names, and that it stays internal.
