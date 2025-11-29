import pandas as pd
import pytest
from app.charts import (
    create_gross_income_chart,
    create_total_taxes_chart,
    create_net_wealth_chart,
    create_total_balance_chart,
    create_cashflow_chart,
    create_tax_rate_chart,
    create_inflow_outflow_chart,
)


@pytest.fixture
def chart_data():
    return pd.DataFrame(
        {
            "Age": [30, 31, 32],
            "Strategy": ["Trad", "Trad", "Trad"],
            "Cumulative_Gross_Income": [100000, 200000, 300000],
            "Cumulative_Total_Tax": [20000, 40000, 60000],
            "Cumulative_Net_Income": [80000, 160000, 240000],
            "Total_Balance": [10000, 25000, 45000],
            "Net_Income": [80000, 80000, 80000],
            "Effective_Tax_Rate": [0.2, 0.2, 0.2],
            "Marginal_Tax_Rate": [0.25, 0.25, 0.25],
            "Amount": [10000, 10000, 10000],  # For flow chart
            "Flow_Type": ["Contribution", "Contribution", "Contribution"],
        }
    )


def test_create_gross_income_chart(chart_data):
    chart = create_gross_income_chart(chart_data)
    assert chart.mark == "line"
    assert chart.encoding.x.shorthand == "Age"
    assert chart.encoding.y.shorthand == "Cumulative_Gross_Income"


def test_create_total_taxes_chart(chart_data):
    chart = create_total_taxes_chart(chart_data)
    assert chart.mark == "line"
    assert chart.encoding.y.shorthand == "Cumulative_Total_Tax"


def test_create_net_wealth_chart(chart_data):
    chart = create_net_wealth_chart(chart_data)
    assert chart.mark == "line"
    assert chart.encoding.y.shorthand == "Cumulative_Net_Income"


def test_create_total_balance_chart(chart_data):
    chart = create_total_balance_chart(chart_data)
    assert chart.mark == "line"
    assert chart.encoding.y.shorthand == "Total_Balance"


def test_create_cashflow_chart(chart_data):
    chart = create_cashflow_chart(chart_data)
    assert chart.mark == "line"
    assert chart.encoding.y.shorthand == "Net_Income"


def test_create_tax_rate_chart(chart_data):
    chart = create_tax_rate_chart(chart_data)
    # Layered chart
    assert hasattr(chart, "layer")
    assert len(chart.layer) == 2


def test_create_inflow_outflow_chart(chart_data):
    chart = create_inflow_outflow_chart(chart_data)
    assert chart.mark == "line"
    assert chart.encoding.y.shorthand == "Amount"
    assert chart.encoding.strokeDash.shorthand == "Flow_Type"
