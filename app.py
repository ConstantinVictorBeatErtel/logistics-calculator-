import streamlit as st
import pandas as pd
import math

st.set_page_config(
    page_title="Surge AI — Logistics Calculator",
    page_icon="⚡",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
div[data-testid="stMetric"] label { color: #a5b4fc !important; font-size: 0.85rem !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #e0e7ff !important; font-weight: 700 !important; }

details { border: 1px solid rgba(99, 102, 241, 0.2) !important; border-radius: 10px !important; }
summary { font-weight: 600 !important; }
th { background: #312e81 !important; color: #e0e7ff !important; }
td, th { padding: 8px 12px !important; }

.section-header {
    background: linear-gradient(90deg, #312e81 0%, #1e1b4b 100%);
    padding: 12px 20px;
    border-radius: 10px;
    margin-bottom: 4px;
}
.section-header h2 { color: #e0e7ff; margin: 0; font-size: 1.3rem; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER + SUMMARY PLACEHOLDER (filled at bottom after all calcs)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("# ⚡ Surge AI — Logistics Calculator")
st.markdown("Each section has foldable **assumptions** — tweak any number and everything recalculates.")
st.divider()

# Reserve a container at the top for the summary KPI cards
summary_container = st.container()
st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# 1. VOLUME & DISTRIBUTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><h2>📦 1 — Volume & Distribution</h2></div>', unsafe_allow_html=True)

with st.expander("Assumptions", expanded=False):
    v1, v2 = st.columns(2)
    with v1:
        total_deliverable = st.number_input("Total deliverable submissions", value=100, step=10, min_value=1, key="vol_total")
        st.markdown("**Category mix**")
        cat_a_pct = st.slider("Category A %", 0, 100, 30, 5, key="vol_a")
        cat_b_pct = st.slider("Category B %", 0, 100, 50, 5, key="vol_b")
        cat_c_pct = 100 - cat_a_pct - cat_b_pct
        if cat_c_pct < 0:
            st.error("A% + B% exceeds 100%. Adjust sliders.")
            cat_c_pct = 0
        st.metric("Category C % (auto)", f"{cat_c_pct}%")
    with v2:
        st.markdown("**Rejection / failure rates**")
        fail_a = st.slider("Cat A failure rate %", 0, 50, 6, 1, key="vol_fa")
        fail_b = st.slider("Cat B failure rate %", 0, 50, 26, 1, key="vol_fb")
        fail_c = st.slider("Cat C failure rate %", 0, 50, 34, 1, key="vol_fc")

# Volume calcs
cat_a_target = round(total_deliverable * cat_a_pct / 100)
cat_b_target = round(total_deliverable * cat_b_pct / 100)
cat_c_target = total_deliverable - cat_a_target - cat_b_target

cat_a_required = math.ceil(cat_a_target / (1 - fail_a / 100)) if fail_a < 100 else cat_a_target
cat_b_required = math.ceil(cat_b_target / (1 - fail_b / 100)) if fail_b < 100 else cat_b_target
cat_c_required = math.ceil(cat_c_target / (1 - fail_c / 100)) if fail_c < 100 else cat_c_target
total_required = cat_a_required + cat_b_required + cat_c_required

# Dashboard
vm1, vm2, vm3, vm4 = st.columns(4)
vm1.metric("Cat A required", cat_a_required)
vm2.metric("Cat B required", cat_b_required)
vm3.metric("Cat C required", cat_c_required)
vm4.metric("Total required", total_required)

volume_df = pd.DataFrame({
    "Category": ["A (Simple)", "B (Reasoning)", "C (Synthesis)", "Total"],
    "Target": [cat_a_target, cat_b_target, cat_c_target, total_deliverable],
    "Failure %": [f"{fail_a}%", f"{fail_b}%", f"{fail_c}%", "—"],
    "Required": [cat_a_required, cat_b_required, cat_c_required, total_required],
    "Buffer": [cat_a_required - cat_a_target, cat_b_required - cat_b_target,
               cat_c_required - cat_c_target, total_required - total_deliverable],
})
st.dataframe(volume_df, width="stretch", hide_index=True)
st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# 2. TIME
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><h2>⏱️ 2 — Time</h2></div>', unsafe_allow_html=True)

with st.expander("Assumptions", expanded=False):
    t1, t2 = st.columns(2)
    with t1:
        st.markdown("**Per-submission time**")
        time_a = st.number_input("Cat A (min)", value=10, step=5, min_value=1, key="t_a")
        time_b = st.number_input("Cat B (min)", value=35, step=5, min_value=1, key="t_b")
        time_c = st.number_input("Cat C (min)", value=60, step=5, min_value=1, key="t_c")
    with t2:
        st.markdown("**Qualification & QA**")
        qual_time = st.number_input("Qualification test time (min)", value=45, step=5, min_value=1, key="t_qual")
        qa_review_time = st.number_input("QA review time per submission (min)", value=30, step=5, min_value=1, key="t_qa")
        hours_per_worker_day = st.number_input("Work hours per worker per day", value=2.0, step=0.5, min_value=0.5, key="t_hpd")

# Time calcs
total_time_a = cat_a_required * time_a
total_time_b = cat_b_required * time_b
total_time_c = cat_c_required * time_c
total_annotation_time = total_time_a + total_time_b + total_time_c
total_qa_time = total_required * qa_review_time

# Dashboard
tm1, tm2, tm3 = st.columns(3)
tm1.metric("Total Annotation Time", f"{total_annotation_time} min ({total_annotation_time/60:.1f} hrs)")
tm2.metric("Total QA Time", f"{total_qa_time} min ({total_qa_time/60:.1f} hrs)")
tm3.metric("Combined Time", f"{(total_annotation_time + total_qa_time)/60:.1f} hrs")

time_df = pd.DataFrame({
    "Category": ["A (Simple)", "B (Reasoning)", "C (Synthesis)", "Total"],
    "Per Sub": [f"{time_a} min", f"{time_b} min", f"{time_c} min", "—"],
    "Subs": [cat_a_required, cat_b_required, cat_c_required, total_required],
    "Total Time": [f"{total_time_a} min", f"{total_time_b} min", f"{total_time_c} min", f"{total_annotation_time} min"],
    "Hours": [f"{total_time_a/60:.1f}", f"{total_time_b/60:.1f}", f"{total_time_c/60:.1f}", f"{total_annotation_time/60:.1f}"],
})
st.dataframe(time_df, width="stretch", hide_index=True)
st.caption(f"ℹ️ Submissions Required trickles down from **Volume** section ({total_required} total).")
st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# 3. PEOPLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><h2>👥 3 — People</h2></div>', unsafe_allow_html=True)

with st.expander("Assumptions", expanded=False):
    p1, p2 = st.columns(2)
    with p1:
        st.markdown("**Worker pool**")
        target_workers = st.number_input("Target active workers", value=12, step=1, min_value=1, key="p_tw")
        cat_c_workers = st.number_input("Cat C-qualified workers", value=8, step=1, min_value=0, key="p_cw")
        cat_b_only_workers = st.number_input("Cat B-only workers", value=4, step=1, min_value=0, key="p_bw")
    with p2:
        st.markdown("**Funnel rates**")
        retention_rate = st.slider("Worker retention rate %", 10, 100, 80, 5, key="p_ret")
        pass_rate = st.slider("Qualification pass rate %", 10, 100, 40, 5, key="p_pass")
        invite_take_rate = st.slider("Invite take rate %", 10, 100, 50, 5, key="p_inv")

# People calcs
workers_before_retention = math.ceil(target_workers / (retention_rate / 100))
workers_before_pass = math.ceil(workers_before_retention / (pass_rate / 100))
workers_to_invite = math.ceil(workers_before_pass / (invite_take_rate / 100))
total_workers = cat_c_workers + cat_b_only_workers

# Pipeline
st.markdown("#### Recruitment Funnel")
pm1, pm2, pm3, pm4 = st.columns(4)
pm1.metric("Target Active", target_workers)
pm2.metric(f"Need (retention {retention_rate}%)", workers_before_retention)
pm3.metric(f"Need (pass rate {pass_rate}%)", workers_before_pass)
pm4.metric(f"Invitations ({invite_take_rate}%)", workers_to_invite)

# Workload per worker type
st.markdown("#### Workload per Worker")

if cat_c_workers > 0:
    a_per_c = round(cat_a_required * (cat_c_workers / max(total_workers, 1)) / cat_c_workers, 1)
    b_per_c = round(cat_b_required * (cat_c_workers / max(total_workers, 1)) / cat_c_workers, 1)
    c_per_c = round(cat_c_required / max(cat_c_workers, 1), 1)
    time_c_worker = a_per_c * time_a + b_per_c * time_b + c_per_c * time_c
    days_c_worker = time_c_worker / (hours_per_worker_day * 60)
else:
    a_per_c = b_per_c = c_per_c = time_c_worker = days_c_worker = 0

if cat_b_only_workers > 0:
    a_per_b = round(cat_a_required * (cat_b_only_workers / max(total_workers, 1)) / cat_b_only_workers, 1)
    leftover_b = cat_b_required - round(cat_b_required * cat_c_workers / max(total_workers, 1))
    b_per_b = round(leftover_b / cat_b_only_workers, 1)
    time_b_worker = a_per_b * time_a + b_per_b * time_b
    days_b_worker = time_b_worker / (hours_per_worker_day * 60)
else:
    a_per_b = b_per_b = time_b_worker = days_b_worker = 0

workload_rows = []
if cat_c_workers > 0:
    workload_rows.append({
        "Worker Type": f"Cat C-qualified (×{cat_c_workers})",
        "A subs": f"{a_per_c:.0f}", "B subs": f"{b_per_c:.0f}", "C subs": f"{c_per_c:.0f}",
        "Total min": f"{time_c_worker:.0f}", "Days": f"{days_c_worker:.1f}",
    })
if cat_b_only_workers > 0:
    workload_rows.append({
        "Worker Type": f"Cat B-only (×{cat_b_only_workers})",
        "A subs": f"{a_per_b:.0f}", "B subs": f"{b_per_b:.0f}", "C subs": "—",
        "Total min": f"{time_b_worker:.0f}", "Days": f"{days_b_worker:.1f}",
    })
if workload_rows:
    st.dataframe(pd.DataFrame(workload_rows), width="stretch", hide_index=True)

subs_per_day_c = ((a_per_c + b_per_c + c_per_c) / max(days_c_worker, 0.01)) * cat_c_workers if cat_c_workers else 0
subs_per_day_b = ((a_per_b + b_per_b) / max(days_b_worker, 0.01)) * cat_b_only_workers if cat_b_only_workers else 0
total_subs_day = subs_per_day_c + subs_per_day_b

st.metric("Est. Total Submissions / Day", f"~{total_subs_day:.0f}")
st.caption(f"ℹ️ Per-submission times trickle down from **Time** section (A={time_a}m, B={time_b}m, C={time_c}m) · {hours_per_worker_day}h/day.")
st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# 4. QA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><h2>🔍 4 — Quality Assurance</h2></div>', unsafe_allow_html=True)

with st.expander("Assumptions", expanded=False):
    qa_col1, qa_col2 = st.columns(2)
    with qa_col1:
        qa_days_available = st.number_input("Days available for QA", value=7, step=1, min_value=1, key="qa_days")
    with qa_col2:
        st.caption(f"QA review time per submission: **{qa_review_time} min** (set in Time section)")

reviews_per_day = total_required / max(qa_days_available, 1)
qa_hours_per_day = reviews_per_day * qa_review_time / 60

qa1, qa2, qa3 = st.columns(3)
qa1.metric("Total Reviews", total_required)
qa2.metric("Reviews / Day", f"~{reviews_per_day:.1f}")
qa3.metric("QA Hours / Day", f"{qa_hours_per_day:.1f} hrs")
st.caption(f"ℹ️ Total reviews trickle down from **Volume** ({total_required}) · Review time from **Time** ({qa_review_time} min).")
st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# 5. MONEY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><h2>💰 5 — Money</h2></div>', unsafe_allow_html=True)

with st.expander("Assumptions — Labour", expanded=False):
    mo1, mo2 = st.columns(2)
    with mo1:
        worker_hourly = st.number_input("Worker hourly rate ($)", value=20.0, step=1.0, min_value=1.0, key="mo_wh")
        reviewer_hourly = st.number_input("Reviewer hourly rate ($)", value=50.0, step=5.0, min_value=1.0, key="mo_rh")
    with mo2:
        reviewer_hours = st.number_input("Total reviewer hours", value=5.0, step=1.0, min_value=0.0, key="mo_rhrs")

with st.expander("Assumptions — Tech Cost", expanded=False):
    tc1, tc2 = st.columns(2)
    with tc1:
        st.markdown("**Infrastructure**")
        cost_filings = st.number_input("Filings ($)", value=0.0, step=5.0, min_value=0.0, key="tc_filings")
        cost_auto_check = st.number_input("Automated checking ($)", value=20.0, step=5.0, min_value=0.0, key="tc_autocheck")
        cost_database = st.number_input("Database ($)", value=30.0, step=5.0, min_value=0.0, key="tc_db")

    with tc2:
        st.markdown("**LLM — Token Pricing**")
        llm_price_input = st.number_input("Input token price ($/M)", value=2.0, step=0.5, min_value=0.0, key="tc_llm_pin")
        llm_price_output = st.number_input("Output token price ($/M)", value=12.0, step=1.0, min_value=0.0, key="tc_llm_pout")

    st.markdown("---")
    st.markdown("**LLM — Submissions**")
    st.caption(f"Number of submissions: **{total_required}** (from Volume section)")
    lc1, lc2 = st.columns(2)
    with lc1:
        st.markdown("*Without SEC filing context*")
        tok_sub_in_nosec = st.number_input("Input tokens / question", value=2000, step=500, min_value=0, key="tc_sub_in_nosec")
        tok_sub_out_nosec = st.number_input("Output tokens / question", value=100, step=50, min_value=0, key="tc_sub_out_nosec")
    with lc2:
        st.markdown("*With SEC filing context*")
        tok_sub_in_sec = st.number_input("Input tokens / question", value=50000, step=5000, min_value=0, key="tc_sub_in_sec")
        tok_sub_out_sec = st.number_input("Output tokens / question", value=100, step=50, min_value=0, key="tc_sub_out_sec")

    st.markdown("---")
    st.markdown("**LLM — Evaluations**")
    num_evals = st.number_input("Number of evaluations", value=total_required, step=1, min_value=0, key="tc_num_evals")
    le1, le2 = st.columns(2)
    with le1:
        tok_eval_in = st.number_input("Input tokens / eval", value=1000, step=500, min_value=0, key="tc_eval_in")
    with le2:
        tok_eval_out = st.number_input("Output tokens / eval", value=100, step=50, min_value=0, key="tc_eval_out")

# ── LLM cost calcs ───────────────────────────────────────────────────────────
# Submissions — without SEC
total_sub_in_nosec = total_required * tok_sub_in_nosec
total_sub_out_nosec = total_required * tok_sub_out_nosec
cost_sub_nosec_in = total_sub_in_nosec / 1_000_000 * llm_price_input
cost_sub_nosec_out = total_sub_out_nosec / 1_000_000 * llm_price_output
cost_sub_nosec = cost_sub_nosec_in + cost_sub_nosec_out

# Submissions — with SEC
total_sub_in_sec = total_required * tok_sub_in_sec
total_sub_out_sec = total_required * tok_sub_out_sec
cost_sub_sec_in = total_sub_in_sec / 1_000_000 * llm_price_input
cost_sub_sec_out = total_sub_out_sec / 1_000_000 * llm_price_output
cost_sub_sec = cost_sub_sec_in + cost_sub_sec_out

# Evaluations
total_eval_in = num_evals * tok_eval_in
total_eval_out = num_evals * tok_eval_out
cost_eval_in = total_eval_in / 1_000_000 * llm_price_input
cost_eval_out = total_eval_out / 1_000_000 * llm_price_output
cost_eval = cost_eval_in + cost_eval_out

total_llm_cost = cost_sub_sec + cost_eval  # conservative: use "with SEC" variant
infra_cost = cost_filings + cost_auto_check + cost_database
tech_cost = infra_cost + total_llm_cost

# ── Labour calcs ─────────────────────────────────────────────────────────────
worker_cost = total_annotation_time / 60 * worker_hourly
qual_cost = workers_to_invite * qual_time / 60 * worker_hourly
reviewer_cost = reviewer_hourly * reviewer_hours
total_cost = worker_cost + qual_cost + reviewer_cost + tech_cost

# ── Dashboard ─────────────────────────────────────────────────────────────────
mo_a, mo_b, mo_c, mo_d = st.columns(4)
mo_a.metric("Worker Cost", f"${worker_cost:,.0f}")
mo_b.metric("Qualification Cost", f"${qual_cost:,.0f}")
mo_c.metric("Reviewer Cost", f"${reviewer_cost:,.0f}")
mo_d.metric("Tech Cost", f"${tech_cost:,.2f}")

budget_df = pd.DataFrame({
    "Line Item": ["Worker Annotation", "Qualification Testing", "Expert Review", "Tech / Infrastructure", "TOTAL"],
    "Formula": [
        f"Total annotation time ÷ 60 × hourly rate → {total_annotation_time} min ÷ 60 × ${worker_hourly:.0f}",
        f"Invitations × qual time ÷ 60 × hourly rate → {workers_to_invite} × {qual_time} min ÷ 60 × ${worker_hourly:.0f}",
        f"Reviewer rate × hours → ${reviewer_hourly:.0f} × {reviewer_hours:.0f}h",
        f"Infra ${infra_cost:.0f} + LLM ${total_llm_cost:.2f}",
        "",
    ],
    "Cost": [f"${worker_cost:,.0f}", f"${qual_cost:,.0f}", f"${reviewer_cost:,.0f}", f"${tech_cost:,.2f}", f"${total_cost:,.2f}"],
})
st.dataframe(budget_df, width="stretch", hide_index=True)

# Tech cost detail table
st.markdown("#### 🖥️ Tech Cost Breakdown")
tech_df = pd.DataFrame({
    "Component": [
        "Filings", "Automated checking", "Database",
        f"LLM Submissions w/o SEC ({total_required}×)",
        f"LLM Submissions w/ SEC ({total_required}×)",
        f"LLM Evaluations ({num_evals}×)",
        "Total LLM (conservative, w/ SEC)",
        "TOTAL TECH",
    ],
    "Tokens In": [
        "—", "—", "—",
        f"{total_sub_in_nosec:,}", f"{total_sub_in_sec:,}", f"{total_eval_in:,}",
        f"{total_sub_in_sec + total_eval_in:,}", "—",
    ],
    "Tokens Out": [
        "—", "—", "—",
        f"{total_sub_out_nosec:,}", f"{total_sub_out_sec:,}", f"{total_eval_out:,}",
        f"{total_sub_out_sec + total_eval_out:,}", "—",
    ],
    "Cost": [
        f"${cost_filings:.2f}", f"${cost_auto_check:.2f}", f"${cost_database:.2f}",
        f"${cost_sub_nosec:.2f}", f"${cost_sub_sec:.2f}", f"${cost_eval:.2f}",
        f"${total_llm_cost:.2f}", f"${tech_cost:.2f}",
    ],
})
st.dataframe(tech_df, width="stretch", hide_index=True)
st.caption(f"ℹ️  Submissions ({total_required}) flow from **Volume** · Token pricing at ${llm_price_input}/M input, ${llm_price_output}/M output.")
st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# 6. TIMELINE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><h2>📅 6 — Timeline</h2></div>', unsafe_allow_html=True)

with st.expander("Assumptions", expanded=False):
    tl1, tl2 = st.columns(2)
    with tl1:
        days_data = st.number_input("Data creation + checking (days)", value=7, step=1, min_value=1, key="tl_data")
        days_meeting = st.number_input("Customer meeting (days)", value=1, step=1, min_value=0, key="tl_meet")
        days_finding = st.number_input("Finding people (days)", value=1, step=1, min_value=0, key="tl_find")
    with tl2:
        days_testing = st.number_input("Testing (days)", value=1, step=1, min_value=0, key="tl_test")
        days_compiling = st.number_input("Compiling & final check (days)", value=1, step=1, min_value=0, key="tl_comp")
        days_buffer = st.number_input("Buffer (days)", value=1, step=1, min_value=0, key="tl_buf")

timeline_items = [
    ("Finding people", days_finding),
    ("Testing / qualification", days_testing),
    ("Data creation + checking", days_data),
    ("Customer meeting", days_meeting),
    ("Compiling & final check", days_compiling),
    ("Buffer", days_buffer),
]
total_days = sum(d for _, d in timeline_items)

timeline_df = pd.DataFrame(timeline_items, columns=["Phase", "Days"])
timeline_df["Start Day"] = timeline_df["Days"].cumsum() - timeline_df["Days"]
timeline_df["End Day"] = timeline_df["Days"].cumsum()

tc1, tc2 = st.columns([2, 1])
with tc1:
    st.dataframe(timeline_df, width="stretch", hide_index=True)
with tc2:
    st.metric("Total Project Duration", f"{total_days} days")
    st.metric("~Calendar Weeks", f"{math.ceil(total_days / 5):.0f} weeks")


# ══════════════════════════════════════════════════════════════════════════════
# FILL THE SUMMARY AT THE TOP (now that all values are computed)
# ══════════════════════════════════════════════════════════════════════════════
with summary_container:
    st.markdown('<div class="section-header"><h2>📊 Summary</h2></div>', unsafe_allow_html=True)
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("💰 Total Budget", f"${total_cost:,.0f}")
    s2.metric("📦 Submissions Required", f"{total_required}")
    s3.metric("📅 Duration", f"{total_days} days")
    s4.metric("👥 Invitations Needed", f"{workers_to_invite}")
    s5.metric("⏱️ Annotation Hours", f"{total_annotation_time/60:.1f}")

st.divider()
st.caption("Built for Surge AI case study logistics planning. Every number trickles through — change one assumption and the rest follows.")
