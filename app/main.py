import streamlit as st
import pandas as pd
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.analysis import run_full_simulation, combine_simulation_results
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
    roth_split_percent=config["roth_split_percent"],
)

acc_401k = results["accumulation_401k"]
acc_roth = results["accumulation_roth"]
acc_split = results["accumulation_split"]
dist_401k = results["distribution_401k"]
dist_roth = results["distribution_roth"]
dist_split = results["distribution_split"]

# --- Combine Results ---
combined_trad = combine_simulation_results(acc_401k, dist_401k)
combined_roth = combine_simulation_results(acc_roth, dist_roth)
combined_split = combine_simulation_results(acc_split, dist_split)

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
trad_data = combined_trad[["Age", "Balance_PreTax", "Balance_Taxable"]].copy()
trad_data["Strategy"] = "Traditional 401k"
trad_data = trad_data.melt(
    id_vars=["Age", "Strategy"],
    value_vars=["Balance_PreTax", "Balance_Taxable"],
    var_name="Account_Type",
    value_name="Balance",
)
trad_data["Account"] = trad_data["Strategy"] + " - " + trad_data["Account_Type"]

roth_data = combined_roth[["Age", "Balance_Roth", "Balance_PreTax"]].copy()
roth_data["Strategy"] = "Roth 401k"
roth_data = roth_data.melt(
    id_vars=["Age", "Strategy"],
    value_vars=["Balance_Roth", "Balance_PreTax"],
    var_name="Account_Type",
    value_name="Balance",
)
roth_data["Account"] = roth_data["Strategy"] + " - " + roth_data["Account_Type"]

split_data = combined_split[
    ["Age", "Balance_PreTax", "Balance_Roth", "Balance_Taxable"]
].copy()
split_data["Strategy"] = f"Split ({config['roth_split_percent']:.0%})"
split_data = split_data.melt(
    id_vars=["Age", "Strategy"],
    value_vars=["Balance_PreTax", "Balance_Roth", "Balance_Taxable"],
    var_name="Account_Type",
    value_name="Balance",
)
split_data["Account"] = split_data["Strategy"] + " - " + split_data["Account_Type"]

all_data = pd.concat([trad_data, roth_data, split_data])

st.altair_chart(create_hero_chart(all_data), use_container_width=True)


# --- Cashflow & Advantage ---
st.markdown("---")
st.header("💵 Cashflow & Advantage")

col_c1, col_c2 = st.columns(2)

with col_c1:
    st.subheader("Net Spendable Income Comparison")
    # Filter for distribution phase
    dist_trad = combined_trad[combined_trad["Phase"] == "Distribution"]
    dist_roth = combined_roth[combined_roth["Phase"] == "Distribution"]
    dist_split = combined_split[combined_split["Phase"] == "Distribution"]

    cf_dist_comp = pd.DataFrame(
        {
            "Age": dist_trad["Age"],
            "Traditional": dist_trad["Net_Income"],
            "Roth": dist_roth["Net_Income"],
            "Split": dist_split["Net_Income"],
        }
    ).melt("Age", var_name="Strategy", value_name="Income")
    st.altair_chart(
        create_net_income_comparison_chart(cf_dist_comp), use_container_width=True
    )

with col_c2:
    st.subheader("Cumulative Advantage (Trad - Roth)")
    # Re-filter to ensure alignment (should be aligned by index if from same simulation run)
    dist_trad = combined_trad[combined_trad["Phase"] == "Distribution"].reset_index(
        drop=True
    )
    dist_roth = combined_roth[combined_roth["Phase"] == "Distribution"].reset_index(
        drop=True
    )

    adv_data = pd.DataFrame(
        {
            "Age": dist_trad["Age"],
            "Diff": dist_trad["Net_Income"] - dist_roth["Net_Income"],
        }
    )
    adv_data["Cumulative Advantage"] = adv_data["Diff"].cumsum()
    st.altair_chart(
        create_cumulative_advantage_chart(adv_data), use_container_width=True
    )

st.subheader("Annual Net Cash Flow (In/Out of Account)")
# In: Contribution + Match
# Out: -Gross_Withdrawal
cf_io_trad = combined_trad.copy()
cf_io_trad["Flow"] = cf_io_trad["Phase"].apply(
    lambda x: "In" if x == "Accumulation" else "Out"
)
cf_io_trad["Amount"] = cf_io_trad.apply(
    lambda x: (x["Contribution"] + x["Match"])
    if x["Phase"] == "Accumulation"
    else -x["Gross_Withdrawal"],
    axis=1,
)
cf_io_trad = cf_io_trad[["Age", "Flow", "Amount"]]
cf_io_trad["Strategy"] = "Traditional"

cf_io_roth = combined_roth.copy()
cf_io_roth["Flow"] = cf_io_roth["Phase"].apply(
    lambda x: "In" if x == "Accumulation" else "Out"
)
cf_io_roth["Amount"] = cf_io_roth.apply(
    lambda x: (x["Contribution"] + x["Match"])
    if x["Phase"] == "Accumulation"
    else -x["Gross_Withdrawal"],
    axis=1,
)
cf_io_roth = cf_io_roth[["Age", "Flow", "Amount"]]
cf_io_roth["Strategy"] = "Roth"

cf_io_all = pd.concat([cf_io_trad, cf_io_roth])

st.altair_chart(create_net_cashflow_chart(cf_io_all), use_container_width=True)

# --- Deep Dive Grid ---
st.markdown("---")
st.header("🔍 Deep Dive Analysis")

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("💰 Wealth Composition (Trad)")
    comp_trad = combined_trad[["Age", "Balance_PreTax", "Balance_Taxable"]].melt(
        "Age", var_name="Account", value_name="Balance"
    )
    st.altair_chart(
        create_wealth_composition_chart(comp_trad, "Trad"), use_container_width=True
    )

    st.subheader("💵 Cashflow: Net Spendable")
    # Net Spendable = Gross_Income - Contribution - Total_Tax (Accumulation)
    # Net Spendable = Net_Income (Distribution)
    # But wait, in Accumulation, Gross_Income is Salary.
    # In Distribution, Gross_Income is Withdrawal.
    # The chart should show "Net Liquidity" available to spend.

    cf_combined = combined_trad.copy()
    cf_combined["Net_Liquidity"] = cf_combined.apply(
        lambda x: (x["Gross_Income"] - x["Contribution"] - x["Total_Tax"])
        if x["Phase"] == "Accumulation"
        else x["Net_Income"],
        axis=1,
    )
    st.altair_chart(
        create_cashflow_chart(cf_combined[["Age", "Net_Liquidity"]]),
        use_container_width=True,
    )

    st.subheader("📥 Annual Contributions")
    acc_only_trad = combined_trad[combined_trad["Phase"] == "Accumulation"]
    contrib_data = acc_only_trad[["Age", "Contribution", "Match"]].melt(
        "Age", var_name="Type", value_name="Amount"
    )
    st.altair_chart(create_contributions_chart(contrib_data), use_container_width=True)

    st.subheader("📉 Effective Tax Rate (Lifetime)")
    st.caption(
        "Effective Tax Rate during retirement (Taxes / Gross Withdrawal). For Roth, taxes were paid upfront, so rate is low/zero."
    )
    dist_trad = combined_trad[combined_trad["Phase"] == "Distribution"]
    dist_roth = combined_roth[combined_roth["Phase"] == "Distribution"]

    etr_data = pd.DataFrame(
        {
            "Age": dist_trad["Age"],
            "Traditional": dist_trad["Effective_Tax_Rate"],
            "Roth": dist_roth["Effective_Tax_Rate"],
        }
    ).melt("Age", var_name="Strategy", value_name="Rate")
    st.altair_chart(create_effective_tax_rate_chart(etr_data), use_container_width=True)


with col_g2:
    st.subheader("💰 Wealth Composition (Roth)")
    comp_roth = combined_roth[["Age", "Balance_Roth", "Balance_PreTax"]].melt(
        "Age", var_name="Account", value_name="Balance"
    )
    st.altair_chart(
        create_wealth_composition_chart(comp_roth, "Roth"), use_container_width=True
    )

    st.subheader("📤 Withdrawal Composition (Trad)")
    dist_trad = combined_trad[combined_trad["Phase"] == "Distribution"]
    wd_data = dist_trad[["Age", "Withdrawal_PreTax", "Withdrawal_Taxable"]].melt(
        "Age", var_name="Source", value_name="Amount"
    )
    st.altair_chart(
        create_withdrawal_composition_chart(wd_data), use_container_width=True
    )

    st.subheader("🏛️ Accumulated Taxes Paid")
    # Use Total_Tax from the dataframe which is now consistent
    full_tax_401k = combined_trad[["Age", "Total_Tax"]].copy()
    full_tax_401k["Cumulative_Tax"] = full_tax_401k["Total_Tax"].cumsum()
    full_tax_401k["Strategy"] = "Traditional 401k"

    full_tax_roth = combined_roth[["Age", "Total_Tax"]].copy()
    full_tax_roth["Cumulative_Tax"] = full_tax_roth["Total_Tax"].cumsum()
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

tab1, tab2, tab3 = st.tabs(
    ["Traditional 401k Data", "Roth 401k Data", "Split Strategy Data"]
)

with tab1:
    st.dataframe(combined_trad, hide_index=True)

with tab2:
    st.dataframe(combined_roth, hide_index=True)

with tab3:
    st.dataframe(combined_split, hide_index=True)
