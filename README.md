# Tune subscription analysis (take-home)

Two years of messy billing exports, turned into clear answers for the CEO and the Head of Growth.

**Live site:** https://miushkaenavimia.github.io/tune-analysis-submission/
one tab per part of the brief, the data-quality report, a map of every table, and SQL on every table (raw and clean) right in the browser.

The four leadership questions:

- **Q1** How healthy is the subscriber base, and how is it trending?
- **Q2** What drives churn?
- **Q3** Did the free trials and price points work?
- **Q4** Should we push annual plans harder?

The brief asks this README for three things: how to run the work end to end, what I'd do with more time, and the time spent.

## 1. How to run it end to end

Requirements: Python 3.9+ and two packages.

```bash
pip install duckdb openpyxl        # or: pip install -r requirements.txt
```

1. Put the four delivered CSVs in `data/` at the repository root:
   `data/users.csv`, `data/transactions_export_1.csv`, `data/transactions_export_2.csv`, `data/churn_labels.csv`.
2. From the repository root run:

```bash
python run_all.py
```

`run_all.py` runs every `sql/NN_*.sql` file in order into `tune.duckdb` (created next to it; about 1 GB, ~20 s),
then every `py/NN_*.py` file, which writes the Part 1a reports into `reports/` and runs 29 automated checks
(`py/02_checks.py`: keys, overlaps, revenue across layers and the headline numbers; any failure stops the run).
All paths are relative to the repository root. The raw CSVs and the database are not in the repository.

Optional:
- `python query.py` opens the database read-only and lets you type SQL (`tables` lists the tables).
- `python py/build_site_data.py` re-exports the tables to Parquet for the website (writes `site/data/` and
  `site/catalog.json`; on GitHub those site files sit at the repository root).

## 2. What I'd do with more time

- **Make the texts more concise:** I kept fuller explanations on purpose so that every step stays clear and easy to check, and with more time I would tighten them so each tab reads faster.
- **Check more cuts before proposing the annual-plan test** ([tab 5a](https://miushkaenavimia.github.io/tune-analysis-submission/#p5a)): I would split renewal and annual-plan take-up by age, channel, city and payment method, to confirm who should get the offer and that each group is large enough.
- **Answer Part 3b, free trials and price points:** question 3 is answered only in part, and the two free-trial waves are a natural experiment that could show whether trials add paying subscribers.
- **Close the data gaps:** April 2017 transactions and a full user export would settle the 10,740 users 1c cannot judge and describe the 109,330 users missing from `users.csv` (8.3% of revenue).
- **Forecast further ahead:** the cohort tables ([tab 2.3](https://miushkaenavimia.github.io/tune-analysis-submission/#p2-churn) and [tab 2.4](https://miushkaenavimia.github.io/tune-analysis-submission/#p2-arpu)) forecast only up to Sep 2017, while the value of an annual plan (5a) needs every start month filled up to M12.
- **Test more cautious scenarios for the three Part 4 moves:** each move rests on one assumption that is not measured, so lower values would show how much of the ~10,000 a year still holds.
- **Strengthen the data engineering:** more checks per table on top of the 29 that run after every build ([tab 1b.1](https://miushkaenavimia.github.io/tune-analysis-submission/#lineage)), and automated tests at each layer, so a broken file is caught before a wrong number reaches leadership.
- **Check that the model is efficient:** table sizes, views vs tables and query speed will matter once the data grows past these 5.7M rows.
- **Test the SQL explorer properly** on every table, large results, phones and slow browsers, as reviewers run their own queries on it.

## 3. Time spent

~5 hours

---

## Where each part of the brief lives

| Part | What | Site tab | Report |
|---|---|---|---|
| **Part 1 · Data engineering** | | | |
| 1a | Data quality: 21 issues, ranked by impact | [1a](https://miushkaenavimia.github.io/tune-analysis-submission/#dq) | `reports/01_data_quality.md` (also `.xlsx`, `.html`) |
| 1b | Clean layer: table map, cleaning rules (duplicates, overlapping transactions and early renewals, cancellations, implausible values), SQL on every table | [1b.1](https://miushkaenavimia.github.io/tune-analysis-submission/#lineage) · [1b.2](https://miushkaenavimia.github.io/tune-analysis-submission/#explorer) | `reports/02_data_model.md` |
| 1c | Billing's churn labels checked against the rule as written | [1c](https://miushkaenavimia.github.io/tune-analysis-submission/#churn) | `reports/03_churn_validation.md` |
| **Part 2 · Core metrics** | | | |
| 2 | Active, new, renewing, reactivated, churn, ARPU, discounts | [Part 2](https://miushkaenavimia.github.io/tune-analysis-submission/#p2-active) | `reports/04_metrics.md` |
| **Part 3 · Deep dive (one of two)** | | | |
| 3a | Churn drivers: what matters, what only looks like it | [Part 3](https://miushkaenavimia.github.io/tune-analysis-submission/#p3a) | `reports/05_deep_dive.md` |
| ~~3b~~ | ~~Free trials and price points~~ | not chosen | - |
| **Part 4 · Executive summary** | | | |
| 4 | Four answers and three recommendations | [Part 4](https://miushkaenavimia.github.io/tune-analysis-submission/#p4) | `reports/08_executive_summary.md` |
| **Part 5 · Experiment and AI** | | | |
| 5a | Annual-plan A/B test design | [5a](https://miushkaenavimia.github.io/tune-analysis-submission/#p5a) | `reports/06_ab_test.md` |
| 5b | How AI was used, and where it was wrong | [5b](https://miushkaenavimia.github.io/tune-analysis-submission/#p5b) | `reports/07_ai_log.md` |

## What gets built

| Script | Builds | One row is |
|---|---|---|
| `sql/00_load_raw.sql` | `raw_users`, `raw_transactions_export_1`, `raw_transactions_export_2`, `raw_churn_labels` | a row of the CSV, exactly as delivered (one table per file) |
| `sql/00_union_exports.sql` | `base_transactions` | a row of either export, values unchanged, plus `src_file` / `src_row` lineage |
| `sql/01_data_quality.sql` | `dq_summary`, `dq_examples_*`, `dq_export_profile`, `dq_t9_by_month`, `dq_exp_0331_by_tx` | one data-quality check / example row |
| `sql/02_stg_transactions.sql` | `ref_price_plan`, `stg_transactions` | a price point; a real billing event (deduplicated, conflicts resolved) |
| `sql/02_stg_users.sql` | `stg_users` | a row of users.csv, cleaned (age 4-92 else NULL, gender 'unknown', typed dates) |
| `sql/03_fct_subscription.sql` | `fct_subscription` | a subscription period (a purchase and the cancels that follow it) |
| `sql/04_dim_user.sql` | `dim_user` | a user seen anywhere (registry, transactions or labels) |
| `sql/05_fct_user_month.sql` | `fct_user_month` | a user in a calendar month with access, a payment or a churn |
| `sql/06_churn_validation.sql` | `churn_mar17`, `churn_confusion`, `churn_disagreement` | a user in the Mar 2017 churn cohort or labelled; one outcome × label cell; one disagreement group |
| `sql/07_fct_cohort.sql` | `fct_cohort` | a start-month cohort in one month since its start |
| `sql/08_metrics.sql` | `mart_metrics_month`, `mart_churn_windows` | a calendar month; a month × churn window |
| `sql/09_deep_dive.sql` | `mart_renewal_decisions`, `mart_churn_drivers`, `mart_churn_factor_summary`, `mart_churn_method_quarter`, `mart_churn_plan_monthly` | Part 3 churn-driver tables (30 days for all, side check) |
| `sql/10_churn_by_type.sql` | `mart_churn_by_type`, `mart_churn_mixed_window`, `mart_return_curve` | a month × subscriber type × churn rule; one subscriber type |
| `sql/11_p2_splits.sql`, `sql/12_more_splits.sql` | `mart_p2_splits`, `mart_more_splits` | a split × month × segment |
| `sql/13_churn_rule_3_30.sql` | the Part 3 tables with suffix `_3d` | Part 3 on the main rule (3 days Auto-renew, 30 days Manual) |
| `py/01_dq_outputs.py` | `reports/01_data_quality.{md,xlsx,html}`, `reports/01_dq_*.csv` | Part 1a report, generated from `dq_summary` |
| `py/02_checks.py` | printed PASS / FAIL list | 29 automated checks after every build: rules that must hold on any data, plus the headline numbers pinned |

Each SQL file starts with a header that states its input, output, grain and the rules it applies.

## Key assumptions, applied the same way everywhere

- **`expires_at` is the last day of access.** A plan with `expires_at` 01/03/17 still gives access on 1 March 2017, so the user counts as active in Mar 2017 and stays in the 1c March cohort, and a purchase on the day after expiry is an on-time renewal. In `fct_subscription`, `covered_end` = expiry + 1 day, and `gap_days` = 1 means no day without access.
- **Churn outcomes not yet known are left out, and counted.** An outcome is known only when its churn window ends by 31/03/17, the last day in the files, so the cut follows each window: Auto-renew plans (3 days) up to an expiry of 28/03/17, Manual plans (30 days) up to 01/03/17. Left out: 10,740 users in 1c, 10,169 paying subscribers whose plan ended in Mar 2017 in Part 2 (2.3 and 2.5; 14,178 with 30 days for all), and 58,877 paid renewals due in Mar 2017 in Part 3 (243,130 with 30 days for all).
- **Renewing and then cancelling counts as retained**, as the brief's churn rule says.

## Repository layout

```
README.md, requirements.txt, run_all.py, query.py
sql/        numbered build scripts (run in order)
py/         Python steps (report generator, site export, nodot.py = site text style helper)
reports/    deliverables
index.html, dq.html, catalog.json, tune_logo.png, .nojekyll, data/raw, data/clean
            the static website served by GitHub Pages; data/raw and data/clean hold Parquet exports
            of the built tables for the site, not the raw CSVs
```
