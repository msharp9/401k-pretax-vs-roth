import altair as alt
import pandas as pd


def create_gross_income_chart(data: pd.DataFrame) -> alt.Chart:
    """
    1. Gross Dollars Earned (Wealth Accumulation): Cumulative Gross Income over time.
    """
    return (
        alt.Chart(data)
        .mark_line()
        .encode(
            x="Age",
            y=alt.Y(
                "Cumulative_Gross_Income",
                axis=alt.Axis(format="$,.0f"),
                title="Cumulative Gross Income",
            ),
            color="Strategy",
            tooltip=[
                "Age",
                "Strategy",
                alt.Tooltip("Cumulative_Gross_Income", format="$,.0f"),
            ],
        )
        .properties(height=300, title="Gross Dollars Earned (Cumulative)")
        .interactive()
    )


def create_total_taxes_chart(data: pd.DataFrame) -> alt.Chart:
    """
    2. Total Taxes Paid: Cumulative Total Tax over time.
    """
    return (
        alt.Chart(data)
        .mark_line()
        .encode(
            x="Age",
            y=alt.Y(
                "Cumulative_Total_Tax",
                axis=alt.Axis(format="$,.0f"),
                title="Cumulative Taxes Paid",
            ),
            color="Strategy",
            tooltip=[
                "Age",
                "Strategy",
                alt.Tooltip("Cumulative_Total_Tax", format="$,.0f"),
            ],
        )
        .properties(height=300, title="Total Taxes Paid (Cumulative)")
        .interactive()
    )


def create_net_wealth_chart(data: pd.DataFrame) -> alt.Chart:
    """
    3. Net Wealth Accumulation: Cumulative Net Income (After-Tax) over time.
    """
    return (
        alt.Chart(data)
        .mark_line()
        .encode(
            x="Age",
            y=alt.Y(
                "Cumulative_Net_Income",
                axis=alt.Axis(format="$,.0f"),
                title="Cumulative Net Income",
            ),
            color="Strategy",
            tooltip=[
                "Age",
                "Strategy",
                alt.Tooltip("Cumulative_Net_Income", format="$,.0f"),
            ],
        )
        .properties(
            height=300, title="Net Wealth Accumulation (Cumulative After-Tax Income)"
        )
        .interactive()
    )


def create_total_balance_chart(data: pd.DataFrame) -> alt.Chart:
    """
    4. Total Balance: Total Account Balance (Sum of all accounts) over time.
    """
    return (
        alt.Chart(data)
        .mark_line()
        .encode(
            x="Age",
            y=alt.Y(
                "Total_Balance", axis=alt.Axis(format="$,.0f"), title="Total Balance"
            ),
            color="Strategy",
            tooltip=["Age", "Strategy", alt.Tooltip("Total_Balance", format="$,.0f")],
        )
        .properties(height=300, title="Total Account Balance")
        .interactive()
    )


def create_cashflow_chart(data: pd.DataFrame) -> alt.Chart:
    """
    5. Cashflow: Annual Net Spendable Income over time.
    """
    return (
        alt.Chart(data)
        .mark_line()
        .encode(
            x="Age",
            y=alt.Y(
                "Net_Income", axis=alt.Axis(format="$,.0f"), title="Annual Net Income"
            ),
            color="Strategy",
            tooltip=["Age", "Strategy", alt.Tooltip("Net_Income", format="$,.0f")],
        )
        .properties(height=300, title="Annual Cashflow (Net Spendable Income)")
        .interactive()
    )


def create_tax_rate_chart(data: pd.DataFrame) -> alt.Chart:
    """
    6. Tax Rates: Marginal and Effective Tax Rates over time.
    """
    base = alt.Chart(data).encode(x="Age")

    effective = base.mark_line().encode(
        y=alt.Y("Effective_Tax_Rate", axis=alt.Axis(format="%"), title="Tax Rate"),
        color="Strategy",
        strokeDash=alt.value([1, 0]),  # Solid line
        tooltip=["Age", "Strategy", alt.Tooltip("Effective_Tax_Rate", format=".2%")],
    )

    # We might want to show Marginal Rate too, but it might get crowded if we show both for all strategies.
    # Let's just show Effective Tax Rate as primary request, maybe add Marginal as dashed?
    # User asked for "Tax Rate and Effective Tax rate".
    # Let's assume "Tax Rate" means Marginal.

    marginal = base.mark_line(strokeDash=[5, 5]).encode(
        y="Marginal_Tax_Rate",
        color="Strategy",
        tooltip=["Age", "Strategy", alt.Tooltip("Marginal_Tax_Rate", format=".2%")],
    )

    return (
        (effective + marginal)
        .properties(height=300, title="Tax Rates (Solid: Effective, Dashed: Marginal)")
        .interactive()
    )


def create_inflow_outflow_chart(data: pd.DataFrame) -> alt.Chart:
    """
    7. Contributions and Withdrawals overtime for each strategy.
    """
    # We need to melt the data to show both Contributions and Withdrawals
    # But the input data here is likely the combined dataframe with columns "Contribution" and "Gross_Withdrawal"
    # We should probably do the melting inside the main app or pass a melted dataframe.
    # Let's assume we pass a melted dataframe with "Flow_Type" and "Amount".

    return (
        alt.Chart(data)
        .mark_line()
        .encode(
            x="Age",
            y=alt.Y("Amount", axis=alt.Axis(format="$,.0f")),
            color="Strategy",
            strokeDash="Flow_Type",  # Contribution vs Withdrawal
            tooltip=[
                "Age",
                "Strategy",
                "Flow_Type",
                alt.Tooltip("Amount", format="$,.0f"),
            ],
        )
        .properties(height=300, title="Contributions (In) vs Withdrawals (Out)")
        .interactive()
    )
