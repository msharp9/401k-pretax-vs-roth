import pytest
import pandas as pd
import altair as alt
from app.charts import (
    create_hero_chart,
    create_wealth_composition_chart,
    create_cashflow_chart,
)


@pytest.fixture
def sample_data():
    return pd.DataFrame(
        {
            "Age": [30, 31, 32],
            "Balance": [10000, 20000, 30000],
            "Account": ["PreTax", "PreTax", "PreTax"],
            "Strategy": ["Trad", "Trad", "Trad"],
            "Net_Liquidity": [5000, 5000, 5000],
        }
    )


def test_create_hero_chart(sample_data):
    chart = create_hero_chart(sample_data)
    assert isinstance(chart, alt.Chart)
    # Check encoding
    assert chart.encoding.x.shorthand == "Age"
    assert chart.encoding.y.shorthand == "Balance"


def test_create_wealth_composition_chart(sample_data):
    chart = create_wealth_composition_chart(sample_data, "Test")
    assert isinstance(chart, alt.Chart)
    assert chart.title == "Wealth Composition (Test)"


def test_create_cashflow_chart(sample_data):
    chart = create_cashflow_chart(sample_data)
    assert isinstance(chart, alt.Chart)
    assert chart.encoding.y.shorthand == "Net_Liquidity"
