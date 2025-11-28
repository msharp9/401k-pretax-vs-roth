import pandas as pd
from typing import Dict, List, Tuple

# --- Constants & Defaults ---
# 2024 Federal Tax Brackets (Single Filer)
# (Lower, Upper, Rate)
TAX_BRACKETS_2024 = [
    (0, 11600, 0.10),
    (11600, 47150, 0.12),
    (47150, 100525, 0.22),
    (100525, 191950, 0.24),
    (191950, 243725, 0.32),
    (243725, 609350, 0.35),
    (609350, float("inf"), 0.37),
]

STANDARD_DEDUCTION_2024 = 14600

# Default Assumptions
DEFAULT_INCOME = 550000
DEFAULT_ACCUMULATION_RETURN = 0.07
DEFAULT_RETIREMENT_RETURN = 0.05
DEFAULT_START_AGE = 35
DEFAULT_RETIREMENT_AGE = 65
DEFAULT_FINAL_AGE = 95
DEFAULT_INFLATION_RATE = 0.025
DEFAULT_CAPITAL_GAINS_RATE = 0.15

# Contribution Limits 2024
BASE_CONTRIBUTION_LIMIT_2024 = 23000
CATCHUP_CONTRIBUTION_LIMIT_2024 = 7500
CATCHUP_AGE = 50


def calculate_federal_tax(
    income: float,
    standard_deduction: float = STANDARD_DEDUCTION_2024,
    brackets: List[Tuple[float, float, float]] = TAX_BRACKETS_2024,
) -> float:
    """
    Calculate federal income tax using progressive tax brackets.
    """
    if income <= standard_deduction:
        return 0

    taxable_income = income - standard_deduction
    total_tax = 0

    for lower, upper, rate in brackets:
        if taxable_income <= lower:
            break

        taxable_in_bracket = min(taxable_income, upper) - lower
        total_tax += taxable_in_bracket * rate

        if taxable_income <= upper:
            break

    return total_tax


def calculate_marginal_tax_rate(
    income: float,
    standard_deduction: float = STANDARD_DEDUCTION_2024,
    brackets: List[Tuple[float, float, float]] = TAX_BRACKETS_2024,
) -> float:
    """
    Calculate the marginal tax rate at a given income level.
    """
    if income <= standard_deduction:
        return 0

    taxable_income = income - standard_deduction

    for lower, upper, rate in brackets:
        if lower <= taxable_income < upper:
            return rate

    return brackets[-1][2]


def get_contribution_limit(
    age: int, year: int, inflation_rate: float = DEFAULT_INFLATION_RATE
) -> Dict[str, float]:
    """
    Get 401k contribution limits based on age and year, adjusted for inflation.
    """
    base_year = 2024
    inflation_factor = (1 + inflation_rate) ** (year - base_year)

    base_limit = round((BASE_CONTRIBUTION_LIMIT_2024 * inflation_factor) / 500) * 500
    catchup_limit = (
        round((CATCHUP_CONTRIBUTION_LIMIT_2024 * inflation_factor) / 500) * 500
        if age >= CATCHUP_AGE
        else 0
    )

    return {
        "base": base_limit,
        "catchup": catchup_limit,
        "total": base_limit + catchup_limit,
    }


def run_accumulation_simulation(
    annual_income: float,
    current_age: int,
    retirement_age: int,
    accumulation_return: float,
    contribution_percentage: float = 1.0,  # 1.0 means max out limits
    employer_match_percent: float = 0.0,
    employer_match_limit: float = 0.0,
    inflation_rate: float = DEFAULT_INFLATION_RATE,
    capital_gains_rate: float = DEFAULT_CAPITAL_GAINS_RATE,
) -> Dict[str, pd.DataFrame]:
    """
    Simulate the accumulation phase for both 401k and Roth strategies.

    Args:
        contribution_percentage: Percentage of the maximum limit to contribute (or could be % of income, but logic below assumes % of max limit for simplicity based on previous notebook, let's adjust to be flexible).
        Actually, let's interpret contribution_percentage as % of Income if > 1 (unlikely) or just a factor.
        Wait, the user asked for "Annual Contribution ($ or %)".
        Let's change the signature to accept a specific annual contribution amount OR a percentage of income.
        For now, let's stick to the logic: User inputs a target contribution.

        Let's refine the args:
        contribution_input: float - If < 1, treated as % of income. If >= 1, treated as $ amount.
        BUT, we also need to respect IRS limits.
    """
    # Re-defining the function inside to handle the logic properly
    pass


# Redefining the function with better signature
def run_full_simulation(
    annual_income: float,
    current_age: int,
    retirement_age: int,
    final_age: int,
    accumulation_return: float,
    retirement_return: float,
    contribution_input: float,  # If <= 1.0 treated as % of income, else $ amount. If 0, assumes max limit? No, let's make it explicit.
    use_max_contribution: bool,
    employer_match_percent: float,
    employer_match_limit: float,
    invest_tax_savings: bool = True,
    annual_raise_percent: float = 0.0,
    inflation_rate: float = DEFAULT_INFLATION_RATE,
    capital_gains_rate: float = DEFAULT_CAPITAL_GAINS_RATE,
) -> Dict[str, pd.DataFrame]:
    accumulation_years = retirement_age - current_age
    accumulation_years = retirement_age - current_age

    # --- Accumulation Phase ---
    accumulation_401k = []
    accumulation_roth = []

    balance_401k_trad = 0.0  # Pre-tax balance
    balance_401k_taxable = 0.0  # Taxable brokerage from tax savings

    # For Roth strategy, we might also have a taxable account if we want to compare "equal cost"
    # The original analysis assumed:
    # 401k Strategy: Contribute $X to 401k. Tax savings $Y invested in Taxable. Total Cost = $X - $Y.
    # Roth Strategy: Contribute $X to Roth. Total Cost = $X.
    # This is NOT equal cost.
    # Equal cost would be:
    # 401k: Contribute $Limit. Cost = $Limit * (1 - TaxRate).
    # Roth: Contribute $Limit. Cost = $Limit.
    # To make them comparable, the notebook did:
    # "Compare strategies based on equal after-tax standard of living" -> This was for withdrawals.
    # For contributions:
    # "401K extra savings are taxed: 401k pre-tax savings that are invested are also taxed"
    # "Tax savings from 401K are invested"
    # So:
    # 401k Contribution = Max Limit
    # Roth Contribution = Max Limit
    # Tax Savings = Max Limit * Marginal Rate
    # 401k Strategy invests Tax Savings into Taxable Account.
    # Roth Strategy invests 0 into Taxable Account (because no tax savings).
    # This implies the person has enough cash flow to max out Roth (which costs more after-tax).
    # This effectively compares:
    # Option A: Max 401k + Invest Tax Savings
    # Option B: Max Roth
    # This assumes the "Budget" is equal to (Max Limit). Wait.
    # If I max 401k ($23k), my take home reduces by $23k * (1-Tax).
    # If I max Roth ($23k), my take home reduces by $23k.
    # So Option B costs more.
    # The notebook says: "Both strategies contribute the same dollar amount to retirement accounts".
    # And "For 401K strategy: tax savings are invested in taxable account".
    # This implies the user has the cashflow to support the Roth contribution.
    # So for the 401k case, they have "extra" cashflow equal to the tax savings, which they invest.
    # This is a fair comparison of "What if I max out my accounts?".

    # We will stick to this logic:
    # 1. Determine Contribution Amount (User input or Max Limit).
    # 2. Calculate Employer Match.
    # 3. 401k Strategy:
    #    - Add Contribution + Match to Pre-Tax 401k.
    #    - Calculate Tax Savings = Contribution * Marginal Rate.
    #    - Add Tax Savings to Taxable Account.
    # 4. Roth Strategy:
    #    - Add Contribution to Roth 401k.
    #    - Add Match to Pre-Tax 401k (Employer match is always pre-tax).
    #    - Taxable Account = 0 (No tax savings).

    for year in range(accumulation_years):
        age = current_age + year
        calendar_year = 2024 + year

        # Grow Income
        current_annual_income = annual_income * ((1 + annual_raise_percent) ** year)

        limits = get_contribution_limit(age, calendar_year, inflation_rate)
        max_limit = limits["total"]

        # Determine user contribution
        if use_max_contribution:
            user_contribution = max_limit
        else:
            if contribution_input <= 1.0:
                user_contribution = current_annual_income * contribution_input
            else:
                user_contribution = contribution_input
            # Cap at limit
            user_contribution = min(user_contribution, max_limit)

        # Employer Match
        match_amount = 0
        if employer_match_limit > 0:
            matchable_contribution = min(
                user_contribution, current_annual_income * employer_match_limit
            )
            match_amount = matchable_contribution * employer_match_percent

        # --- 401k Strategy ---
        # Invest
        balance_401k_trad += user_contribution + match_amount

        # Tax Savings
        marginal_rate = calculate_marginal_tax_rate(current_annual_income)
        tax_savings = user_contribution * marginal_rate

        if invest_tax_savings:
            balance_401k_taxable += tax_savings

        # Growth
        balance_401k_trad *= 1 + accumulation_return
        balance_401k_taxable *= 1 + accumulation_return

        # Tax Drag on Taxable
        taxable_gains = balance_401k_taxable - (
            balance_401k_taxable / (1 + accumulation_return)
        )
        tax_on_gains = taxable_gains * capital_gains_rate
        balance_401k_taxable -= tax_on_gains

        # Tax Rates
        # For Traditional 401k, contribution is tax-deductible
        taxable_income_for_fed_tax = current_annual_income - user_contribution
        federal_income_tax = calculate_federal_tax(taxable_income_for_fed_tax)

        total_tax = federal_income_tax + tax_on_gains

        effective_tax_rate = (
            total_tax / current_annual_income if current_annual_income > 0 else 0
        )

        accumulation_401k.append(
            {
                "Year": year,
                "Age": age,
                "Gross_Income": current_annual_income,
                "Contribution": user_contribution,
                "Match": match_amount,
                "Balance_PreTax": balance_401k_trad,
                "Balance_Taxable": balance_401k_taxable,
                "Total_Balance": balance_401k_trad + balance_401k_taxable,
                "Tax_On_Brokerage_Gains": tax_on_gains,
                "Tax_Savings": tax_savings,
                "Marginal_Tax_Rate": marginal_rate,
                "Effective_Tax_Rate": effective_tax_rate,
                "Federal_Income_Tax": federal_income_tax,
                "Total_Tax": total_tax,
            }
        )

        # --- Roth Strategy ---
        # Invest
        # Roth Contribution goes to Roth Bucket
        # Match Contribution goes to Pre-Tax Bucket (Standard 401k rule)
        # We need to track Pre-Tax bucket for Roth Strategy too!

        # Let's use separate variables for Roth Strategy
        if year == 0:
            roth_strat_balance_roth = 0.0
            roth_strat_balance_pretax = 0.0  # From match
            # roth_strat_balance_taxable = 0.0 # Should be 0

        roth_strat_balance_roth += user_contribution
        roth_strat_balance_pretax += match_amount

        # Growth
        roth_strat_balance_roth *= 1 + accumulation_return
        roth_strat_balance_pretax *= 1 + accumulation_return

        # Roth Tax Calculation
        # The user contributes 'user_contribution' AFTER tax.
        # Taxable Income is the full Gross Income.
        federal_income_tax = calculate_federal_tax(current_annual_income)

        # We also tracked "Income_Tax_Paid_On_Contribution" separately for analysis,
        # but it is part of the Federal Income Tax.
        # Total Tax for Roth strategy in accumulation is just the Federal Income Tax
        # (assuming no taxable brokerage account in this simplified comparison).
        total_tax = federal_income_tax

        marginal_rate = calculate_marginal_tax_rate(current_annual_income)
        roth_pretax_equivalent = user_contribution / (1 - marginal_rate)
        roth_tax_paid = roth_pretax_equivalent - user_contribution

        effective_tax_rate = (
            total_tax / current_annual_income if current_annual_income > 0 else 0
        )

        accumulation_roth.append(
            {
                "Year": year,
                "Age": age,
                "Gross_Income": current_annual_income,
                "Contribution": user_contribution,
                "Match": match_amount,
                "Balance_Roth": roth_strat_balance_roth,
                "Balance_PreTax": roth_strat_balance_pretax,
                "Total_Balance": roth_strat_balance_roth + roth_strat_balance_pretax,
                "Income_Tax_Paid_On_Contribution": roth_tax_paid,  # Track the upfront tax
                "Tax_Savings": 0,
                "Marginal_Tax_Rate": marginal_rate,
                "Effective_Tax_Rate": effective_tax_rate,
                "Federal_Income_Tax": federal_income_tax,
                "Total_Tax": total_tax,
            }
        )

        # Update loop variables for next iteration
        # (Implicitly handled by updating the balance variables)

    # --- Distribution Phase ---
    # We need to optimize withdrawals.
    # 401k Strategy: Has PreTax + Taxable.
    # Roth Strategy: Has Roth + PreTax (from match).

    # We reuse the optimization logic but adapted for the new buckets.

    # 401k Strategy Totals at Retirement
    final_401k_pretax = balance_401k_trad
    final_401k_taxable = balance_401k_taxable

    # Roth Strategy Totals at Retirement
    final_roth_roth = roth_strat_balance_roth
    final_roth_pretax = roth_strat_balance_pretax

    # Run distribution for 401k Strategy
    dist_401k = run_distribution_simulation(
        final_401k_pretax,
        0,
        final_401k_taxable,
        retirement_age,
        final_age,
        retirement_return,
    )

    # Run distribution for Roth Strategy
    dist_roth = run_distribution_simulation(
        final_roth_pretax,
        final_roth_roth,
        0,
        retirement_age,
        final_age,
        retirement_return,
    )

    return {
        "accumulation_401k": pd.DataFrame(accumulation_401k),
        "accumulation_roth": pd.DataFrame(accumulation_roth),
        "distribution_401k": pd.DataFrame(dist_401k),
        "distribution_roth": pd.DataFrame(dist_roth),
    }


def calculate_annual_withdrawal_need(
    starting_balance: float, years: int, return_rate: float
) -> float:
    if return_rate == 0:
        return starting_balance / years
    factor = (return_rate * (1 + return_rate) ** years) / (
        (1 + return_rate) ** years - 1
    )
    return starting_balance * factor


def run_distribution_simulation(
    start_pretax: float,
    start_roth: float,
    start_taxable: float,
    retirement_age: int,
    final_age: int,
    return_rate: float,
) -> List[Dict]:
    years = final_age - retirement_age
    total_balance = start_pretax + start_roth + start_taxable

    # Calculate gross withdrawal needed to deplete TOTAL balance
    # This is a simplification. The notebook tried to equalize "After-Tax" income.
    # To do that, we need to solve for X such that (Withdrawal - Tax) is constant.
    # But Tax depends on Withdrawal source.
    # The notebook logic:
    # 1. Calculate Gross Withdrawal from Total Balance (as if no tax).
    # 2. Withdraw proportionally from accounts.
    # 3. Calculate Tax.
    # 4. Resulting Net Income is what it is.
    # This results in different Net Incomes for the two strategies.
    # The notebook claimed "Equal Lifestyle Comparison: Compare strategies based on equal after-tax standard of living".
    # But in `optimize_withdrawal_strategy`:
    # "For equal lifestyle comparison, we need to determine what withdrawal amounts from each strategy would provide the same after-tax spending power."
    # It calculated `withdrawal_401k_strategy` based on total balance.
    # Then calculated `after_tax_income_401k`.
    # Then for Roth, it just calculated `withdrawal_roth_strategy` and `after_tax_income_roth`.
    # It didn't force them to be equal. It just compared them.
    # "Annual After-Tax Income: $233,798" (401k) vs "$218,212" (Roth).
    # So the 401k strategy actually provided MORE income in that example because of the tax savings invested.

    # We will follow the same logic: Deplete the pot over N years, calculate taxes, show resulting Net Income.

    annual_gross_withdrawal = calculate_annual_withdrawal_need(
        total_balance, years, return_rate
    )

    results = []

    curr_pretax = start_pretax
    curr_roth = start_roth
    curr_taxable = start_taxable

    for year in range(years):
        age = retirement_age + year

        # Growth
        curr_pretax *= 1 + return_rate
        curr_roth *= 1 + return_rate
        curr_taxable *= 1 + return_rate

        # Determine withdrawal mix
        # Proportional to balances
        curr_total = curr_pretax + curr_roth + curr_taxable
        if curr_total <= 0:
            break

        w_pretax = annual_gross_withdrawal * (curr_pretax / curr_total)
        w_roth = annual_gross_withdrawal * (curr_roth / curr_total)
        w_taxable = annual_gross_withdrawal * (curr_taxable / curr_total)

        # Withdraw
        curr_pretax -= w_pretax
        curr_roth -= w_roth
        curr_taxable -= w_taxable

        # Calculate Tax
        # PreTax -> Ordinary Income
        tax_pretax = calculate_federal_tax(w_pretax)

        # Taxable -> Capital Gains (Assume 50% is gains as per notebook)
        tax_taxable = (w_taxable * 0.5) * DEFAULT_CAPITAL_GAINS_RATE

        # Roth -> 0 Tax

        total_tax = tax_pretax + tax_taxable
        net_income = (w_pretax + w_roth + w_taxable) - total_tax

        # Marginal Rate on Withdrawal (using Gross Withdrawal as proxy for income level)
        # Note: This is an approximation. True marginal rate depends on taxable income.
        # For PreTax, taxable income is w_pretax.
        # For Taxable, it's capital gains (which has different rates).
        # For Roth, it's 0.
        # Let's report the Marginal Rate based on the Taxable Income (w_pretax).
        marginal_rate_dist = calculate_marginal_tax_rate(w_pretax)

        results.append(
            {
                "Year": year,
                "Age": age,
                "Balance_PreTax": max(0, curr_pretax),
                "Balance_Roth": max(0, curr_roth),
                "Balance_Taxable": max(0, curr_taxable),
                "Total_Balance": max(0, curr_total),
                "Gross_Income": w_pretax
                + w_roth
                + w_taxable,  # Gross Withdrawal is the "Income"
                "Gross_Withdrawal": w_pretax + w_roth + w_taxable,
                "Withdrawal_PreTax": w_pretax,
                "Withdrawal_Roth": w_roth,
                "Withdrawal_Taxable": w_taxable,
                "Federal_Income_Tax": tax_pretax,
                "Tax_On_Brokerage_Gains": tax_taxable,
                "Total_Tax": total_tax,
                "Net_Income": net_income,
                "Effective_Tax_Rate": total_tax / (w_pretax + w_roth + w_taxable)
                if (w_pretax + w_roth + w_taxable) > 0
                else 0,
                "Marginal_Tax_Rate": marginal_rate_dist,
            }
        )

    return results


def combine_simulation_results(
    acc_df: pd.DataFrame, dist_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Combines accumulation and distribution dataframes into a single view.
    """
    acc_df = acc_df.copy()
    dist_df = dist_df.copy()

    acc_df["Phase"] = "Accumulation"
    dist_df["Phase"] = "Distribution"

    # Adjust Year in distribution to be continuous
    if not acc_df.empty:
        last_acc_year = acc_df["Year"].max()
        dist_df["Year"] = dist_df["Year"] + last_acc_year + 1

    combined = pd.concat([acc_df, dist_df], ignore_index=True)
    combined = combined.fillna(0)

    # Reorder columns: Age, Year, Phase, then the rest
    cols = ["Age", "Year", "Phase"] + [
        c for c in combined.columns if c not in ["Age", "Year", "Phase"]
    ]
    combined = combined[cols]

    return combined
