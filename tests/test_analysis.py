from app.analysis import (
    calculate_federal_tax,
    calculate_marginal_tax_rate,
    get_contribution_limit,
    run_full_simulation,
    simulate_accumulation_strategy,
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
    # 2025 Base
    limits_2025 = get_contribution_limit(30, 2025)
    assert limits_2025["base"] == 23500
    assert limits_2025["catchup"] == 0

    # 2026 Base (Fixed at 24500)
    limits_2026 = get_contribution_limit(30, 2026)
    assert limits_2026["base"] == 24500

    # Test Inflation on 2027
    # 2026 Base = 24500
    # Inflation 4%
    # 24500 * 1.04 = 25480 -> Rounds to 25500
    limits_2027 = get_contribution_limit(30, 2027, inflation_rate=0.04)
    assert limits_2027["base"] == 25500

    # Catch-up Age 50
    limits_50_2025 = get_contribution_limit(50, 2025)
    assert limits_50_2025["catchup"] == 7500

    limits_50_2026 = get_contribution_limit(50, 2026)
    assert limits_50_2026["catchup"] == 8000

    # Catch-up Age 60-63
    limits_60 = get_contribution_limit(60, 2025)
    assert limits_60["catchup"] == 11250

    limits_63 = get_contribution_limit(63, 2025)
    assert limits_63["catchup"] == 11250

    limits_64 = get_contribution_limit(64, 2025)
    assert limits_64["catchup"] == 7500


def test_high_income_catchup_mandate():
    # High income earner (>150k)
    # Age 60 (eligible for 11250 catchup)
    # Strategy: 100% Traditional (roth_split=0.0)
    # Max contribution

    # Base 23500 + Catchup 11250 = 34750
    # Base goes to Trad (23500)
    # Catchup MUST go to Roth (11250)

    res = simulate_accumulation_strategy(
        annual_income=200000,
        current_age=60,
        years=1,
        return_rate=0.0,
        contribution_input=1.0,  # Max
        use_max_contribution=True,
        match_percent=0.0,
        match_limit=0.0,
        invest_tax_savings_percent=0.0,
        annual_raise=0.0,
        inflation_rate=0.0,
        capital_gains_rate=0.15,
        roth_split=0.0,  # Traditional Strategy
    )

    row = res.iloc[0]
    assert row["Balance_PreTax"] == 23500
    assert row["Balance_Roth"] == 11250  # Forced Roth catchup


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


def test_retirement_income_impact():
    # Run with 0 retirement income
    res_0 = run_full_simulation(
        annual_income=100000,
        current_age=50,
        retirement_age=60,
        final_age=70,
        accumulation_return=0.05,
        retirement_return=0.05,
        contribution_input=1.0,
        use_max_contribution=True,
        employer_match_percent=0.0,
        employer_match_limit=0.0,
        retirement_income=0.0,
    )

    # Run with 50k retirement income
    res_50k = run_full_simulation(
        annual_income=100000,
        current_age=50,
        retirement_age=60,
        final_age=70,
        accumulation_return=0.05,
        retirement_return=0.05,
        contribution_input=1.0,
        use_max_contribution=True,
        employer_match_percent=0.0,
        employer_match_limit=0.0,
        retirement_income=50000.0,
    )

    # Check Traditional Strategy (Taxable withdrawals)
    dist_0 = res_0["distribution_401k"]
    dist_50k = res_50k["distribution_401k"]

    # Tax should be higher with extra income
    assert dist_50k["Federal_Income_Tax"].sum() > dist_0["Federal_Income_Tax"].sum()

    # Net Income should be higher overall because we added 50k/yr
    assert dist_50k["Net_Income"].mean() > dist_0["Net_Income"].mean()

    # Effective Tax Rate on withdrawals + income should be higher (progressive tax)
    # Note: Effective Tax Rate logic in analysis.py is Total Tax / Gross Income
    assert dist_50k["Effective_Tax_Rate"].mean() > dist_0["Effective_Tax_Rate"].mean()


def test_invest_tax_savings_percentage():
    # Run with 100% investment
    results_100 = run_full_simulation(
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
        invest_tax_savings_percent=1.0,
        annual_raise_percent=0.0,
    )

    # Run with 50% investment
    results_50 = run_full_simulation(
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
        invest_tax_savings_percent=0.5,
        annual_raise_percent=0.0,
    )

    # Run with 0% investment
    results_0 = run_full_simulation(
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
        invest_tax_savings_percent=0.0,
        annual_raise_percent=0.0,
    )

    bal_100 = results_100["accumulation_401k"].iloc[-1]["Total_Balance"]
    bal_50 = results_50["accumulation_401k"].iloc[-1]["Total_Balance"]
    bal_0 = results_0["accumulation_401k"].iloc[-1]["Total_Balance"]

    # 100% > 50% > 0%
    assert bal_100 > bal_50 > bal_0

    # Taxable balance check
    taxable_100 = results_100["accumulation_401k"].iloc[-1]["Balance_Taxable"]
    taxable_50 = results_50["accumulation_401k"].iloc[-1]["Balance_Taxable"]
    taxable_0 = results_0["accumulation_401k"].iloc[-1]["Balance_Taxable"]

    assert taxable_100 > taxable_50 > taxable_0
    assert taxable_0 == 0
    # 50% should be roughly half of 100% (ignoring compounding differences slightly, but roughly)
    # Actually, compounding makes it not exactly half, but it should be significant.
    assert taxable_50 > 0


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
        invest_tax_savings_percent=1.0,
        annual_raise_percent=0.0,
    )

    acc_401k = results["accumulation_401k"]
    print("\nDEBUG: Head of acc_401k:")
    print(acc_401k[["Age", "Balance_PreTax", "Balance_Taxable"]].head())

    # Check that PreTax balance is growing
    assert acc_401k.iloc[0]["Balance_PreTax"] > 0
    assert acc_401k.iloc[-1]["Balance_PreTax"] > 0

    # Check for new tax columns
    assert "Marginal_Tax_Rate" in acc_401k.columns
    assert "Effective_Tax_Rate" in acc_401k.columns
    assert "Federal_Income_Tax" in acc_401k.columns
    assert "Tax_On_Brokerage_Gains" in acc_401k.columns
    assert "Gross_Income" in acc_401k.columns
    assert "Total_Tax" in acc_401k.columns

    # Verify values are reasonable
    assert 0 <= acc_401k.iloc[0]["Marginal_Tax_Rate"] <= 1.0
    assert 0 <= acc_401k.iloc[0]["Effective_Tax_Rate"] <= 1.0
    assert acc_401k.iloc[0]["Federal_Income_Tax"] > 0


def test_combine_simulation_results():
    from app.analysis import combine_simulation_results
    import pandas as pd

    acc_df = pd.DataFrame({"Year": [0, 1], "Age": [30, 31], "Balance": [100, 200]})
    dist_df = pd.DataFrame({"Year": [0, 1], "Age": [32, 33], "Balance": [150, 100]})

    combined = combine_simulation_results(acc_df, dist_df)

    assert len(combined) == 4
    assert "Phase" in combined.columns
    assert combined.iloc[0]["Phase"] == "Accumulation"
    assert combined.iloc[2]["Phase"] == "Distribution"
    # Check Year continuity
    assert combined.iloc[2]["Year"] == 2
    assert combined.iloc[3]["Year"] == 3
    # Check Age
    assert combined.iloc[2]["Age"] == 32


def test_split_strategy():
    from app.analysis import simulate_accumulation_strategy

    # Test 50/50 Split
    df = simulate_accumulation_strategy(
        annual_income=100000,
        current_age=30,
        years=1,
        return_rate=0.0,
        contribution_input=10000,
        use_max_contribution=False,
        match_percent=0.0,
        match_limit=0.0,
        invest_tax_savings_percent=0.0,
        annual_raise=0.0,
        inflation_rate=0.0,
        capital_gains_rate=0.15,
        roth_split=0.5,
    )

    row = df.iloc[0]
    # Total Contribution should be 10000
    assert row["Contribution"] == 10000
    # PreTax Balance should be 5000 (50%)
    assert row["Balance_PreTax"] == 5000
    # Roth Balance should be 5000 (50%)
    assert row["Balance_Roth"] == 5000
    # Taxable Income should be reduced by 5000 (Trad portion)
    # Gross Income 100k - 5k = 95k
    # We can't check taxable income directly as it's internal, but we can check Federal Tax
    # But Federal Tax depends on brackets.
    # Let's check Total Balance
    assert row["Total_Balance"] == 10000

    # Test 100% Roth
    df_roth = simulate_accumulation_strategy(
        annual_income=100000,
        current_age=30,
        years=1,
        return_rate=0.0,
        contribution_input=10000,
        use_max_contribution=False,
        match_percent=0.0,
        match_limit=0.0,
        invest_tax_savings_percent=0.0,
        annual_raise=0.0,
        inflation_rate=0.0,
        capital_gains_rate=0.15,
        roth_split=1.0,
    )
    row_roth = df_roth.iloc[0]
    assert row_roth["Balance_PreTax"] == 0
    assert row_roth["Balance_Roth"] == 10000

    # Test 100% Trad
    df_trad = simulate_accumulation_strategy(
        annual_income=100000,
        current_age=30,
        years=1,
        return_rate=0.0,
        contribution_input=10000,
        use_max_contribution=False,
        match_percent=0.0,
        match_limit=0.0,
        invest_tax_savings_percent=0.0,
        annual_raise=0.0,
        inflation_rate=0.0,
        capital_gains_rate=0.15,
        roth_split=0.0,
    )
    row_trad = df_trad.iloc[0]
    assert row_trad["Balance_PreTax"] == 10000
    assert row_trad["Balance_Roth"] == 0
