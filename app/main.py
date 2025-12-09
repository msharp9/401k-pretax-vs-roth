import streamlit as st
import pandas as pd
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.analysis import run_full_simulation, combine_simulation_results
from app.ui import render_sidebar, render_summary_metrics
from app.charts import (
    create_gross_income_chart,
    create_total_taxes_chart,
    create_net_wealth_chart,
    create_total_balance_chart,
    create_cashflow_chart,
    create_tax_rate_chart,
    create_inflow_outflow_chart,
)

# Set page config
st.set_page_config(page_title="401k vs Roth Analysis", page_icon="💰", layout="wide")

st.title("💰 401k vs Roth 401k Analysis")
st.markdown("""
This tool compares the long-term impact of contributing to a **Traditional 401k** (Pre-Tax) vs a **Roth 401k** (After-Tax).
It simulates the accumulation phase (working years) and the distribution phase (retirement years), accounting for taxes, investment growth, and inflation.
""")

with st.expander("Catch-up Contribution Rules"):
    st.markdown("""
    *   Age 50+: Standard catch-up contribution applies (\$7,500 in 2025, \$8,000 in 2026).
    *   Age 60-63: Special catch-up limit applies (\$11,250 in 2025).
    *   High Income Rule: If prior year wages exceed \$150,000 (2025), catch-up contributions must be made to a Roth account.
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
    invest_tax_savings_percent=config["invest_tax_savings_percent"],
    annual_raise_percent=config["annual_raise"],
    retirement_income=config["retirement_income"],
    roth_split_percent=config["roth_split_percent"],
    current_401k_balance=config["current_401k_balance"],
    current_roth_balance=config["current_roth_balance"],
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
    acc_split,
    dist_401k,
    dist_roth,
    dist_split,
    config["retirement_age"],
    config["invest_tax_savings_percent"],
)


# --- Visualizations ---
# --- Data Preparation for Charts ---
# We need to add cumulative columns to the combined dataframes
def prepare_chart_data(df, strategy_name):
    df = df.copy()
    df["Strategy"] = strategy_name
    df["Cumulative_Gross_Income"] = df["Gross_Income"].cumsum()
    df["Cumulative_Total_Tax"] = df["Total_Tax"].cumsum()

    # Net Income in Accumulation = Gross - Tax - Contribution (What you take home)
    # Net Income in Distribution = Net_Income (What you take home)
    # Wait, "Net Wealth Accumulation" usually means "Assets".
    # But user asked for "Net Wealth Accumulation" AND "Total Balance".
    # And "Gross Dollars Earned".
    # So "Net Wealth Accumulation" likely means "Cumulative Net Income".

    # Let's calculate Annual Net Income for Accumulation if not present
    # In accumulation phase of analysis.py, we didn't explicitly save "Net_Income" (spendable).
    # We saved Gross, Contribution, Tax.
    # So Net = Gross - Contribution - Tax.

    def calc_net(row):
        if row["Phase"] == "Accumulation":
            return row["Gross_Income"] - row["Contribution"] - row["Total_Tax"]
        else:
            return row["Net_Income"]

    df["Net_Income"] = df.apply(calc_net, axis=1)
    df["Cumulative_Net_Income"] = df["Net_Income"].cumsum()

    return df


trad_chart_data = prepare_chart_data(combined_trad, "Traditional")
roth_chart_data = prepare_chart_data(combined_roth, "Roth")
split_chart_data = prepare_chart_data(
    combined_split, f"Split ({config['roth_split_percent']:.0%})"
)

all_chart_data = pd.concat([trad_chart_data, roth_chart_data, split_chart_data])

# --- Visualizations ---
st.markdown("---")

# 1. Gross Dollars Earned
st.altair_chart(create_gross_income_chart(all_chart_data), use_container_width=True)

# 2. Total Taxes Paid
st.altair_chart(create_total_taxes_chart(all_chart_data), use_container_width=True)

# 3. Net Wealth Accumulation
st.altair_chart(create_net_wealth_chart(all_chart_data), use_container_width=True)

# 4. Total Balance
st.altair_chart(create_total_balance_chart(all_chart_data), use_container_width=True)

# 5. Cashflow
st.altair_chart(create_cashflow_chart(all_chart_data), use_container_width=True)

# 6. Tax Rates
st.altair_chart(create_tax_rate_chart(all_chart_data), use_container_width=True)

# 7. Contributions and Withdrawals
# Prepare data for this specific chart
# We want lines for Contribution and Gross_Withdrawal
# Melt the data
flow_data = all_chart_data.melt(
    id_vars=["Age", "Strategy"],
    value_vars=["Contribution", "Gross_Withdrawal"],
    var_name="Flow_Type",
    value_name="Amount",
)
st.altair_chart(create_inflow_outflow_chart(flow_data), use_container_width=True)

# --- Additional Metrics ---
st.markdown("---")
st.subheader("📊 Other Key Metrics")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)


# Calculate Investment Earnings
# Earnings = Final Balance + Total Withdrawals - Total Contributions - Total Match
def calculate_earnings(acc_df, dist_df):
    final_balance = dist_df.iloc[-1]["Total_Balance"]
    total_withdrawals = dist_df["Gross_Withdrawal"].sum()
    total_contributions = acc_df["Contribution"].sum()
    total_match = acc_df["Match"].sum()
    return final_balance + total_withdrawals - total_contributions - total_match


trad_earnings = calculate_earnings(acc_401k, dist_401k)
roth_earnings = calculate_earnings(acc_roth, dist_roth)
split_earnings = calculate_earnings(acc_split, dist_split)

with col_m1:
    st.metric("Total Contributions (All)", f"${acc_401k['Contribution'].sum():,.0f}")
    st.metric("Total Match Received (All)", f"${acc_401k['Match'].sum():,.0f}")

with col_m2:
    st.metric("Total Investment Earnings (Trad)", f"${trad_earnings:,.0f}")
    st.metric("Total Investment Earnings (Roth)", f"${roth_earnings:,.0f}")
    st.metric("Total Investment Earnings (Split)", f"${split_earnings:,.0f}")

with col_m3:
    # Use the chart data which has the cumulative columns
    trad_total_tax = trad_chart_data.iloc[-1]["Cumulative_Total_Tax"]
    roth_total_tax = roth_chart_data.iloc[-1]["Cumulative_Total_Tax"]
    split_total_tax = split_chart_data.iloc[-1]["Cumulative_Total_Tax"]

    st.metric("Total Taxes Paid (Trad)", f"${trad_total_tax:,.0f}")
    st.metric("Total Taxes Paid (Roth)", f"${roth_total_tax:,.0f}")
    st.metric("Total Taxes Paid (Split)", f"${split_total_tax:,.0f}")

with col_m4:
    # Lifetime Average Effective Tax Rate
    st.metric(
        "Lifetime Avg Effective Tax Rate (Trad)",
        f"{trad_chart_data['Effective_Tax_Rate'].mean():.2%}",
    )
    st.metric(
        "Lifetime Avg Effective Tax Rate (Roth)",
        f"{roth_chart_data['Effective_Tax_Rate'].mean():.2%}",
    )
    st.metric(
        "Lifetime Avg Effective Tax Rate (Split)",
        f"{split_chart_data['Effective_Tax_Rate'].mean():.2%}",
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
