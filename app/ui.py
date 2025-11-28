import streamlit as st
from app.analysis import (
    DEFAULT_INCOME,
    DEFAULT_ACCUMULATION_RETURN,
    DEFAULT_RETIREMENT_RETURN,
    DEFAULT_START_AGE,
    DEFAULT_RETIREMENT_AGE,
    DEFAULT_FINAL_AGE,
)


def render_sidebar():
    """
    Renders the sidebar inputs and returns the configuration dictionary.
    """
    st.sidebar.header("📝 Assumptions")

    # Personal Info
    st.sidebar.subheader("Personal Details")
    current_age = st.sidebar.number_input(
        "Current Age", min_value=18, max_value=70, value=DEFAULT_START_AGE
    )
    retirement_age = st.sidebar.number_input(
        "Retirement Age", min_value=50, max_value=80, value=DEFAULT_RETIREMENT_AGE
    )
    final_age = st.sidebar.number_input(
        "Life Expectancy", min_value=70, max_value=110, value=DEFAULT_FINAL_AGE
    )

    # Income & Contributions
    st.sidebar.subheader("Income & Contributions")
    annual_income = st.sidebar.number_input(
        "Annual Income ($)", min_value=30000, value=DEFAULT_INCOME, step=5000
    )
    annual_raise = st.sidebar.slider("Annual Raise (%)", 0.0, 10.0, 2.0, 0.1) / 100.0

    contribution_mode = st.sidebar.radio(
        "Contribution Amount",
        ["Max Out Limits", "Custom Amount", "Percentage of Income"],
    )

    use_max_contribution = False
    contribution_input = 0.0

    if contribution_mode == "Max Out Limits":
        use_max_contribution = True
    elif contribution_mode == "Custom Amount":
        contribution_input = st.sidebar.number_input(
            "Annual Contribution ($)", min_value=0, value=23000, step=1000
        )
    else:
        pct = st.sidebar.slider("Contribution %", 0, 50, 10)
        contribution_input = pct / 100.0

    # Employer Match
    st.sidebar.subheader("Employer Match")
    match_percent = st.sidebar.slider(
        "Employer Match % (on contribution)",
        0,
        100,
        0,
        help="Employer matches X% of your contribution...",
    )
    match_limit = st.sidebar.slider(
        "Match Limit % (of salary)", 0, 20, 0, help="...up to Y% of your salary."
    )

    # Strategy Settings
    st.sidebar.subheader("Strategy Settings")
    invest_tax_savings = st.sidebar.checkbox(
        "Invest Tax Savings?",
        value=True,
        help="If checked, the tax savings from Traditional 401k contributions are invested in a taxable brokerage account. If unchecked, they are assumed to be spent.",
    )

    roth_split = st.sidebar.slider(
        "Split Strategy: Roth %",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
        help="Percentage of contributions to go to Roth 401k for the 'Split' strategy.",
    )

    # Investment Returns
    st.sidebar.subheader("Investment Returns")
    accumulation_return = (
        st.sidebar.slider(
            "Return During Working Years (%)",
            0.0,
            15.0,
            DEFAULT_ACCUMULATION_RETURN * 100,
            0.1,
        )
        / 100.0
    )
    retirement_return = (
        st.sidebar.slider(
            "Return During Retirement (%)",
            0.0,
            10.0,
            DEFAULT_RETIREMENT_RETURN * 100,
            0.1,
        )
        / 100.0
    )

    return {
        "current_age": current_age,
        "retirement_age": retirement_age,
        "final_age": final_age,
        "annual_income": annual_income,
        "annual_raise": annual_raise,
        "contribution_input": contribution_input,
        "use_max_contribution": use_max_contribution,
        "match_percent": match_percent,
        "match_limit": match_limit,
        "invest_tax_savings": invest_tax_savings,
        "accumulation_return": accumulation_return,
        "retirement_return": retirement_return,
        "roth_split_percent": roth_split / 100.0,
    }


def render_summary_metrics(
    acc_401k, acc_roth, dist_401k, dist_roth, retirement_age, invest_tax_savings
):
    """
    Renders the executive summary metrics.
    """
    st.header("📊 Executive Summary")

    col1, col2, col3 = st.columns(3)

    # 401k Metrics
    with col1:
        st.subheader("Traditional 401k Strategy")
        final_acc_bal_401k = acc_401k.iloc[-1]["Total_Balance"]
        st.metric(
            "Peak Wealth (Age {})".format(retirement_age), f"${final_acc_bal_401k:,.0f}"
        )

        avg_net_income_401k = dist_401k["Net_Income"].mean()
        st.metric("Avg Annual Net Income (Retirement)", f"${avg_net_income_401k:,.0f}")

        total_tax_401k = dist_401k["Total_Tax"].sum()
        st.metric("Total Taxes Paid (Retirement)", f"${total_tax_401k:,.0f}")

    # Roth Metrics
    with col2:
        st.subheader("Roth 401k Strategy")
        final_acc_bal_roth = acc_roth.iloc[-1]["Total_Balance"]
        delta_bal = final_acc_bal_roth - final_acc_bal_401k
        st.metric(
            "Peak Wealth (Age {})".format(retirement_age),
            f"${final_acc_bal_roth:,.0f}",
            delta=f"{delta_bal:,.0f}",
        )

        avg_net_income_roth = dist_roth["Net_Income"].mean()
        delta_inc = avg_net_income_roth - avg_net_income_401k
        st.metric(
            "Avg Annual Net Income (Retirement)",
            f"${avg_net_income_roth:,.0f}",
            delta=f"{delta_inc:,.0f}",
        )

        total_tax_roth = dist_roth["Total_Tax"].sum()
        st.metric("Total Taxes Paid (Retirement)", f"${total_tax_roth:,.0f}")

    # Analysis
    with col3:
        st.subheader("Analysis")
        if avg_net_income_roth > avg_net_income_401k:
            st.success(
                f"**Roth Wins!** You get **${delta_inc:,.0f}** more per year in retirement."
            )
        else:
            st.success(
                f"**Traditional Wins!** You get **${-delta_inc:,.0f}** more per year in retirement."
            )

        if invest_tax_savings:
            st.info(
                "This assumes you invest the tax savings from the Traditional 401k into a taxable brokerage account."
            )
        else:
            st.warning(
                "You are NOT investing the tax savings from the Traditional 401k. This significantly penalizes the Traditional strategy."
            )
