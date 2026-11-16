"""02_checks.py - automated checks that run at the end of every build (called by run_all.py).

Two kinds of checks, all read-only against tune.duckdb:
  1. Rules that must hold on any copy of the data: unique keys, no overlapping access periods,
     revenue that reconciles across layers, every user present in dim_user, groups that add up.
  2. The headline numbers the site and the reports quote, pinned to the delivered files.
     If a script change moves one of them, the build stops here instead of a wrong number reaching leadership.
Each check prints PASS or FAIL; any FAIL ends the run with an error.
Run via run_all.py, or directly: python py/02_checks.py
"""
import pathlib
import sys
import duckdb

ROOT = pathlib.Path(__file__).resolve().parents[1]
con = duckdb.connect(str(ROOT / "tune.duckdb"), read_only=True)
one = lambda sql: con.sql(sql).fetchone()[0]

# (name, SQL returning one value, expected value)
RULES = [
    ("base = export_1 + export_2 rows",
     "SELECT (SELECT count(*) FROM base_transactions) - (SELECT count(*) FROM raw_transactions_export_1)"
     " - (SELECT count(*) FROM raw_transactions_export_2)", 0),
    ("stg: event_id unique",
     "SELECT count(*) - count(DISTINCT event_id) FROM stg_transactions", 0),
    ("stg: (user_id, event_seq) unique",
     "SELECT count(*) - count(DISTINCT (user_id, event_seq)) FROM stg_transactions", 0),
    ("stg: no non-cancel expiry before purchase",
     "SELECT count(*) FROM stg_transactions WHERE is_cancel = 0 AND expires_date < transacted_date", 0),
    ("fct_subscription: one period per purchase",
     "SELECT (SELECT count(*) FROM fct_subscription) - (SELECT sum(is_purchase) FROM stg_transactions)", 0),
    ("fct_subscription: subscription_id unique",
     "SELECT count(*) - count(DISTINCT subscription_id) FROM fct_subscription", 0),
    ("fct_subscription: (user_id, period_no) unique",
     "SELECT count(*) - count(DISTINCT (user_id, period_no)) FROM fct_subscription", 0),
    ("fct_subscription: end never before start",
     "SELECT count(*) FROM fct_subscription WHERE end_date < start_date OR covered_end < covered_start", 0),
    ("fct_subscription: access periods never overlap within a user",
     "SELECT count(*) FROM (SELECT covered_start, lag(covered_end) OVER (PARTITION BY user_id ORDER BY period_no) AS prev_end"
     " FROM fct_subscription) WHERE covered_start < prev_end", 0),
    ("revenue: fct_subscription = stg purchases",
     "SELECT sum(amount_paid) - (SELECT sum(amount_paid) FROM stg_transactions WHERE is_purchase = 1) FROM fct_subscription", 0),
    ("revenue: fct_user_month = fct_subscription",
     "SELECT sum(amount_paid) - (SELECT sum(amount_paid) FROM fct_subscription) FROM fct_user_month", 0),
    ("dim_user: user_id unique",
     "SELECT count(*) - count(DISTINCT user_id) FROM dim_user", 0),
    ("dim_user: covers every registry, transaction and label user",
     "SELECT count(*) FROM (SELECT user_id FROM raw_users UNION SELECT user_id FROM stg_transactions"
     " UNION SELECT user_id FROM raw_churn_labels) a ANTI JOIN dim_user USING (user_id)", 0),
    ("fct_user_month: (user_id, month) unique",
     "SELECT count(*) - count(DISTINCT (user_id, month)) FROM fct_user_month", 0),
    ("fct_user_month: 27 months, Jan 2015 to Mar 2017",
     "SELECT count(DISTINCT month) FROM fct_user_month", 27),
    ("fct_user_month: active days never above 31",
     "SELECT count(*) FROM fct_user_month WHERE active_days > 31", 0),
    ("2.2: New + Renewing + Reactivated = paying, every month",
     "SELECT count(*) FROM mart_metrics_month WHERE paying_subscribers <> new_paid + renewing_paid + reactivated_paid", 0),
    ("fct_cohort: retention between 0% and 100%",
     "SELECT count(*) FROM fct_cohort WHERE retention_pct < 0 OR retention_pct > 100", 0),
    ("fct_cohort: cumulative ARPU never falls",
     "SELECT count(*) FROM (SELECT cum_arpu, lag(cum_arpu) OVER (PARTITION BY cohort_month ORDER BY months_since_start) AS prev"
     " FROM fct_cohort) WHERE cum_arpu < prev - 1e-9", 0),
    ("1c: every label in churn_labels.csv is in the matrix",
     "SELECT (SELECT sum(label_retained + label_churned) FROM churn_confusion) - (SELECT count(*) FROM raw_churn_labels)", 0),
]

# Numbers quoted on the site and in the reports, for the delivered files
PINNED = [
    ("rows in stg_transactions", "SELECT count(*) FROM stg_transactions", 5_725_763),
    ("rows in fct_subscription", "SELECT count(*) FROM fct_subscription", 5_501_434),
    ("rows in dim_user", "SELECT count(*) FROM dim_user", 1_800_905),
    ("rows in fct_user_month", "SELECT count(*) FROM fct_user_month", 6_637_518),
    ("users missing from users.csv", "SELECT count(*) FROM dim_user WHERE NOT is_in_users", 109_330),
    ("paying subscribers, Mar 2017", "SELECT paying_subscribers FROM mart_metrics_month WHERE month = DATE '2017-03-01'", 303_374),
    ("1c: users where the rule and the labels agree",
     "SELECT sum(CASE our_outcome WHEN 'retained' THEN label_retained WHEN 'churned' THEN label_churned END) FROM churn_confusion", 197_972),
    ("1c: users judged by both",
     "SELECT sum(label_retained + label_churned) FROM churn_confusion WHERE our_outcome IN ('retained', 'churned')", 205_213),
    ("1c: users that cannot be judged (no April data)",
     "SELECT total FROM churn_confusion WHERE our_outcome = 'unknown'", 10_740),
]

failed = 0
for group, checks in (("Rules", RULES), ("Pinned numbers", PINNED)):
    print(f"\n{group}")
    for name, sql, expected in checks:
        got = one(sql)
        ok = got == expected
        failed += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {got:,}" + ("" if ok else f" (expected {expected:,})"))
con.close()

total = len(RULES) + len(PINNED)
print(f"\n{total - failed} of {total} checks pass")
if failed:
    sys.exit(f"{failed} check(s) failed: fix the build before using any number")
