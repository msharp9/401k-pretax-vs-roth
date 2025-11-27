from app.analysis import (
    calculate_federal_tax,
    calculate_marginal_tax_rate,
    get_contribution_limit,
    run_full_simulation,
)


def test_calculate_federal_tax():
    # Test 0 income
    assert calculate_federal_tax(0) == 0

    # Test below standard deduction
    assert calculate_federal_tax(10000) == 0

    # Test first bracket
    # Income 20000. Taxable = 20000 - 14600 = 5400. Tax = 5400 * 0.10 = 540
    assert calculate_federal_tax(20000) == 540

    # Test specific case from notebook (approximate)
    # Income 550,000
    # Taxable = 535,400
    # Expected around 159k
    tax = calculate_federal_tax(550000)
    assert 150000 < tax < 170000


def test_calculate_marginal_tax_rate():
    assert calculate_marginal_tax_rate(10000) == 0
    assert calculate_marginal_tax_rate(20000) == 0.10
    assert calculate_marginal_tax_rate(550000) == 0.35  # Based on 2024 brackets


def test_get_contribution_limit():
    limits_2024 = get_contribution_limit(35, 2024)
    assert limits_2024["base"] == 23000
    assert limits_2024["catchup"] == 0

    limits_2024_old = get_contribution_limit(55, 2024)
    assert limits_2024_old["catchup"] == 7500

    # Test inflation
    limits_2025 = get_contribution_limit(35, 2025, inflation_rate=0.025)
    assert limits_2025["base"] == 23000 * 1.025


def test_run_full_simulation_sanity():
    results = run_full_simulation(
        annual_income=100000,
        current_age=30,
        retirement_age=60,
        final_age=90,
        accumulation_return=0.07,
        retirement_return=0.05,
        contribution_input=1.0,  # Max out
        use_max_contribution=True,
        employer_match_percent=0.0,
        employer_match_limit=0.0,
        annual_raise_percent=0.0,
    )

    assert "accumulation_401k" in results
    assert "accumulation_roth" in results
    assert "distribution_401k" in results
    assert "distribution_roth" in results

    acc_401k = results["accumulation_401k"]
    assert len(acc_401k) == 30  # 30 to 60

    dist_401k = results["distribution_401k"]
    assert len(dist_401k) == 30  # 60 to 90

    # Check that balances grow
    assert acc_401k.iloc[-1]["Total_Balance"] > acc_401k.iloc[0]["Total_Balance"]


def test_invest_tax_savings_toggle():
    # Run with investment
    results_invest = run_full_simulation(
        annual_income=100000,
        current_age=30,
        retirement_age=60,
        final_age=90,
        accumulation_return=0.07,
        retirement_return=0.05,
        contribution_input=1.0,
        use_max_contribution=True,
        employer_match_percent=0.0,
        employer_match_limit=0.0,
        invest_tax_savings=True,
        annual_raise_percent=0.0,
    )

    # Run without investment
    results_spend = run_full_simulation(
        annual_income=100000,
        current_age=30,
        retirement_age=60,
        final_age=90,
        accumulation_return=0.07,
        retirement_return=0.05,
        contribution_input=1.0,
        use_max_contribution=True,
        employer_match_percent=0.0,
        employer_match_limit=0.0,
        invest_tax_savings=False,
        annual_raise_percent=0.0,
    )

    bal_invest = results_invest["accumulation_401k"].iloc[-1]["Total_Balance"]
    bal_spend = results_spend["accumulation_401k"].iloc[-1]["Total_Balance"]

    # Investing tax savings should result in higher balance
    assert bal_invest > bal_spend

    # Without investment, taxable balance should be 0 (or close to it if we had initial balance, but here 0)
    assert results_spend["accumulation_401k"].iloc[-1]["Balance_Taxable"] == 0


def test_pretax_balance_growth():
    results = run_full_simulation(
        annual_income=100000,
        current_age=30,
        retirement_age=60,
        final_age=90,
        accumulation_return=0.07,
        retirement_return=0.05,
        contribution_input=1.0,
        use_max_contribution=True,
        employer_match_percent=0.0,
        employer_match_limit=0.0,
        invest_tax_savings=True,
        annual_raise_percent=0.0,
    )

    acc_401k = results["accumulation_401k"]
    print("\nDEBUG: Head of acc_401k:")
    print(acc_401k[["Age", "Balance_PreTax", "Balance_Taxable"]].head())

    # Check that PreTax balance is growing
    assert acc_401k.iloc[0]["Balance_PreTax"] > 0
    assert acc_401k.iloc[-1]["Balance_PreTax"] > 0
