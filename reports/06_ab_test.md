# 5a · Annual-plan promotion test

Interactive version with charts: https://miushkaenavimia.github.io/tune-analysis-submission/#p5a

**Question from Growth:** should we offer 30-day subscribers a discounted annual plan when their subscription comes up for renewal?

**Bottom line:** one month of renewals is enough for Manual users and one or two for Auto-renew users (about 66,700 users per group per month; Auto-renew users on $99 or $129 are left out, since they already pay for almost the whole year). The annual cash comes in on day 1, so the first months will always look good. It is tracked weekly from week 1, decide on a tested 12-month forecast at month 2 for Manual users and month 3 for Auto-renew users, confirm with real cash at month 12, and see at month 13 whether annual buyers renew. Auto-renew users already pay almost every month, so they get a smaller discount (11 months' price) than Manual users (10 months' price), and each payment type is decided on its own.

## 1. Hypothesis

Offering an annual plan at renewal, "12 months for the price of 10" for Manual users and "12 months for the price of 11" for Auto-renew users, raises **12-month net revenue per subscriber** among Manual users, half of whom are gone within a year, and raises it a little, or at least does not lower it, among Auto-renew users, who already stay.

The break-even is simple. In the next 12 months, Manual users pay on average for 7.3 months at their own monthly price, so an annual plan at 10 months' price brings about $396 more per taker. Auto-renew users already pay for 10.4 months, so at 10 months' price each Auto-renew taker would pay about $33 less than today; at 11 months' price they pay about $99 more. Split by monthly price, Auto-renew users on $99 or $129 already pay for about 11.5 months, so even 11 × loses revenue on them (−$61 and −$103 per taker); they are left out, and Auto-renew users on $149 gain about $121 per taker (payment method 39 left out, see section 2). Real takers are more loyal than average, so the true gain per taker is lower than these averages; that is why the test measures it rather than assumes it.

**Decision rule**

| Result | Decision |
|:--|:--|
| 12-month net revenue per assigned user up, 97.5% interval above zero (stricter than 95%, because Auto-renew and Manual are two separate reads), renewal at the offer at or above 93.9% for all eligible users and 80.0% for Manual users | Ship, for that payment type only |
| Revenue flat or down, or renewal below 93.9% for all eligible users or 80.0% for Manual users | Don't ship, even if take-up looks high |
| Up for Manual, flat or down for Auto-renew | Offer the annual plan to Manual users only |

## 2. Baselines from the data

All numbers come from `fct_subscription` (clean layer, Part 1b). "Eligible" = a paid 30-day period (30 or 31 days, not free) reaching its expiry date.

| Baseline | All | Auto-renew | Manual |
|:--|:--:|:--:|:--:|
| Eligible subscribers per month (Oct 2016 – Jan 2017) | 233,800 | 210,300 (89.9%) | 23,500 (10.1%) |
| Renew in time (same months): within 3 days for Auto-renew, 30 days for Manual (the site's churn rule) | 95.9% | 97.5% | 82.0% |
| Switch to an annual plan today, with no offer (same months) | 0.13% | 0.07% | 0.7% |
| 12-month revenue per subscriber (Q1 2016 group, 225,158 users) | $1,318 | $1,361 | $1,097 |
| Standard deviation of that revenue | $607 | $562 | $762 |
| Still paying 12 months later | 74.9% | 79.9% | 49.3% |
| Months paid in the next 12, at their own monthly price | 9.9 | 10.4 | 7.3 |
| Revenue gained per taker of an annual plan at 10 × their monthly price | +$36 | −$33 | +$396 |
| Revenue gained per taker at the offered price (11 × Auto-renew, 10 × Manual) | - | +$99 | +$396 |

Other facts that shape the design:

- **Annual plans renew at 69.0%** at the end of the plan (20,981 annual periods ending Jan 2016 – Jan 2017). That is the only prior for "annual retention".
- **Prices differ:** in January 2017, 46.9% of 30-day subscribers paid $149 and 39.4% paid $99. Today's annual list price ($1,788 for 410 days) is a deal for a $149 payer but costs 50% more than 12 months at $99. So the offer must be priced **from each user's own monthly price**, not from the list price.
- Only **0.3%** of annual purchases since 2016 were cancelled (baseline for the refund guardrail).

**What the offer means per group** (users whose first renewal fell in Jan – Mar 2016, groups above 10,000 users; revenue per user over the next 12 months):

| Group | Paid today in a year (average) | Full-year price, if they stay 12 months | Annual offer | User saves | Tune gains per buyer |
|:--|:--:|:--:|:--:|:--:|:--:|
| Manual, $149 (25,110) | $1,050 | $1,788 | $1,490 (10 ×) | $298 | +$440 |
| Manual, $150 (11,457) | $1,200 | $1,800 | $1,500 (10 ×) | $300 | +$300 |
| Auto-renew, $149 (98,542, without payment method 39) | $1,518 | $1,788 | $1,639 (11 ×) | $149 | +$121 |
| ~~Auto-renew, $129 (13,889)~~ | $1,522 | $1,548 | $1,419 (11 ×) | $129 | −$103 |
| ~~Auto-renew, $99 (54,322)~~ | $1,150 | $1,188 | $1,089 (11 ×) | $99 | −$61 |

The crossed-out groups pay about 11.5 times a year already (also in Jul – Sep 2015), so they are left out of the test. Auto-renew users on payment method 39 are left out of these revenue baselines: their charges failed in early 2016 (Billing gap), which made $149 Auto-renew users look like they pay for only 9.5 months (10.2 without them). **Eligible baselines after that cut:** 133,400 users reach renewal per month (Manual 23,500, Auto-renew on $149 or other prices 109,900); renewal in time 94.4% (Auto-renew 97.1%, Manual 82.0%); annual take-up today 0.23% (Auto-renew 0.12%); 12-month revenue $1,418 (SD $710), Auto-renew $1,534 (SD $652, 10.4 of 12 months paid, +$97 per taker at 11 ×).

## 3. Design

| Item | Choice | Why |
|:--|:--|:--|
| Unit | **User** (`user_id`), assigned once and kept for the whole test | A user renews every month; assigning each renewal would mix both offers for one person. |
| Eligible | Paid 30-day subscriber, 7 days before expiry, no future period already bought, not on a free trial; **Auto-renew users on $99 or $129 a month are left out** | These are the people Growth wants to reach, at the moment they decide. Auto-renew users on $99 / $129 already pay for about 11.5 of the next 12 months, so any annual discount would lower revenue (see the table below). |
| Split | 50 / 50, balanced within Auto-renew vs Manual and within price ($99 / $149 / other) | The two payer types behave very differently; each needs a fair comparison. |
| Check the split | Before reading any result: group sizes close to 50 / 50, and groups alike on age band, gender, city, acquisition channel, payment type, plan price, tenure and past renewals | If they differ, the assignment is broken and any result is untrustworthy. |
| Control | Normal renewal | |
| Treatment | Annual plan priced from their current monthly price: 10 × for Manual users (about 17% off), 11 × for Auto-renew users on $149 (about 8% off) | One clear offer per payment type. Auto-renew users already pay for 10.4 of 12 months, so 10 × would give them money away. |
| Exposure | The offer is shown once, at the user's first renewal in the test | Repeat views would wear the offer out and blur the novelty check. |
| Read by | Auto-renew vs Manual, and first renewal vs later | These are the two strongest churn drivers (Part 3), and the offer should work very differently in each. |

## 4. Metrics

**Primary: 12-month net revenue per assigned user.** Everyone assigned counts, whether they took the offer or not. This is the only fair way to compare: the people who take an annual plan are the most loyal, so comparing takers with non-takers would flatter the offer.

**Secondary:** annual take-up (today 0.23% among eligible users); paid days in the next 12 months.

**Guardrails (stop or rethink if they move the wrong way):**

| Guardrail | Baseline | What it protects |
|:--|:--:|:--|
| Renewal at the offer moment, any plan | 94.4% (Manual: 82.0%) | The offer must not confuse or push people away. |
| 12-month revenue of Auto-renew users on $149 | $1,534 | They already pay for 10.4 of 12 months, so a bigger discount than 11 × would give money away. |
| Annual plans cancelled or refunded within 30 days | 0.3% | Regret buys. |

## 5. Sample size

Two-sided test, 5% false-alarm rate, 80% power, revenue standard deviations from section 2.

**Users needed per group** to detect a change in 12-month revenue of:

| Group | 1% | 2% | 3% | 5% |
|:--|:--:|:--:|:--:|:--:|
| All eligible | 39,277 | 9,819 | 4,364 | 1,571 |
| Auto-renew on $149 | 28,318 | 7,079 | 3,146 | 1,133 |
| Manual | 75,641 | 18,910 | 8,405 | 3,026 |

**What one month gives (50 / 50):** about 66,700 users per group, of whom 11,800 are Manual and 55,000 Auto-renew.

- All eligible users: detects a change of **0.8%** (about $11 per user).
- Auto-renew on $149: **0.8%** (about $12 per user).
- Manual: **2.8%** (about $31 per user). This is the group that decides the test, and it sets the enrolment length.

**Is the bar reachable?** Each Manual taker adds about $396, so a take-up of about 8% among Manual users already clears the $31-per-user bar. Each eligible Auto-renew taker adds about $97 on average, so one month clears their $12-per-user bar (0.8%) only at about 13% take-up; at 9%, Auto-renew enrolment runs a second month (bar about $8.6), which moves the Auto-renew decision from month 3 to month 4. Leaving out Auto-renew users on $99 / $129 halves the Auto-renew group (105,100 → 55,000 per group), which is the cost of this cut. Today only 0.7% of Manual users and 0.12% of eligible Auto-renew users switch to annual with no offer.

Renewal guardrail: to see a drop from 94.4% to 93.9% needs 34,319 users per group; from 82.0% to 80.0% (Manual) needs 7,295 (z = 2.24). Both fit easily.

Formula: users per group = 2 × (z + 0.84)² × SD² / (smallest change)². z = 2.24 for each payment type (2.5% false alarms each, so 5% across the two reads, Bonferroni) and 1.96 for all users.

## 6. Duration, and the "cash now, retention later" problem

An annual plan pays up front. In month 1 the treatment group will show a big revenue jump that means nothing yet. Monthly payers pay as they go, and annual buyers can't churn for a year.

| When | What is read | Decision |
|:--|:--|:--|
| Week 1, then weekly | Per payment type: take-up, renewal at the offer, refunds, cash so far | Stop early only for harm, at a strict 99% bound. Never stop early for a win, because upfront cash always looks like one |
| Month 1 | Enrol: every 30-day subscriber passes renewal once. Take-up by enrolment week, to spot a novelty effect | - |
| Month 2 | **12-month forecast, Manual:** every Manual user is 30 days past the offer | Go / no-go for Manual |
| Month 3 (4 if a second enrolment month is needed) | **12-month forecast, Auto-renew:** every user is 60 days past the offer (many failed Auto-renew charges are paid later, so day 30 is too early) | Go / no-go for Auto-renew |
| Months 4–11, monthly | **Forecast check:** the forecast also says how much each group should have paid by this month; compare it with the real cash, per payment type | If the real gap between the groups drifts away from the forecast gap, reopen the decision |
| Month 12 | **Final primary read:** actual 12-month cash for both groups | Confirm or reverse |
| Month 13–14 | Do annual buyers renew? Compare with 69.0% today | Is the annual plan good for the long run? |

**The 12-month forecast** = cash paid so far + what past users in the same situation paid in the rest of the year. "Same situation" = payment type, price ($99 / $149 / other), tenure, still paying or not on that day, on an annual plan or not, renewals so far. An annual buyer's payment is their known year, so upfront cash no longer looks like a fake win.

Tested on the 225,158 users of section 2 (first renewal Jan – Mar 2016): the rules were learned on a random half and checked on the other half, against what each user really paid in the next 12 months.

| Group (test half) | Real 12-month revenue | Forecast at day 30 | Forecast at day 60 |
|:--|:--:|:--:|:--:|
| Manual, bought again within 30 days | $1,337 | $1,332 | $1,334 |
| Manual, did not buy again | $397 | $403 | $406 |
| Manual, switched to annual by day 30 (280 users) | $1,809 | $1,835 | $1,823 |
| Auto-renew, charged on time (3 days) | $1,448 | $1,405 | $1,447 |
| Auto-renew, not charged on time | $839 | $1,102 | $835 |

Share of the differences between single users that the forecast explains (Auto-renew / Manual): day 0 (payment type, price, tenure only) 8% / 4%, day 7 39% / 26%, day 30 42% / 32%, day 60 67% / 48%, day 90 72% / 59%. The strongest signal is whether the user is still paying on that day, then the cash paid so far. Forecasts for one start month at a time (learned on the other two) were off by up to about 6% at day 60; an error like that hits both groups alike, so it mostly cancels in the difference.

**69.0% is only a prior.** It comes from people who chose an annual plan on their own, without a discount, and all of them pay Manual. In Jan 2015 – Oct 2015, Auto-renew monthly subscribers who paid with a discount were more often still paying a year later than those who paid full price (80%–87% vs 71%–78%), but an annual offer is a different discount, so the year-2 forecast is also checked at a lower rate before a full rollout.

Keep 10% of eligible users in a holdout with no annual offer until month 14, even if the offer rolls out at month 3 or 4.

## 7. Analysis SQL

Runs on the clean layer plus a hypothetical `experiment_assignments(user_id, variant, assigned_at)` table. It returns, per payment type, take-up, renewal under the site's churn rule (3 days Auto-renew, 30 days Manual), the gap in the 12-month revenue forecast (read at day 30 for Manual and day 60 for Auto-renew, the go / no-go in section 6) and the real 12-month cash gap (the month-12 check), each with its 97.5% interval. The forecast learns from past users whose first renewal fell in Jan – Mar 2016, as in section 6. Tested on a fake 50 / 50 split of Nov 2016 renewals with no offer: it found no difference, as it should (Manual forecast gap −$2 against a 97.5% interval of ±$14, Auto-renew +$0.8 against ±$3.8).

```sql
-- 5a analysis: 12-month revenue forecast per assigned user, read at day 30 (Manual) and day 60 (Auto-renew)
-- forecast = cash paid so far + monthly price x (rest-of-year cash / monthly price) of past users in the same situation
with past0 as (                                    -- past users: first paid 30-day period expiring Jan - Mar 2016
  select user_id, subscription_id, start_date, end_date as d0, is_auto_renew, amount_paid as price, period_no,
         case when is_auto_renew = 1 then 60 else 30 end as k,
         row_number() over (partition by user_id order by end_date, subscription_id) as rn
  from fct_subscription
  where plan_days in (30, 31) and is_free = 0 and amount_paid > 0
    and end_date between date '2016-01-01' and date '2016-03-31'
    and not (is_auto_renew = 1 and amount_paid in (99, 129))   -- same eligibility as the test
), past as (                                       -- what each past user did after that period, at day k and by day 365
  select p.user_id, p.is_auto_renew, p.price, p.period_no, p.k,
    coalesce(sum(s.amount_paid), 0)                                                            as cash_12m,
    coalesce(sum(s.amount_paid) filter (where s.start_date <= p.d0 + p.k), 0)                  as cash_k,
    coalesce(max((s.start_date <= p.d0 + p.k and s.end_date >= p.d0 + p.k and s.amount_paid > 0)::int), 0) as paying_k,
    coalesce(max((s.start_date <= p.d0 + p.k and s.plan_days >= 360 and s.amount_paid > 0)::int), 0)       as annual_k,
    least(count(*) filter (where s.start_date <= p.d0 + p.k and s.amount_paid > 0), 3)         as renewals_k
  from past0 p
  left join fct_subscription s
    on s.user_id = p.user_id and s.start_date > p.start_date and s.start_date <= p.d0 + 365
   and s.subscription_id <> p.subscription_id
  where p.rn = 1
  group by all
), a0 as (                                         -- test users: the paid 30-day period they were offered at (next expiry)
  select e.user_id, e.variant,
         arg_min(s.subscription_id, s.end_date) as sub_id, arg_min(s.start_date, s.end_date) as start0, min(s.end_date) as d0,
         arg_min(s.is_auto_renew, s.end_date) as is_auto_renew, arg_min(s.amount_paid, s.end_date) as price,
         arg_min(s.period_no, s.end_date) as period_no
  from experiment_assignments e
  join fct_subscription s
    on s.user_id = e.user_id and e.assigned_at::date between s.start_date and s.end_date
   and s.plan_days in (30, 31) and s.is_free = 0 and s.amount_paid > 0
  group by all
), a as (
  select *, case when is_auto_renew = 1 then 60 else 30 end as k from a0
  where not (is_auto_renew = 1 and price in (99, 129))         -- eligibility: Auto-renew users on $99 / $129 are left out
), u as (                                          -- the same facts for each test user; everyone assigned counts, takers or not
  select a.user_id, a.variant, a.is_auto_renew, a.price, a.period_no, a.k,
    coalesce(max((s.plan_days >= 360 and s.start_date <= a.d0 + 30)::int), 0)                  as took_annual,
    coalesce(max((s.is_free = 0 and s.start_date <= a.d0
         + case when a.is_auto_renew = 1 then 3 else 30 end)::int), 0)                          as renewed,      -- churn rule: 3 days Auto-renew, 30 days Manual
    coalesce(sum(s.amount_paid) filter (where s.start_date <= a.d0 + 365), 0)                 as cash_12m,     -- month 12 read
    coalesce(sum(s.amount_paid) filter (where s.start_date <= a.d0 + a.k), 0)                 as cash_k,
    coalesce(max((s.start_date <= a.d0 + a.k and s.end_date >= a.d0 + a.k and s.amount_paid > 0)::int), 0) as paying_k,
    coalesce(max((s.start_date <= a.d0 + a.k and s.plan_days >= 360 and s.amount_paid > 0)::int), 0)       as annual_k,
    least(count(*) filter (where s.start_date <= a.d0 + a.k and s.amount_paid > 0), 3)         as renewals_k
  from a
  left join fct_subscription s
    on s.user_id = a.user_id and s.start_date > a.start0 and s.subscription_id <> a.sub_id
  group by all
), cells as (                                      -- same situation = payment type, price band, tenure band, paying, annual, renewals on day k
  select *,
    case when price between 95 and 105 then '99' when price between 140 and 155 then '149' else 'other' end as price_band,
    case when period_no <= 1 then '1' when period_no <= 3 then '2-3' when period_no <= 12 then '4-12' else '13+' end as tenure_band
  from (select 'past' as src, user_id, null as variant, is_auto_renew, price, period_no, cash_12m, cash_k, paying_k, annual_k, renewals_k,
               null::int as took_annual, null::int as renewed from past
        union all
        select 'test', user_id, variant, is_auto_renew, price, period_no, cash_12m, cash_k, paying_k, annual_k, renewals_k,
               took_annual, renewed from u)
), rate as (                                       -- rest-of-year cash, in months of the user's own price
  select is_auto_renew, price_band, tenure_band, paying_k, annual_k, renewals_k,
         sum(cash_12m - cash_k) / sum(price) as rest_months
  from cells where src = 'past' group by all
), f as (
  select c.*, c.cash_k + c.price * coalesce(r.rest_months, g.rest_months) as forecast_12m
  from cells c
  left join rate r using (is_auto_renew, price_band, tenure_band, paying_k, annual_k, renewals_k)
  cross join (select sum(cash_12m - cash_k) / sum(price) as rest_months from cells where src = 'past') g
  where c.src = 'test'
), grp as (
  select is_auto_renew, variant, count(*) n, avg(took_annual) take_up, avg(renewed) renewal,
         avg(forecast_12m) fc, var_samp(forecast_12m) fc_v, avg(cash_12m) cash, var_samp(cash_12m) cash_v
  from f group by all
)
select t.is_auto_renew, t.n n_treat, c.n n_ctrl, t.take_up, c.renewal ctrl_renewal, t.renewal treat_renewal,
       t.fc - c.fc                                    as forecast_diff,          -- go / no-go: day 30 Manual, day 60 Auto-renew
       2.24 * sqrt(t.fc_v / t.n + c.fc_v / c.n)       as forecast_ci975_half,    -- ship only if forecast_diff > this
       t.cash - c.cash                                as cash_12m_diff,          -- month 12: confirm on real cash
       2.24 * sqrt(t.cash_v / t.n + c.cash_v / c.n)   as cash_ci975_half
from grp t join grp c on c.is_auto_renew = t.is_auto_renew and t.variant = 'treatment' and c.variant = 'control'
order by 1;
```

Baselines above come from these queries (DuckDB, `tune.duckdb`):

```sql
-- Monthly flow, renewal in time (3 days Auto-renew, 30 days Manual), switch to annual (paid 30-day periods by expiry month)
with s as (
  select *, lead(start_date) over w nxt_start, lead(plan_days) over w nxt_days
  from fct_subscription window w as (partition by user_id order by start_date, period_no)
)
select date_trunc('month', end_date) m, count(distinct user_id) users,
  avg(coalesce(nxt_start <= end_date + case when is_auto_renew = 1 then 3 else 30 end, false)::int) renew,
  avg(coalesce(nxt_start <= end_date + 30 and nxt_days >= 360, false)::int) to_annual
from s where plan_days in (30, 31) and is_free = 0 and amount_paid > 0
  and end_date between date '2016-01-01' and date '2017-01-31'
group by 1 order by 1;

-- 12-month revenue per subscriber (first eligible expiry in Q1 2016)
with e as (
  select user_id, subscription_id, start_date, end_date, is_auto_renew,
    row_number() over (partition by user_id order by end_date, subscription_id) rn
  from fct_subscription where plan_days in (30, 31) and is_free = 0 and amount_paid > 0
    and end_date between date '2016-01-01' and date '2016-03-31'
)
select e.is_auto_renew, count(distinct e.user_id), avg(rev), stddev(rev) from (
  select e.user_id, e.is_auto_renew, coalesce(sum(s.amount_paid), 0) rev
  from e left join fct_subscription s on s.user_id = e.user_id and s.start_date > e.start_date
    and s.start_date <= e.end_date + 365 and s.subscription_id <> e.subscription_id
  where e.rn = 1 group by all) e
group by rollup(1);
```

## 8. Limits

- Revenue baselines come from 2016; prices and the payer mix may have moved since.
- The data has no app usage, so it can't tell whether annual buyers stay because they learn more or just because they prepaid.
- The 69.0% annual renewal comes from people who chose annual on their own. An annual offer is a different discount from the 2015 monthly one, so its buyers may still renew less.
