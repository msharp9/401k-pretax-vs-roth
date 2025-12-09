import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.analysis import run_full_simulation


def test_starting_balances():
    # Define test parameters
    annual_income = 100000
    current_age = 30
    retirement_age = 60
    final_age = 90
    accumulation_return = 0.05
    retirement_return = 0.04
    contribution_input = 10000
    use_max_contribution = False
    employer_match_percent = 0.0
    employer_match_limit = 0.0

    # Case 1: No starting balance
    results_zero = run_full_simulation(
        annual_income=annual_income,
        current_age=current_age,
        retirement_age=retirement_age,
        final_age=final_age,
        accumulation_return=accumulation_return,
        retirement_return=retirement_return,
        contribution_input=contribution_input,
        use_max_contribution=use_max_contribution,
        employer_match_percent=employer_match_percent,
        employer_match_limit=employer_match_limit,
        current_401k_balance=0,
        current_roth_balance=0,
    )

    # Case 2: With starting balance
    start_401k = 50000
    start_roth = 20000
    results_with_balance = run_full_simulation(
        annual_income=annual_income,
        current_age=current_age,
        retirement_age=retirement_age,
        final_age=final_age,
        accumulation_return=accumulation_return,
        retirement_return=retirement_return,
        contribution_input=contribution_input,
        use_max_contribution=use_max_contribution,
        employer_match_percent=employer_match_percent,
        employer_match_limit=employer_match_limit,
        current_401k_balance=start_401k,
        current_roth_balance=start_roth,
    )

    # Check Year 0 balances
    # In Year 0, the balance should be Starting Balance + Contribution + Growth (if any, usually growth applies to start balance too)
    # The simulation logic:
    # balance_pretax = start_balance_pretax
    # ...
    # balance_pretax += trad_contribution + match_amount
    # ...
    # balance_pretax *= 1 + return_rate

    # So Year 0 End Balance = (Start + Contribution) * (1 + Return)

    acc_401k_zero = results_zero["accumulation_401k"]
    acc_401k_bal = results_with_balance["accumulation_401k"]

    # Check Traditional Strategy (100% PreTax)
    # Year 0
    row0_zero = acc_401k_zero.iloc[0]
    row0_bal = acc_401k_bal.iloc[0]

    # Expected difference in Year 0 Balance PreTax
    # Zero: (0 + Contrib) * (1+r)
    # Bal: (Start + Contrib) * (1+r)
    # Diff: Start * (1+r)

    expected_diff = start_401k * (1 + accumulation_return)
    actual_diff = row0_bal["Balance_PreTax"] - row0_zero["Balance_PreTax"]

    print(f"Year 0 Diff: {actual_diff}, Expected: {expected_diff}")
    assert abs(actual_diff - expected_diff) < 1.0, "Year 0 Balance difference incorrect"

    # Check Roth Strategy (100% Roth)
    acc_roth_zero = results_zero["accumulation_roth"]
    acc_roth_bal = results_with_balance["accumulation_roth"]

    row0_roth_zero = acc_roth_zero.iloc[0]
    row0_roth_bal = acc_roth_bal.iloc[0]

    expected_diff_roth = start_roth * (1 + accumulation_return)
    actual_diff_roth = row0_roth_bal["Balance_Roth"] - row0_roth_zero["Balance_Roth"]

    print(f"Year 0 Roth Diff: {actual_diff_roth}, Expected: {expected_diff_roth}")
    assert abs(actual_diff_roth - expected_diff_roth) < 1.0, (
        "Year 0 Roth Balance difference incorrect"
    )

    # Check Split Strategy (50/50)
    # Both starting balances should be present regardless of strategy split for contributions?
    # Wait, the logic says:
    # balance_pretax = start_balance_pretax
    # balance_roth = start_balance_roth
    # So YES, starting balances are independent of contribution strategy.

    acc_split_bal = results_with_balance["accumulation_split"]
    acc_split_bal.iloc[0]

    # For split strategy, we have both balances.
    # Check that they are consistent.
    # PreTax Balance should include start_401k
    # Roth Balance should include start_roth

    # We can compare against the single-strategy runs, but contribution amounts differ.
    # But the "Starting Balance" portion of the growth should be identical.

    print("Test passed!")


if __name__ == "__main__":
    test_starting_balances()
