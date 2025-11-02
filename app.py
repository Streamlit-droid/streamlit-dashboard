import streamlit as st
import pandas as pd
import plotly.express as px
from dataclasses import asdict
from typing import Any

from api_response_processor.data_classes import (
PropertySummary, UnitsSummary,
RentSummaryForCurrentAndLastTwoMonths,
LeadsSummaryForThreeWeeks,
DelinquencyForThreeMonths,
ResidentRetentionSummaryForCurrentMonth
)

from api_response_processor import (property_unit_lead_summary_generator,
                                    rent_billed_collected_generator,
                                    delinquency_generator,
                                    resident_retention_generator)


# =========================
# GLOBALS / THEME
# =========================
ACCENT = "#0f988f"  # teal


# =========================
# PAGE SETUP & STYLES
# =========================
def setup_page():
    st.set_page_config(page_title="Property Dashboard", page_icon="🏢", layout="wide")

def inject_css():
    st.markdown(f"""
    <style>
    .main > div:first-child {{ padding-top: 0rem; }}
    .block-container {{ padding-top: 1rem; }}

    /* KPI cards */
    .kpi-grid {{ margin: .25rem 0 1rem; }}
    .kpi-card {{
      background: #dfeeea;               /* soft green */
      border-radius: 14px;
      padding: 14px 18px;
      box-shadow: 0 2px 14px rgba(0,0,0,.05);
      border: 1px solid rgba(0,0,0,.06);
    }}
    .kpi-label {{ font-size: 0.95rem; color: #4b5563; }}
    .kpi-value {{ font-size: 2rem; font-weight: 700; line-height: 1.1; }}

    div[data-testid="stPlotlyChart"] {{
      background: #f6faf9; border: 1px solid rgba(0,0,0,.08);
      border-radius: 14px; padding: 12px 12px 6px; box-shadow: 0 2px 12px rgba(0,0,0,.05);
    }}

    /* Segmented centered tabs */
    div[data-baseweb="tab-list"] {{
      width: 100%; max-width: 900px; margin: 0rem auto 0.75rem; padding: 6px;
      background: #eaf2f1; border-radius: 14px; box-shadow: 0 2px 16px rgba(0,0,0,.06);
      display: flex; gap: 6px;
    }}
    button[data-baseweb="tab"] {{
      flex: 1 1 0; justify-content: center; border-radius: 10px; background: transparent;
      color: #0b2b2b; font-weight: 700; font-size: 1.02rem; padding: .7rem 1.2rem;
      border: 2px solid transparent; transition: all .15s ease-in-out;
    }}
    button[data-baseweb="tab"]:hover {{ background: rgba(15,152,143,.08); }}
    button[data-baseweb="tab"][aria-selected="true"] {{
      background: {ACCENT}; color: #fff; border-color: {ACCENT};
      box-shadow: 0 1px 6px rgba(15,152,143,.35);
    }}
    button[data-baseweb="tab"] > div:first-child {{ border-bottom: none !important; }}
    </style>
    """, unsafe_allow_html=True)


# =========================
# HELPERS
# =========================
def safe_num(v: Any) -> float:
    """Convert Union[int,str,None] to float (NaN on fail)."""
    try:
        if v is None: return float("nan")
        if isinstance(v, str) and v.strip() == "": return float("nan")
        return float(v)
    except Exception:
        return float("nan")

def k(value, currency=False):
    if value in (None, "NA", ""): return "—"
    try:
        v = float(value)
        if currency: return f"${v/1000:,.2f} K"
        if v.is_integer(): return f"{int(v):,}"
        return f"{v:,.2f}"
    except Exception:
        return str(value)

def pct(value):
    if value in (None, "NA", ""): return "—"
    try:
        v = float(str(value).replace("%",""))
        return f"{v:,.2f} %"
    except Exception:
        return str(value)

def kpi_card(label: str, value: str):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def dc_to_df(obj) -> pd.DataFrame:
    """Dataclass -> one-row DataFrame (flat)."""
    return pd.DataFrame([asdict(obj)])

def cardify(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.1)", borderwidth=1
        )
    )
    return fig


# =========================
# DEMO DATA (replace with your real instances)
# =========================
def create_demo_models():
    property_id = 100102627 #The reserve at rye 290
    (all_property_summary,
     all_unit_summary,
     leads_summary_for_three_weeks) = property_unit_lead_summary_generator.generate_property_unit_lead_summary(property_id)
    # rent summary
    rent_summary = rent_billed_collected_generator.generate_rent_billed_collected_summary(property_id)
    delinquency_summary = delinquency_generator.generate_delinquency_report(property_id)

    # resident retention summary
    resident_retention_summary = resident_retention_generator.build_resident_retention(property_id)

    return (all_property_summary,
            all_unit_summary,
            resident_retention_summary,
            rent_summary,
            delinquency_summary,
            leads_summary_for_three_weeks)


# =========================
# RENDERERS (tabs)
# =========================
def render_overview(ps_by_date: dict[str, PropertySummary],
                    rs: RentSummaryForCurrentAndLastTwoMonths,
                    dq: DelinquencyForThreeMonths):
    """
    ps_by_date: Ordered dict {date_string: PropertySummary, ...}
                First item = latest date.
    rs: RentSummaryForCurrentAndLastTwoMonths dataclass.
    """

    # ---- KPIs from latest ----
    latest_date, latest_ps = next(iter(ps_by_date.items()))

    st.markdown('<div class="kpi-grid"></div>', unsafe_allow_html=True)
    a,b,c,d,e,f,g = st.columns(7, gap="small")
    with a: kpi_card("Total Units", k(latest_ps.total_units))
    with b: kpi_card("Rentable Units", k(latest_ps.total_rentable_units))
    with c: kpi_card("Excluded Units", k(latest_ps.excluded_units))
    with d: kpi_card("Occupied %", pct(latest_ps.occupied_units_percentage))
    with e: kpi_card("Leased %", pct(latest_ps.leased_units_percentage))
    with f: kpi_card("Trend %", pct(latest_ps.trend_percentage))
    with g: kpi_card("Evictions/Skips", k(latest_ps.evictions_and_skips_occurred))

    # ---- Rent billed vs collected (3 months) ----
    rent_rows = [
        {
            "Period": rs.current_month_date,
            "Billed": safe_num(rs.current_month_total_rent_billed),
            "Collected": safe_num(rs.current_month_total_rent_collected),
        },
        {
            "Period": rs.last_month_date,
            "Billed": safe_num(rs.last_month_total_rent_billed),
            "Collected": safe_num(rs.last_month_total_rent_collected),
        },
        {
            "Period": rs.month_before_last_date,
            "Billed": safe_num(rs.month_before_last_total_rent_billed),
            "Collected": safe_num(rs.month_before_last_total_rent_collected),
        },
    ]
    rent_df = pd.DataFrame(rent_rows)
    rent_long = rent_df.melt(id_vars=["Period"],
                             value_vars=["Billed","Collected"],
                             var_name="Type", value_name="Amount")

    left, right = st.columns(2)
    with left:
        st.subheader("Rent billed vs collected")
        fig = px.bar(rent_long, x="Period", y="Amount", color="Type", barmode="group", text_auto=".0f")
        st.plotly_chart(cardify(fig), use_container_width=True, key="rent_billed_collected")

    with right:
        st.subheader("Delinquency")
        coll = pd.DataFrame({
            "Period": ["0-30 Days","30-60 Days","60-90 Days"],
            "Delinquency": [
                safe_num(dq.current_month_delinquency),
                safe_num(dq.last_month_delinquency),
                safe_num(dq.month_before_last_delinquency),
            ]
        })
        fig2 = px.bar(coll, x="Period", y="Delinquency", text_auto=".0f")
        st.plotly_chart(cardify(fig2), use_container_width=True, key="collection_pct")

    # ---- Raw property summaries table ----
    raw_rows = []
    for date_key, ps in ps_by_date.items():
        row = {"Date": date_key, **asdict(ps)}
        raw_rows.append(row)
    raw_df = pd.DataFrame(raw_rows)

    st.write("---")
    st.subheader("Property summary (raw)")
    st.dataframe(raw_df, use_container_width=True, hide_index=True, key="ps_table")


def render_operations(us_by_date: dict[str, UnitsSummary],
                      leads: LeadsSummaryForThreeWeeks):
    """
    us_by_date: Ordered dict {date_string: UnitsSummary, ...}
                First item = latest date.
    maint: MaintenanceSummaryForThreeWeeks dataclass.
    leads: LeadsSummaryForThreeWeeks dataclass.
    """

    # ---- KPIs from latest UnitsSummary ----
    latest_date, latest_us = next(iter(us_by_date.items()))

    st.markdown('<div class="kpi-grid"></div>', unsafe_allow_html=True)
    a,b,c,d = st.columns(4, gap="large")
    with a: kpi_card("Occupied Units", k(latest_us.count_of_occupied_units))
    with b: kpi_card("Vacant Units", k(latest_us.count_of_vacant_units))
    with c: kpi_card(f"Move-ins ({latest_date})", k(latest_us.count_of_total_move_ins))
    with d: kpi_card(f"Move-outs ({latest_date})", k(latest_us.count_of_total_move_out))

    # ---- Leads (3 weeks) ----
    leads_df = pd.DataFrame([
        {"Week":"Current", "Range": f"{leads.current_week_start_date} → {leads.current_week_end_date}",
         "New Leads":safe_num(leads.current_week_new_leads_count),
         "Tours":safe_num(leads.current_week_tours_count),
         "Application Completed":safe_num(leads.current_week_applications_completed_count),
         "Lease Approved":safe_num(leads.current_week_lease_approved_count)},
        {"Week":"Last", "Range": f"{leads.last_week_start_date} → {leads.last_week_end_date}",
         "New Leads":safe_num(leads.last_week_new_leads_count),
         "Tours":safe_num(leads.last_week_tours_count),
         "Application Completed":safe_num(leads.last_week_applications_completed_count),
         "Lease Approved":safe_num(leads.last_week_lease_approved_count)},
        {"Week":"Week Before Last", "Range": f"{leads.week_before_last_start_date} → {leads.week_before_last_end_date}",
         "New Leads":safe_num(leads.week_before_last_new_leads_count),
         "Tours":safe_num(leads.week_before_last_tours_count),
         "Application Completed":safe_num(leads.week_before_last_applications_completed_count),
         "Lease Approved":safe_num(leads.week_before_last_lease_approved_count)},
    ])
    leads_long = leads_df.melt(id_vars=["Week","Range"], var_name="Stage", value_name="Count")

    # ---- Charts ----

    st.subheader("Leads & Applications (3 weeks)")
    fig4 = px.bar(leads_long, x="Week", y="Count", color="Stage", barmode="group",
                  hover_data=["Range"], text_auto=".0f")
    st.plotly_chart(cardify(fig4), use_container_width=True, key="leads_3w")

    # ---- Raw UnitsSummary table ----
    raw_rows = []
    for date_key, us in us_by_date.items():
        row = {"Date": date_key, **asdict(us)}
        raw_rows.append(row)
    raw_df = pd.DataFrame(raw_rows)

    st.write("---")
    st.subheader("Units summary (raw)")
    st.dataframe(raw_df, use_container_width=True, hide_index=True, key="us_table")


def render_retention(rr3: ResidentRetentionSummaryForCurrentMonth):
    st.markdown('<div class="kpi-grid"></div>', unsafe_allow_html=True)
    a,b = st.columns(2, gap="large")
    with a: kpi_card("Expiring Leases", k(rr3.expiring_leases))
    with b: kpi_card("Renewals", k(rr3.renewals))


# =========================
# ENTRY POINT
# =========================
def main():
    setup_page()
    inject_css()

    # Replace the following line with your real dataclass instances
    ps, us, resident_retent3, rent3, dq3, leads3 = create_demo_models()

    st.title("🏢 Property Dashboard for The Reserve at Rye 290")

    t1, t2, t3 = st.tabs(["Overview", "Operations", "Resident Retention"])
    with t1:
        render_overview(ps, rent3, dq3)
    with t2:
        render_operations(us, leads3)
    with t3:
        render_retention(resident_retent3)

if __name__ == "__main__":
    main()
