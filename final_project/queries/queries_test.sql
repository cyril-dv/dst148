--------------------------------------------------
-- TEST
--------------------------------------------------

with id_list as (
    select 
        sk_id_curr 
    from application_test
),
app_test as (
    select
        *
    from application_test
),
cb_active_loans as (
    select 
        sk_id_curr,
        max(case when credit_type = 'Mortgage' then 1 else 0 end) as CB_HAS_MORTAGE,
        max(case when credit_type = 'Car loan' then 1 else 0 end) as CB_HAS_CARLOAN,
        sum(case when credit_type = 'Credit card' then 1 else 0 end) as CB_HAS_CC,
        sum(case when credit_type = 'Consumer credit' then 1 else 0 end) as CB_ACT_LOANS_CNT,
        avg(case when credit_type = 'Consumer credit' then amt_credit_sum else null end) as CB_ACT_LOANS_AVG,
        sum(case when credit_type = 'Consumer credit' then amt_credit_sum else null end) as CB_ACT_LOANS_SUM
    from bureau
    where 1=1
        and credit_active = 'Active'
    group by 
        sk_id_curr
),
cb_past_loans as (
    select
        sk_id_curr,
        sum(case when credit_type = 'Consumer credit' then 1 else 0 end) as CB_PST_LOANS_CNT,
        avg(case when credit_type = 'Consumer credit' then amt_credit_sum else null end) as CB_PST_LOANS_AVG,
        sum(case when credit_type = 'Consumer credit' then amt_credit_sum else null end) as CB_PST_LOANS_SUM
    from bureau
    where 1=1
        and credit_active = 'Closed'
        and days_credit >= -365*5
    group by 
        sk_id_curr
),
cb_payments_first as (
    select
        sk_id_curr,
        avg(cb_dpd_first_cnt) as CB_DPD_FIRST_CNT,
        avg(cb_dpd_first_sum) as CB_DPD_FIRST_SUM
    from (
        select 
            sk_id_curr,
            sk_id_bureau,
            sum(case when status in ('1', '2', '3', '4', '5') then 1 else 0 end) as CB_DPD_FIRST_CNT,
            sum(case when status in ('1', '2', '3', '4', '5') then status::int else 0 end) as CB_DPD_FIRST_SUM
        from (
            select 
                b.sk_id_curr,
                bb.sk_id_bureau,
                bb.status,
                bb.months_balance,
                row_number() over (partition by bb.sk_id_bureau order by bb.months_balance asc) as cnt
            from bureau_balance as bb
            join bureau as b on bb.sk_id_bureau = b.sk_id_bureau
            where 1=1
                and b.days_credit >= -365*5
            ) as q1
        where cnt <= 12
        group by
            sk_id_curr,
            sk_id_bureau
    ) as q2
    group by
        sk_id_curr
),
cb_payments_last as (
    select
        sk_id_curr,
        avg(cb_dpd_last_cnt) as CB_DPD_LAST_CNT,
        avg(cb_dpd_last_sum) as CB_DPD_LAST_SUM
    from (
        select 
            sk_id_curr,
            sk_id_bureau,
            sum(case when status in ('1', '2', '3', '4', '5') then 1 else 0 end) as CB_DPD_LAST_CNT,
            sum(case when status in ('1', '2', '3', '4', '5') then status::int else 0 end) as CB_DPD_LAST_SUM
        from (
            select 
                b.sk_id_curr,
                bb.sk_id_bureau,
                bb.status,
                bb.months_balance,
                row_number() over (partition by bb.sk_id_bureau order by bb.months_balance desc) as cnt
            from bureau_balance as bb
            join bureau as b on bb.sk_id_bureau = b.sk_id_bureau
            where 1=1
                and b.days_credit >= -365*5
            ) as q1
        where cnt <= 13
        group by
            sk_id_curr,
            sk_id_bureau
    ) as q2
    group by
        sk_id_curr
),
pa_all_loans as (
    select
        sk_id_curr,
        coalesce(pa_loans_app_cnt / (pa_loans_app_cnt + pa_loans_ref_cnt + pa_loans_unu_cnt), 0) as pa_loans_app_pct,
        coalesce(pa_loans_ref_cnt / (pa_loans_app_cnt + pa_loans_ref_cnt + pa_loans_unu_cnt), 0) as pa_loans_ref_pct,
        coalesce(pa_loans_unu_cnt / (pa_loans_app_cnt + pa_loans_ref_cnt + pa_loans_unu_cnt), 0) as pa_loans_unu_pct,
        coalesce(pa_loans_app_avg, 0) as pa_loans_app_avg,
        coalesce(pa_loans_ref_avg, 0) as pa_loans_ref_avg,
        coalesce(pa_loans_unu_avg, 0) as pa_loans_unu_avg,
        coalesce(pa_loans_app_sum, 0) as pa_loans_app_sum,
        coalesce(pa_loans_ref_sum, 0) as pa_loans_ref_sum,
        coalesce(pa_loans_unu_sum, 0) as pa_loans_unu_sum,
        coalesce(pa_days_decision_max, 0) as pa_days_decision_max,
        coalesce(pa_insured_avg / pa_loans_app_cnt, 0) as pa_insured_avg,
        coalesce(pa_loans_term_avg, 0) as pa_loans_term_avg,
        coalesce(pa_loans_term_max, 0) as pa_loans_term_max,
        coalesce(pa_pct_risk_avg, 0) as pa_pct_risk_avg
    from (
        select
            sk_id_curr,
            sum(case when name_contract_status = 'Approved' then 1 else 0 end) as PA_LOANS_APP_CNT,
            sum(case when name_contract_status = 'Refused' then 1 else 0 end) as PA_LOANS_REF_CNT,
            sum(case when name_contract_status = 'Unused offer' then 1 else 0 end) as PA_LOANS_UNU_CNT,
            avg(case when name_contract_status = 'Approved' then amt_credit else null end) as PA_LOANS_APP_AVG,
            avg(case when name_contract_status = 'Refused' then amt_credit else null end) as PA_LOANS_REF_AVG,
            avg(case when name_contract_status = 'Unused offer' then amt_credit else null end) as PA_LOANS_UNU_AVG,
            sum(case when name_contract_status = 'Approved' then amt_credit else null end) as PA_LOANS_APP_SUM,
            sum(case when name_contract_status = 'Refused' then amt_credit else null end) as PA_LOANS_REF_SUM,
            sum(case when name_contract_status = 'Unused offer' then amt_credit else null end) as PA_LOANS_UNU_SUM,
            max(days_decision) as PA_DAYS_DECISION_MAX,
            sum(case when name_contract_status = 'Approved' and nflag_insured_on_approval = 1 then 1. else 0 end) as PA_INSURED_AVG,
            avg(case when name_contract_status = 'Approved' and name_contract_type <> 'Revolving loans' then cnt_payment else null end) as PA_LOANS_TERM_AVG,
            max(case when name_contract_status = 'Approved' and name_contract_type <> 'Revolving loans' then cnt_payment else null end) as PA_LOANS_TERM_MAX,
            avg(case when name_yield_group = 'XNA' then null
                    when name_yield_group = 'low_action' then 1
                    when name_yield_group = 'low_normal' then 2
                    when name_yield_group = 'middle' then 3
                    when name_yield_group = 'high' then 4 end) as PA_PCT_RISK_AVG
        from previous_application
        where 1=1
            and flag_last_appl_per_contract = 'Y'
            and nflag_last_appl_in_day = 1
            and name_contract_type <> 'XNA'
        group by
            sk_id_curr
    ) as q
), 
pa_act_loans as (
    select
        sk_id_curr,
        count(*) as PA_ACT_LOANS_CNT,
        avg(amt_credit) as PA_ACT_LOANS_AVG,
        sum(amt_credit) as PA_ACT_LOANS_SUM,
        sum(amt_annuity) as PA_ACT_LOANS_ANN_SUM,
    from previous_application
    where 1=1
        and flag_last_appl_per_contract = 'Y'
        and nflag_last_appl_in_day = 1
        and name_contract_type <> 'XNA'
        and name_contract_status = 'Approved'
        and cnt_payment*30 + days_decision > 0
    group by
        sk_id_curr
),
ip_loans as (
    select 
        sk_id_curr,
        avg(days_late) as IP_LOANS_DAYS_LATE_AVG
    from (
        select 
            i.sk_id_prev,
            i.sk_id_curr,
            i.num_instalment_number,
            avg(i.days_instalment) as days_instalment,
            avg(i.days_entry_payment) as days_entry_payment,
            avg(i.days_entry_payment) - avg(i.days_instalment) as days_late
        from previous_application as p
        join installments_payments as i on p.sk_id_prev = i.sk_id_prev
        where 1=1
            and p.flag_last_appl_per_contract = 'Y'
            and p.nflag_last_appl_in_day = 1
            and p.name_contract_type <> 'XNA'
            and p.name_portfolio <> 'Cards'
            and p.name_contract_status = 'Approved'
            and p.days_decision >= -365*5
            and i.amt_payment > 100
            and i.num_instalment_number <= 12
        group by
            i.sk_id_prev,
            i.sk_id_curr,
            i.num_instalment_version,
            i.num_instalment_number
    ) as q
        group by
            sk_id_curr
),
ip_cards as (
    select 
        sk_id_curr,
        avg(days_late) as IP_CC_DAYS_LATE_AVG
    from (
        select 
            i.sk_id_prev,
            i.sk_id_curr,
            i.num_instalment_number,
            avg(i.days_instalment) as days_instalment,
            avg(i.days_entry_payment) as days_entry_payment,
            avg(i.days_entry_payment) - avg(i.days_instalment) as days_late
        from previous_application as p
        join installments_payments as i on p.sk_id_prev = i.sk_id_prev
        where 1=1
            and p.flag_last_appl_per_contract = 'Y'
            and p.nflag_last_appl_in_day = 1
            and p.name_contract_type <> 'XNA'
            and p.name_portfolio = 'Cards'
            and p.name_contract_status = 'Approved'
            and p.days_decision >= -365*5
            and i.amt_payment > 50
            and i.num_instalment_number <= 24
        group by
            i.sk_id_prev,
            i.sk_id_curr,
            i.num_instalment_version,
            i.num_instalment_number
    ) as q
        group by
            sk_id_curr
),
ip_loans_dpd as (
    select
        sk_id_curr,
        avg(ip_loans_dpd) as IP_LOANS_DPD
    from (
        select 
            sk_id_prev,
            sk_id_curr,
            sum(case when days_late > 0 then 1 else 0 end) as IP_LOANS_DPD
        from (
            select 
                i.sk_id_prev,
                i.sk_id_curr,
                i.num_instalment_number,
                avg(i.days_instalment) as days_instalment,
                avg(i.days_entry_payment) as days_entry_payment,
                avg(i.days_entry_payment) - avg(i.days_instalment) as days_late
            from previous_application as p
            join installments_payments as i on p.sk_id_prev = i.sk_id_prev
            where 1=1
                and p.flag_last_appl_per_contract = 'Y'
                and p.nflag_last_appl_in_day = 1
                and p.name_contract_type <> 'XNA'
                and p.name_portfolio <> 'Cards'
                and p.name_contract_status = 'Approved'
                and p.days_decision >= -365*5
                and i.amt_payment > 100
                and i.num_instalment_number <= 12
            group by
                i.sk_id_prev,
                i.sk_id_curr,
                i.num_instalment_version,
                i.num_instalment_number
        ) as q
        group by
            sk_id_prev,
            sk_id_curr
    )
    group by
        sk_id_curr
),
ip_cards_dpd as (
    select
        sk_id_curr,
        avg(ip_cc_dpd) as IP_CC_DPD
    from (
        select 
            sk_id_prev,
            sk_id_curr,
            sum(case when days_late > 0 then 1 else 0 end) as IP_CC_DPD
        from (
            select 
                i.sk_id_prev,
                i.sk_id_curr,
                i.num_instalment_number,
                avg(i.days_instalment) as days_instalment,
                avg(i.days_entry_payment) as days_entry_payment,
                avg(i.days_entry_payment) - avg(i.days_instalment) as days_late
            from previous_application as p
            join installments_payments as i on p.sk_id_prev = i.sk_id_prev
            where 1=1
                and p.flag_last_appl_per_contract = 'Y'
                and p.nflag_last_appl_in_day = 1
                and p.name_contract_type <> 'XNA'
                and p.name_portfolio = 'Cards'
                and p.name_contract_status = 'Approved'
                and p.days_decision >= -365*5
                and i.amt_payment > 50
                and i.num_instalment_number <= 24
            group by
                i.sk_id_prev,
                i.sk_id_curr,
                i.num_instalment_version,
                i.num_instalment_number
        ) as q
        group by
            sk_id_prev,
            sk_id_curr
    )
    group by
        sk_id_curr
),
cc_loading as (
    select 
        sk_id_curr,
        avg(cc_loading) as CC_LOADING_AVG
    from (
        select 
            sk_id_curr,
            sk_id_prev,
            months_balance,
            amt_balance,
            amt_credit_limit_actual,
            cc_ratio,
            case when cc_ratio between 0 and 5 then 0
                    when cc_ratio > 5 and cc_ratio <= 25 then 1
                    when cc_ratio > 25 and cc_ratio <= 50 then 2
                    when cc_ratio > 50 and cc_ratio <= 75 then 3
                    when cc_ratio > 75 and cc_ratio <= 100 then 4
                    when cc_ratio > 100 then 5
                    else 0
                end as cc_loading
        from (
        select 
            c.sk_id_curr,
            c.sk_id_prev,
            c.months_balance,
            c.amt_balance,
            c.amt_credit_limit_actual,
            c.amt_balance / c.amt_credit_limit_actual * 100 as cc_ratio,
            row_number() over (partition by c.sk_id_prev order by c.months_balance desc) as cnt
        from previous_application as p
        join credit_card_balance as c on p.sk_id_prev = c.sk_id_prev
        where 1=1
            and p.flag_last_appl_per_contract = 'Y'
            and p.nflag_last_appl_in_day = 1
            and p.name_contract_type <> 'XNA'
            and p.name_portfolio = 'Cards'
            and p.name_contract_status = 'Approved'
            and p.days_decision >= -365*2
        ) as q
        where cnt <= 6
    )
    group by
        sk_id_curr
)
select 
    app_tst.*,
    -- cb_active_loans
    coalesce(cbl_act.CB_HAS_MORTAGE, 0) as CB_HAS_MORTAGE,
    coalesce(cbl_act.CB_HAS_CARLOAN, 0) as CB_HAS_CARLOAN,
    coalesce(cbl_act.CB_HAS_CC, 0) as CB_HAS_CC,
    coalesce(cbl_act.CB_ACT_LOANS_CNT, 0) as CB_ACT_LOANS_CNT,
    coalesce(cbl_act.CB_ACT_LOANS_AVG, 0) as CB_ACT_LOANS_AVG,
    coalesce(cbl_act.CB_ACT_LOANS_SUM, 0) as CB_ACT_LOANS_SUM,
    -- cb_past_loans
    coalesce(cbl_pst.CB_PST_LOANS_CNT, 0) as CB_PST_LOANS_CNT,
    coalesce(cbl_pst.CB_PST_LOANS_AVG, 0) as CB_PST_LOANS_AVG,
    coalesce(cbl_pst.CB_PST_LOANS_SUM, 0) as CB_PST_LOANS_SUM,
    coalesce(cbl_act.CB_ACT_LOANS_CNT / cbl_pst.CB_PST_LOANS_CNT, 0) as CB_LOANS_CNT_RATIO,
    coalesce(cbl_act.CB_ACT_LOANS_AVG / cbl_pst.CB_PST_LOANS_AVG, 0) as CB_LOANS_AVG_RATIO,
    coalesce(cbl_act.CB_ACT_LOANS_SUM / cbl_pst.CB_PST_LOANS_SUM, 0) as CB_LOANS_SUM_RATIO,
    -- cb_payments_first
    coalesce(cbp_fst.CB_DPD_FIRST_CNT, -99999) as CB_DPD_FIRST_CNT,
    coalesce(cbp_fst.CB_DPD_FIRST_SUM, -99999) as CB_DPD_FIRST_SUM,
    -- cb_payments_last
    coalesce(cbp_lst.CB_DPD_LAST_CNT, -99999) as CB_DPD_LAST_CNT,
    coalesce(cbp_lst.CB_DPD_LAST_SUM, -99999) as CB_DPD_LAST_SUM,
    -- pa_all_loans
    coalesce(pa_all.PA_LOANS_APP_PCT, -99999) as PA_LOANS_APP_PCT,
    coalesce(pa_all.PA_LOANS_REF_PCT, -99999) as PA_LOANS_REF_PCT,
    coalesce(pa_all.PA_LOANS_UNU_PCT, -99999) as PA_LOANS_UNU_PCT,
    coalesce(pa_all.PA_LOANS_APP_AVG, -99999) as PA_LOANS_APP_AVG,
    coalesce(pa_all.PA_LOANS_REF_AVG, -99999) as PA_LOANS_REF_AVG,
    coalesce(pa_all.PA_LOANS_UNU_AVG, -99999) as PA_LOANS_UNU_AVG,
    coalesce(pa_all.PA_LOANS_APP_SUM, -99999) as PA_LOANS_APP_SUM,
    coalesce(pa_all.PA_LOANS_REF_SUM, -99999) as PA_LOANS_REF_SUM,
    coalesce(pa_all.PA_LOANS_UNU_SUM, -99999) as PA_LOANS_UNU_SUM,
    coalesce(pa_all.PA_DAYS_DECISION_MAX, -99999) as PA_DAYS_DECISION_MAX,
    coalesce(pa_all.PA_INSURED_AVG, -99999) as PA_INSURED_AVG,
    coalesce(pa_all.PA_LOANS_TERM_AVG, -99999) as PA_LOANS_TERM_AVG,
    coalesce(pa_all.PA_LOANS_TERM_MAX, -99999) as PA_LOANS_TERM_MAX,
    coalesce(pa_all.PA_PCT_RISK_AVG, -99999) as PA_PCT_RISK_AVG,
    -- pa_act_loans
    coalesce(pa_act.PA_ACT_LOANS_CNT, 0) as PA_ACT_LOANS_CNT,
    coalesce(pa_act.PA_ACT_LOANS_AVG, 0) as PA_ACT_LOANS_AVG,
    coalesce(pa_act.PA_ACT_LOANS_SUM, 0) as PA_ACT_LOANS_SUM,
    coalesce(pa_act.PA_ACT_LOANS_ANN_SUM, 0) as PA_ACT_LOANS_ANN_SUM,
    -- ip_loans
    coalesce(ip_lns.IP_LOANS_DAYS_LATE_AVG, -99999) as IP_LOANS_DAYS_LATE_AVG,
    -- ip_cards
    coalesce(ip_crd.IP_CC_DAYS_LATE_AVG, -99999) as IP_CC_DAYS_LATE_AVG,
    -- ip_loans_dpd
    coalesce(ip_lns_dpd.IP_LOANS_DPD, -99999) as IP_LOANS_DPD,
    -- ip_cards_dpd
    coalesce(ip_crd_dpd.IP_CC_DPD, -99999) as IP_CC_DPD,
    -- cc_loading
    coalesce(cc_ldn.CC_LOADING_AVG, -99999) as CC_LOADING_AVG
from id_list as i
left join app_test          as app_tst     on i.sk_id_curr = app_tst.sk_id_curr
left join cb_active_loans   as cbl_act     on i.sk_id_curr = cbl_act.sk_id_curr
left join cb_past_loans     as cbl_pst     on i.sk_id_curr = cbl_pst.sk_id_curr
left join cb_payments_first as cbp_fst     on i.sk_id_curr = cbp_fst.sk_id_curr
left join cb_payments_last  as cbp_lst     on i.sk_id_curr = cbp_lst.sk_id_curr
left join pa_all_loans      as pa_all      on i.sk_id_curr = pa_all.sk_id_curr
left join pa_act_loans      as pa_act      on i.sk_id_curr = pa_act.sk_id_curr
left join ip_loans          as ip_lns      on i.sk_id_curr = ip_lns.sk_id_curr
left join ip_cards          as ip_crd      on i.sk_id_curr = ip_crd.sk_id_curr
left join ip_loans_dpd      as ip_lns_dpd  on i.sk_id_curr = ip_lns_dpd.sk_id_curr
left join ip_cards_dpd      as ip_crd_dpd  on i.sk_id_curr = ip_crd_dpd.sk_id_curr
left join cc_loading        as cc_ldn      on i.sk_id_curr = cc_ldn.sk_id_curr