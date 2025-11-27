import streamlit as st
import pandas as pd
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.analysis import run_full_simulation
from app.ui import render_sidebar, render_summary_metrics
from app.charts import (
    create_hero_chart,
    create_wealth_composition_chart,
    create_cashflow_chart,
    create_contributions_chart,
    create_effective_tax_rate_chart,
    create_net_income_comparison_chart,
    create_withdrawal_composition_chart,
    create_accumulated_taxes_chart,
    create_cumulative_advantage_chart,
    create_net_cashflow_chart,
)

# Set page config
st.set_page_config(page_title="401k vs Roth Analysis", page_icon="💰", layout="wide")

st.title("💰 401k vs Roth 401k Analysis")
st.markdown("""
This tool compares the long-term impact of contributing to a **Traditional 401k** (Pre-Tax) vs a **Roth 401k** (After-Tax).
It simulates the accumulation phase (working years) and the distribution phase (retirement years), accounting for taxes, investment growth, and inflation.
""")

# --- Sidebar ---
config = render_sidebar()

# --- Run Analysis ---
results = run_full_simulation(
    annual_income=config["annual_income"],
    current_age=config["current_age"],
    retirement_age=config["retirement_age"],
    final_age=config["final_age"],
    accumulation_return=config["accumulation_return"],
    retirement_return=config["retirement_return"],
    contribution_input=config["contribution_input"],
    use_max_contribution=config["use_max_contribution"],
    employer_match_percent=config["match_percent"] / 100.0
    if config["match_percent"] > 0
    else 0,
    employer_match_limit=config["match_limit"] / 100.0
    if config["match_limit"] > 0
    else 0,
    invest_tax_savings=config["invest_tax_savings"],
    annual_raise_percent=config["annual_raise"],
)

acc_401k = results["accumulation_401k"]
acc_roth = results["accumulation_roth"]
dist_401k = results["distribution_401k"]
dist_roth = results["distribution_roth"]

# --- Summary Metrics ---
render_summary_metrics(
    acc_401k,
    acc_roth,
    dist_401k,
    dist_roth,
    config["retirement_age"],
    config["invest_tax_savings"],
)

# --- Visualizations ---
st.markdown("---")
st.header("📈 Lifetime Wealth Trajectory")

# Prepare data for Hero Chart
trad_data = pd.concat(
    [
        acc_401k[["Age", "Balance_PreTax", "Balance_Taxable"]],
        dist_401k[["Age", "Balance_PreTax", "Balance_Taxable"]],
    ]
)
trad_data["Strategy"] = "Traditional 401k"
trad_data = trad_data.melt(
    id_vars=["Age", "Strategy"],
    value_vars=["Balance_PreTax", "Balance_Taxable"],
    var_name="Account_Type",
    value_name="Balance",
)
trad_data["Account"] = trad_data["Strategy"] + " - " + trad_data["Account_Type"]

roth_data = pd.concat(
    [
        acc_roth[["Age", "Balance_Roth", "Balance_PreTax"]],
        dist_roth[["Age", "Balance_Roth", "Balance_PreTax"]],
    ]
)
roth_data["Strategy"] = "Roth 401k"
roth_data = roth_data.melt(
    id_vars=["Age", "Strategy"],
    value_vars=["Balance_Roth", "Balance_PreTax"],
    var_name="Account_Type",
    value_name="Balance",
)
roth_data["Account"] = roth_data["Strategy"] + " - " + roth_data["Account_Type"]

all_data = pd.concat([trad_data, roth_data])

st.altair_chart(create_hero_chart(all_data), use_container_width=True)

with st.expander("Debug Data"):
    st.write("Traditional 401k Data Head:")
    st.write(acc_401k[["Age", "Balance_PreTax", "Balance_Taxable"]].head())
    st.write("Melted Trad Data Head:")
    st.write(trad_data.head())

# --- Cashflow & Advantage ---
st.markdown("---")
st.header("💵 Cashflow & Advantage")

col_c1, col_c2 = st.columns(2)

with col_c1:
    st.subheader("Net Spendable Income Comparison")
    cf_dist_comp = pd.DataFrame(
        {
            "Age": dist_401k["Age"],
            "Traditional": dist_401k["Net_Income"],
            "Roth": dist_roth["Net_Income"],
        }
    ).melt("Age", var_name="Strategy", value_name="Income")
    st.altair_chart(
        create_net_income_comparison_chart(cf_dist_comp), use_container_width=True
    )

with col_c2:
    st.subheader("Cumulative Advantage (Trad - Roth)")
    adv_data = pd.DataFrame(
        {
            "Age": dist_401k["Age"],
            "Diff": dist_401k["Net_Income"] - dist_roth["Net_Income"],
        }
    )
    adv_data["Cumulative Advantage"] = adv_data["Diff"].cumsum()
    st.altair_chart(
        create_cumulative_advantage_chart(adv_data), use_container_width=True
    )

st.subheader("Annual Net Cash Flow (In/Out of Account)")
cf_io_trad = pd.concat(
    [
        acc_401k[["Age", "Contribution", "Match"]].assign(
            Flow="In", Amount=lambda x: x["Contribution"] + x["Match"]
        ),
        dist_401k[["Age", "Gross_Withdrawal"]].assign(
            Flow="Out", Amount=lambda x: -x["Gross_Withdrawal"]
        ),
    ]
)
cf_io_trad["Strategy"] = "Traditional"

cf_io_roth = pd.concat(
    [
        acc_roth[["Age", "Contribution", "Match"]].assign(
            Flow="In", Amount=lambda x: x["Contribution"] + x["Match"]
        ),
        dist_roth[["Age", "Gross_Withdrawal"]].assign(
            Flow="Out", Amount=lambda x: -x["Gross_Withdrawal"]
        ),
    ]
)
cf_io_roth["Strategy"] = "Roth"
cf_io_all = pd.concat([cf_io_trad, cf_io_roth])

st.altair_chart(create_net_cashflow_chart(cf_io_all), use_container_width=True)

# --- Deep Dive Grid ---
st.markdown("---")
st.header("🔍 Deep Dive Analysis")

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("💰 Wealth Composition (Trad)")
    comp_trad = pd.concat(
        [
            acc_401k[["Age", "Balance_PreTax", "Balance_Taxable"]],
            dist_401k[["Age", "Balance_PreTax", "Balance_Taxable"]],
        ]
    ).melt("Age", var_name="Account", value_name="Balance")
    st.altair_chart(
        create_wealth_composition_chart(comp_trad, "Trad"), use_container_width=True
    )

    st.subheader("💵 Cashflow: Net Spendable")
    cf_acc = acc_401k.copy()
    cf_acc["Net_Liquidity"] = cf_acc["Income"] - cf_acc["Contribution"]
    cf_dist = dist_401k.copy()
    cf_dist["Net_Liquidity"] = cf_dist["Net_Income"]
    cf_combined = pd.concat(
        [cf_acc[["Age", "Net_Liquidity"]], cf_dist[["Age", "Net_Liquidity"]]]
    )
    st.altair_chart(create_cashflow_chart(cf_combined), use_container_width=True)

    st.subheader("📥 Annual Contributions")
    contrib_data = acc_401k[["Age", "Contribution", "Match"]].melt(
        "Age", var_name="Type", value_name="Amount"
    )
    st.altair_chart(create_contributions_chart(contrib_data), use_container_width=True)

    st.subheader("📉 Effective Tax Rate (Lifetime)")
    st.caption(
        "Effective Tax Rate during retirement (Taxes / Gross Withdrawal). For Roth, taxes were paid upfront, so rate is low/zero."
    )
    etr_data = pd.DataFrame(
        {
            "Age": dist_401k["Age"],
            "Traditional": dist_401k["Effective_Tax_Rate"],
            "Roth": dist_roth["Effective_Tax_Rate"],
        }
    ).melt("Age", var_name="Strategy", value_name="Rate")
    st.altair_chart(create_effective_tax_rate_chart(etr_data), use_container_width=True)


with col_g2:
    st.subheader("💰 Wealth Composition (Roth)")
    comp_roth = pd.concat(
        [
            acc_roth[["Age", "Balance_Roth", "Balance_PreTax"]],
            dist_roth[["Age", "Balance_Roth", "Balance_PreTax"]],
        ]
    ).melt("Age", var_name="Account", value_name="Balance")
    st.altair_chart(
        create_wealth_composition_chart(comp_roth, "Roth"), use_container_width=True
    )

    st.subheader("📤 Withdrawal Composition (Trad)")
    wd_data = dist_401k[["Age", "Withdrawal_PreTax", "Withdrawal_Taxable"]].melt(
        "Age", var_name="Source", value_name="Amount"
    )
    st.altair_chart(
        create_withdrawal_composition_chart(wd_data), use_container_width=True
    )

    st.subheader("🏛️ Accumulated Taxes Paid")
    acc_401k["Annual_Tax"] = acc_401k["Tax_Paid"]
    dist_401k["Annual_Tax"] = dist_401k["Total_Tax"]
    full_tax_401k = pd.concat(
        [acc_401k[["Age", "Annual_Tax"]], dist_401k[["Age", "Annual_Tax"]]]
    )
    full_tax_401k["Cumulative_Tax"] = full_tax_401k["Annual_Tax"].cumsum()
    full_tax_401k["Strategy"] = "Traditional 401k"

    acc_roth["Annual_Tax"] = acc_roth["Tax_Paid"]
    dist_roth["Annual_Tax"] = dist_roth["Total_Tax"]
    full_tax_roth = pd.concat(
        [acc_roth[["Age", "Annual_Tax"]], dist_roth[["Age", "Annual_Tax"]]]
    )
    full_tax_roth["Cumulative_Tax"] = full_tax_roth["Annual_Tax"].cumsum()
    full_tax_roth["Strategy"] = "Roth 401k"

    tax_comp = pd.concat([full_tax_401k, full_tax_roth])
    st.altair_chart(create_accumulated_taxes_chart(tax_comp), use_container_width=True)

# --- Additional Metrics ---
st.markdown("---")
st.subheader("📊 Additional Metrics")

col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    st.metric("Total Contributions (Trad)", f"${acc_401k['Contribution'].sum():,.0f}")
    st.metric("Total Match Received", f"${acc_401k['Match'].sum():,.0f}")

with col_m2:
    st.metric(
        "Total Taxes Paid (Trad)", f"${full_tax_401k.iloc[-1]['Cumulative_Tax']:,.0f}"
    )
    st.metric(
        "Total Taxes Paid (Roth)", f"${full_tax_roth.iloc[-1]['Cumulative_Tax']:,.0f}"
    )

with col_m3:
    st.metric(
        "Avg Effective Tax Rate (Trad)", f"{dist_401k['Effective_Tax_Rate'].mean():.2%}"
    )
    st.metric(
        "Avg Effective Tax Rate (Roth)", f"{dist_roth['Effective_Tax_Rate'].mean():.2%}"
    )

# --- Detailed Analysis Tabs ---
st.markdown("---")
st.header("🔍 Detailed Data")

tab1, tab2 = st.tabs(["Traditional 401k Data", "Roth 401k Data"])

with tab1:
    st.dataframe(acc_401k)
    st.dataframe(dist_401k)

with tab2:
    st.dataframe(acc_roth)
    st.dataframe(dist_roth)
