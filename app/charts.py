import altair as alt
import pandas as pd


def create_hero_chart(all_data: pd.DataFrame) -> alt.Chart:
    """
    Creates the unified timeline chart showing balances for all accounts.
    """
    return (
        alt.Chart(all_data)
        .mark_line()
        .encode(
            x="Age",
            y=alt.Y("Balance", axis=alt.Axis(format="$,.0f")),
            color="Account",
            strokeDash="Strategy",
            tooltip=[
                "Age",
                "Strategy",
                "Account",
                alt.Tooltip("Balance", format="$,.0f"),
            ],
        )
        .interactive()
    )


def create_wealth_composition_chart(
    data: pd.DataFrame, strategy_name: str
) -> alt.Chart:
    """
    Creates a stacked area chart for wealth composition.
    """
    return (
        alt.Chart(data)
        .mark_area()
        .encode(
            x="Age",
            y=alt.Y("Balance", stack=True, axis=alt.Axis(format="$,.0f")),
            color="Account",
            tooltip=["Age", "Account", alt.Tooltip("Balance", format="$,.0f")],
        )
        .properties(height=300, title=f"Wealth Composition ({strategy_name})")
    )


def create_cashflow_chart(data: pd.DataFrame) -> alt.Chart:
    """
    Creates a bar chart for net spendable income.
    """
    return (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x="Age",
            y=alt.Y(
                "Net_Liquidity", axis=alt.Axis(format="$,.0f"), title="Net Spendable"
            ),
            tooltip=[alt.Tooltip("Net_Liquidity", format="$,.0f")],
        )
        .properties(height=300, title="Net Spendable Income")
    )


def create_contributions_chart(data: pd.DataFrame) -> alt.Chart:
    """
    Creates a stacked bar chart for contributions.
    """
    return (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x="Age",
            y=alt.Y("Amount", stack=True, axis=alt.Axis(format="$,.0f")),
            color="Type",
            tooltip=["Age", "Type", alt.Tooltip("Amount", format="$,.0f")],
        )
        .properties(height=300, title="Annual Contributions")
    )


def create_effective_tax_rate_chart(data: pd.DataFrame) -> alt.Chart:
    """
    Creates a line chart for effective tax rate.
    """
    return (
        alt.Chart(data)
        .mark_line()
        .encode(
            x="Age",
            y=alt.Y("Rate", axis=alt.Axis(format="%")),
            color="Strategy",
            tooltip=["Age", "Strategy", alt.Tooltip("Rate", format=".2%")],
        )
        .properties(height=300, title="Effective Tax Rate")
    )


def create_net_income_comparison_chart(data: pd.DataFrame) -> alt.Chart:
    """
    Creates a line chart comparing net income.
    """
    return (
        alt.Chart(data)
        .mark_line()
        .encode(
            x="Age",
            y=alt.Y("Income", axis=alt.Axis(format="$,.0f")),
            color="Strategy",
            tooltip=["Age", "Strategy", alt.Tooltip("Income", format="$,.0f")],
        )
        .properties(height=300, title="Net Income Comparison")
    )


def create_withdrawal_composition_chart(data: pd.DataFrame) -> alt.Chart:
    """
    Creates a stacked bar chart for withdrawal sources.
    """
    return (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x="Age",
            y=alt.Y("Amount", stack=True, axis=alt.Axis(format="$,.0f")),
            color="Source",
            tooltip=["Age", "Source", alt.Tooltip("Amount", format="$,.0f")],
        )
        .properties(height=300, title="Withdrawal Composition")
    )


def create_accumulated_taxes_chart(data: pd.DataFrame) -> alt.Chart:
    """
    Creates a line chart for accumulated taxes.
    """
    return (
        alt.Chart(data)
        .mark_line()
        .encode(
            x="Age",
            y=alt.Y("Cumulative_Tax", axis=alt.Axis(format="$,.0f")),
            color="Strategy",
            tooltip=["Age", "Strategy", alt.Tooltip("Cumulative_Tax", format="$,.0f")],
        )
        .properties(height=300, title="Accumulated Taxes Paid")
    )


def create_cumulative_advantage_chart(data: pd.DataFrame) -> alt.Chart:
    """
    Creates an area chart for cumulative advantage.
    """
    return (
        alt.Chart(data)
        .mark_area(
            line={"color": "darkgreen"},
            color=alt.Gradient(
                gradient="linear",
                stops=[
                    alt.GradientStop(color="white", offset=0),
                    alt.GradientStop(color="darkgreen", offset=1),
                ],
                x1=1,
                x2=1,
                y1=1,
                y2=0,
            ),
        )
        .encode(
            x="Age",
            y=alt.Y("Cumulative Advantage", axis=alt.Axis(format="$,.0f")),
            tooltip=["Age", alt.Tooltip("Cumulative Advantage", format="$,.0f")],
        )
        .properties(height=300, title="Cumulative Advantage (Trad - Roth)")
    )


def create_net_cashflow_chart(data: pd.DataFrame) -> alt.Chart:
    """
    Creates a bar chart for net cash flow (in/out).
    """
    return (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x="Age",
            y=alt.Y("Amount", axis=alt.Axis(format="$,.0f")),
            color="Strategy",
            column="Strategy",
            tooltip=["Age", "Strategy", alt.Tooltip("Amount", format="$,.0f")],
        )
        .properties(height=300, title="Annual Net Cash Flow")
    )
