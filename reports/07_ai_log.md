# 5b · AI process log

Interactive version: https://miushkaenavimia.github.io/tune-analysis-submission/#p5b

**Bottom line:** AI wrote most of the SQL and text; I set the questions, the rules and the checks. This log lists 13 cases where the AI was wrong, worst first: I caught 9, Claude caught 3 by re-checking against the data, and a reviewer caught 1. Cases 1–9 would have changed the answers; those are the 8 rows on tab 5b (cases 3 and 4 share one row). No AI number went in until a DuckDB query on the full data confirmed it.

## 1. Tools and what each did

| Tool | Used for |
|:--|:--|
| **Claude (Claude Code, desktop app)** | Main analyst: profiling queries, the DuckDB pipeline (`sql/`), the clean layer, churn validation, Python report generators, the site. Ran every query against the real database. The model matched the task: Opus 5.5 built the pipeline, queries, reports and site; Fable handled a few of the most complex reasoning tasks; Sonnet 5.5, a lighter model, handled a narrow side task. I ran the work as a team of agents: one main session held the plan and the decisions, while many specialised sub-sessions worked in parallel, each on a single task such as data-quality checks, rechecking every number in DuckDB, cross-tab consistency or an examiner-style review. Most started fresh with a short brief to keep context small; plan mode reviewed the plan before any code was written, and memory files carried decisions between sessions. |
| **Gemini** | Second opinion: critical review of the Part 1a data-quality findings and of the churn window, drafts of page and chart design, and sharper wording. |
| **Claude Design** | Used separately for advice on the site's layout and design. |
| **NotebookLM** | Audio overviews of the reports, listened to while working. |

## 2. How I worked with them

- **Second opinions are checked, not trusted.** Every claim from Gemini was re-run in DuckDB before it went in.
- **No typed numbers.** Supporting numbers in the reports are computed by SQL at build time; text that drifted from the data was the trigger for this rule.
- **Every detection query is checked against its count.** If the query that lists an issue returns a different number of rows than the check that counts it, the build flags it.
- **Re-read the brief before ranking.** Severity = how much an issue changes the answers leadership asked for.
- **Same input, same output.** Consecutive runs of `run_all.py` give identical outputs.

## 3. Representative prompts

The three prompts that steered the work most are on tab 5b. Others, paraphrased from the chat, except the first, which is a file in the repo:

1. **Critical review (Gemini):** "You are a senior data analyst reviewing someone else's data-quality report. Be critical and specific. Do not praise. If you cannot verify a claim without the data, say so." Full prompt: `reports/gemini_review_prompt_1a.md`.
2. "Re-run Gemini's renewal-by-day numbers on the full data in DuckDB, using both export files."
3. "Break the days-to-renewal curve down by plan type and by Auto-renew vs Manual. Show % of returners by day."
4. "Rank the issues by how much they affect the four leadership questions, not by how many rows they touch."
5. "Implement billing's churn definition on the clean layer and compare it with `churn_labels.csv`. Explain every disagreement group."

## 4. Cases where the AI was wrong

| # | Tool | What it got wrong | Why that was wrong | What I did instead | Caught by |
|:--:|:--|:--|:--|:--|:--|
| 1 | Gemini | Reported a renewal spike on day 31 (17.5%; real 0.35%) and 33.4% churn (real 43.5%), with an invented "card declined" reason. | It had read only part of the data. Kept, it would have set the churn window around a spike that does not exist and reported churn about 10 points too low. | Claude re-ran it on the full data in DuckDB; Gemini then admitted it used a partial file. Since then every second opinion is re-run on the full data before it is used. | **Me.** The day-31 jump looked wrong. |
| 2 | Claude | Said discounts brought less revenue, by comparing the total revenue of the discounted group with that of the full-price group, which was 3.5 to 44 times larger, without dividing by the number of subscribers. | Groups of different sizes cannot be compared by their totals. Per subscriber, Auto-renew monthly subscribers at $149 who paid with a discount in Jan 2015 – Oct 2015 paid $1,700 each over the next 12 months, against $1,540 for those who paid full price (+10%), and every one of the 10 months points the same way. Kept, the report would have said the discount did not pay off. | Groups of different sizes are compared per subscriber, month by month; every tab was checked for the same wrong idea. | **Me**, from business sense: fewer subscribers got a discount, so their total was bound to be lower. |
| 3 | Claude | Kept billing's churn labels at Medium and defended "export split stays #1" without re-reading the brief's ranking rule. | The brief ranks by impact on leadership's answers, and the labels are likely the churn number the CEO already saw. At Medium, the biggest risk would have been hidden. | Re-read the brief. Labels moved to Critical, now issue #1. | **Me.** |
| 4 | Claude | Inconsistent ranking: 2015 missing plan length under-rated, and early renewals (578,644 rows) missing from the list. | Missing plan length touches 39.7% of users active Mar 2015 – Oct 2015. Kept, the list would have under-stated two problems that change the churn and plan answers. | Plan length moved to Critical; early renewals added at High (first rated Medium, then corrected). | **Me**, by asking about wrongly computed plan durations. |
| 5 | Claude | "Plan type doesn't change the churn window." | It looked at one renewal curve for everyone instead of splitting it by how people pay. Auto-renew returners are 98.0% back by day 1 and 98.5% by day 3, Manual monthly returners only 47.8% by day 1 and 95.1% by day 30. One 30-day window for everyone would have reported Auto-renew churn as 2.4% instead of 3.0%. | Renewal timing is checked per payment type before fixing the window: 3 days for Auto-renew, 30 days for Manual. 30 days for everyone stays as a side check, and 1c keeps it because the brief defines it there. | **Me.** "You were wrong, payment type changes it." |
| 6 | Claude | Counted 11,560 "conflicting versions" between the two exports by matching user + day, which is not a unique key. | Real conflicts: 747. Kept, about 10,800 real, separate purchases would have been dropped as duplicates. | Match on the whole event (user, day, method, plan, amount, cancel). Only true one-to-one matches count as the same event. | **Claude itself**, while building the clean layer. |
| 7 | Claude | Added a "Billing gap: Left out / Included" toggle to the Part 4 churn graph, but kept the same averages (4.9% and 4.3%) in both views. | With the gap months included, the averages are 6.2% and 5.1%. Kept, the graph would have hidden the billing gap's effect. | Each view now computes its own averages. | **Me**, by eye on the graph: switching the toggle did not change the averages, which made no sense. |
| 8 | Claude | Read `expires_at` two ways: in 1c as the last day of access, but in the active counts (`covered_end` in `fct_subscription`) as the first day without access. | The two parts were built at different times and never checked against each other. A plan ending on the 1st dropped out of that month's paying subscribers while its churn still counted there (Mar 2016 churn 14.0% instead of 13.8%). | One reading everywhere: the expiry date is the last day of access (`covered_end` = expiry + 1). The not-yet-known cut now follows each churn window. Every moved number re-run in DuckDB on the full data. | A reviewer's question about how the expiry date is read |
| 9 | Gemini | "All 109,330 users missing from `users.csv` are paying users." | Only 53,023 of them ever paid. Kept, the issue would have looked about twice as big as it is. | Sized the issue on paying users and reported their share of revenue (8.3%). | **Claude**, by re-running it in DuckDB. |
| 10 | Claude | Counted a user who paid on the last day of a month as having access for that whole month. | The billing failures looked shorter and cheaper than they really were. | Check that each metric measures what the question asks, not just something close to it. | **Me**: the dates did not make sense. |
| 11 | Gemini | Explained ages 106 and 112 with the Taiwan (ROC) calendar. | Most age-106 users registered in 2014-15, and 112 matches no recent ROC year. Kept, it would have "corrected" ages with a made-up rule. | Rejected the story. Impossible ages are handled by the cleaning rule in `stg_users`. | **Claude**, by checking registration years. |
| 12 | Claude | Loaded both exports straight into one "raw" table and added `src_file` / `src_row` at load. | Not a wrong number, a design flaw: the raw layer mixed loading with modelling (combining files, adding columns), so it could no longer be checked 1:1 against the files. | Split into exact raw tables (`raw_transactions_export_1`, `_2`), one per file, plus a separate step, `base_transactions` (`sql/00_union_exports.sql`), that combines them and adds lineage. Every downstream table was checked identical before and after. | **Me**, by asking whether loading the files as-is first, then combining in its own step, would be more correct. |
| 13 | Claude | Put only the transactions through STAGING; the users file was cleaned inside `dim_user`. | Not a wrong number, a design flaw: cleaning was split between two layers, so STAGING was not "the one place where cleaning happens". | New `stg_users` table holds all user cleaning; `dim_user` reads it. Every other table checked identical. | **Me**, by asking. |

**Cases 3-4 in detail: the AI's original 1a ranking vs the final one** (the original is the first version uploaded to GitHub; only issues that moved are shown):

| Issue | AI's original rank | Final rank |
|:--|:--:|:--:|
| Billing's churn labels | 10 · Medium | 1 · Critical |
| 2015 paid rows missing plan length | 3 · High | 2 · Critical |
| Exports split by expiry date | 1 · Critical | 3 · Critical |
| Gender missing | 11 · Medium | 6 · High |
| Free periods with no price | 6 · Medium | 8 · High |
| Early renewals | not listed | 9 · High |

**Also caught by Claude itself** (smaller): a loader bug that left the file path in every row; a non-repeatable tie-break that changed churn-label counts between runs; a first duplicate fix that still over-counted (1,561 rows instead of 747). All fixed; listed in `py/01_dq_outputs.py` (CORRECTIONS).

## 5. What I'd keep doing

- Use one AI to check the other, but let **the data** decide.
- Ask "how do you know?" when a number looks too clean or a story too neat.
- Keep a log like this one while working, not after.
