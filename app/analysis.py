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
DEFAULT_INCOME = 80000
DEFAULT_ACCUMULATION_RETURN = 0.08
DEFAULT_RETIREMENT_RETURN = 0.06
DEFAULT_START_AGE = 25
DEFAULT_RETIREMENT_AGE = 65
DEFAULT_FINAL_AGE = 90
DEFAULT_INFLATION_RATE = 0.025
DEFAULT_CAPITAL_GAINS_RATE = 0.15

# Contribution Limits 2024
# Contribution Limits
BASE_CONTRIBUTION_LIMIT_2025 = 23500
BASE_CONTRIBUTION_LIMIT_2026 = 24500
CATCHUP_CONTRIBUTION_LIMIT_2025 = 7500
CATCHUP_CONTRIBUTION_LIMIT_2026 = 8000
CATCHUP_60_63_LIMIT_2025 = 11250
HIGH_INCOME_THRESHOLD_2025 = 150000
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
    # Base Limit Projection
    if year == 2025:
        base_limit = BASE_CONTRIBUTION_LIMIT_2025
    elif year >= 2026:
        # Anchor to 2026
        inflation_factor = (1 + inflation_rate) ** (year - 2026)
        base_limit = (
            round((BASE_CONTRIBUTION_LIMIT_2026 * inflation_factor) / 500) * 500
        )
    else:
        # Fallback for pre-2025 (shouldn't happen in sim but good for robustness)
        base_limit = 23000

    # Catch-up Limit Projection
    if year == 2025:
        std_catchup_limit = CATCHUP_CONTRIBUTION_LIMIT_2025
        special_catchup_limit = CATCHUP_60_63_LIMIT_2025
    elif year >= 2026:
        # Anchor to 2026 for standard catchup
        inflation_factor_catchup = (1 + inflation_rate) ** (year - 2026)
        std_catchup_limit = (
            round((CATCHUP_CONTRIBUTION_LIMIT_2026 * inflation_factor_catchup) / 500)
            * 500
        )

        # Special catchup is 150% of standard catchup in 2025? Or indexed?
        # The rule is "greater of $10,000 or 150% of the regular catch-up limit for 2024".
        # Actually, for 2025 it's $11,250.
        # For 2026, if standard is 8000, 150% is 12000?
        # User said "if you are age 60 to 63, the $8,000 catch-up contribution is increased to $11,250."
        # This implies 11,250 is fixed or the specific number for 2026?
        # "Looking ahead to 2026... catch-up contribution is increased to $11,250."
        # So I will use 11,250 for 2026 as well, indexed from 2025 base.
        # Let's just index the 11,250 from 2025.
        inflation_factor_2025 = (1 + inflation_rate) ** (year - 2025)
        special_catchup_limit = (
            round((CATCHUP_60_63_LIMIT_2025 * inflation_factor_2025) / 500) * 500
        )
    else:
        std_catchup_limit = 7500
        special_catchup_limit = (
            7500  # No special catchup before 2025/2026 logic applies
        )

    catchup_limit = 0
    if 60 <= age <= 63:
        catchup_limit = special_catchup_limit
    elif age >= CATCHUP_AGE:
        catchup_limit = std_catchup_limit

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
    invest_tax_savings_percent: float = 1.0,
    annual_raise_percent: float = 0.0,
    inflation_rate: float = DEFAULT_INFLATION_RATE,
    capital_gains_rate: float = DEFAULT_CAPITAL_GAINS_RATE,
    roth_split_percent: float = 0.5,
) -> Dict[str, pd.DataFrame]:
    accumulation_years = retirement_age - current_age
    accumulation_years = retirement_age - current_age

    # --- Run Simulations ---
    # 1. Traditional Strategy (100% PreTax)
    accumulation_401k = simulate_accumulation_strategy(
        annual_income,
        current_age,
        accumulation_years,
        accumulation_return,
        contribution_input,
        use_max_contribution,
        employer_match_percent,
        employer_match_limit,
        invest_tax_savings_percent,
        annual_raise_percent,
        inflation_rate,
        capital_gains_rate,
        roth_split=0.0,
    )

    # 2. Roth Strategy (100% Roth)
    accumulation_roth = simulate_accumulation_strategy(
        annual_income,
        current_age,
        accumulation_years,
        accumulation_return,
        contribution_input,
        use_max_contribution,
        employer_match_percent,
        employer_match_limit,
        invest_tax_savings_percent,
        annual_raise_percent,
        inflation_rate,
        capital_gains_rate,
        roth_split=1.0,
    )

    # 3. Split Strategy (User Defined Split)
    accumulation_split = simulate_accumulation_strategy(
        annual_income,
        current_age,
        accumulation_years,
        accumulation_return,
        contribution_input,
        use_max_contribution,
        employer_match_percent,
        employer_match_limit,
        invest_tax_savings_percent,
        annual_raise_percent,
        inflation_rate,
        capital_gains_rate,
        roth_split=roth_split_percent,
    )

    # --- Distribution Phase ---
    # Helper to run distribution for a given accumulation result
    def run_dist_for_acc(acc_df):
        last_row = acc_df.iloc[-1]
        return run_distribution_simulation(
            last_row["Balance_PreTax"],
            last_row["Balance_Roth"],
            last_row["Balance_Taxable"],
            retirement_age,
            final_age,
            retirement_return,
        )

    dist_401k = run_dist_for_acc(accumulation_401k)
    dist_roth = run_dist_for_acc(accumulation_roth)
    dist_split = run_dist_for_acc(accumulation_split)

    return {
        "accumulation_401k": accumulation_401k,
        "accumulation_roth": accumulation_roth,
        "accumulation_split": accumulation_split,
        "distribution_401k": pd.DataFrame(dist_401k),
        "distribution_roth": pd.DataFrame(dist_roth),
        "distribution_split": pd.DataFrame(dist_split),
    }


def simulate_accumulation_strategy(
    annual_income,
    current_age,
    years,
    return_rate,
    contribution_input,
    use_max_contribution,
    match_percent,
    match_limit,
    invest_tax_savings_percent,
    annual_raise,
    inflation_rate,
    capital_gains_rate,
    roth_split: float,  # 0.0 to 1.0
) -> pd.DataFrame:
    results = []

    balance_pretax = 0.0
    balance_roth = 0.0
    balance_taxable = 0.0

    for year in range(years):
        age = current_age + year
        calendar_year = 2025 + year

        # Grow Income
        current_annual_income = annual_income * ((1 + annual_raise) ** year)

        limits = get_contribution_limit(age, calendar_year, inflation_rate)
        base_limit = limits["base"]
        total_limit = limits["total"]

        # Determine user contribution
        if use_max_contribution:
            user_contribution = total_limit
        else:
            if contribution_input <= 1.0:
                user_contribution = current_annual_income * contribution_input
            else:
                user_contribution = contribution_input
            user_contribution = min(user_contribution, total_limit)

        # Employer Match (Always PreTax)
        match_amount = 0
        if match_limit > 0:
            matchable_contribution = min(
                user_contribution, current_annual_income * match_limit
            )
            match_amount = matchable_contribution * match_percent

        # Split Contribution Logic (High Income Rule)
        # Check High Income Threshold (Indexed? Assuming yes)
        inflation_factor_threshold = (1 + inflation_rate) ** (calendar_year - 2025)
        high_income_threshold = (
            round((HIGH_INCOME_THRESHOLD_2025 * inflation_factor_threshold) / 500) * 500
        )

        is_high_income = current_annual_income > high_income_threshold

        # Determine how much is "Base" vs "Catch-up"
        # Catch-up is the amount over the base limit
        amount_base = min(user_contribution, base_limit)
        amount_catchup = max(0, user_contribution - base_limit)

        # Base portion follows the strategy split
        base_roth = amount_base * roth_split
        base_trad = amount_base * (1 - roth_split)

        # Catch-up portion
        if is_high_income and amount_catchup > 0:
            # Mandated Roth for catch-up
            catchup_roth = amount_catchup
            catchup_trad = 0.0
        else:
            # Follows strategy split
            catchup_roth = amount_catchup * roth_split
            catchup_trad = amount_catchup * (1 - roth_split)

        roth_contribution = base_roth + catchup_roth
        trad_contribution = base_trad + catchup_trad

        # Invest
        balance_pretax += trad_contribution + match_amount
        balance_roth += roth_contribution

        # Tax Calculation
        # Taxable Income = Gross Income - Trad Contribution
        taxable_income_for_fed_tax = current_annual_income - trad_contribution
        federal_income_tax = calculate_federal_tax(taxable_income_for_fed_tax)
        marginal_rate = calculate_marginal_tax_rate(taxable_income_for_fed_tax)

        # Tax Savings Logic
        # We compare against a baseline of "No Deduction" (i.e. All Roth or just paying tax on full income).
        # Tax Savings = Trad Contribution * Marginal Rate
        # This is the "extra cash" generated by choosing Trad over Roth/Taxable.
        tax_savings = trad_contribution * marginal_rate

        # Invest percentage of tax savings
        tax_savings_invested = tax_savings * invest_tax_savings_percent
        balance_taxable += tax_savings_invested

        # Growth
        balance_pretax *= 1 + return_rate
        balance_roth *= 1 + return_rate
        balance_taxable *= 1 + return_rate

        # Tax Drag on Taxable
        taxable_gains = balance_taxable - (balance_taxable / (1 + return_rate))
        tax_on_gains = taxable_gains * capital_gains_rate
        balance_taxable -= tax_on_gains

        total_tax = federal_income_tax + tax_on_gains

        # Roth Upfront Tax (Informational)
        # We calculate what the tax *would* be on the Roth portion if it were grossed up?
        # Or just the tax paid on the income used to fund it?
        # It's included in federal_income_tax.
        # But for the specific column "Income_Tax_Paid_On_Contribution":
        # It's the tax attributable to the Roth contribution.
        # Approx: Roth Contribution / (1 - Marginal) * Marginal
        roth_pretax_equivalent = roth_contribution / (1 - marginal_rate)
        roth_tax_paid = roth_pretax_equivalent - roth_contribution

        effective_tax_rate = (
            total_tax / current_annual_income if current_annual_income > 0 else 0
        )

        results.append(
            {
                "Year": year,
                "Age": age,
                "Gross_Income": current_annual_income,
                "Contribution": user_contribution,
                "Match": match_amount,
                "Balance_PreTax": balance_pretax,
                "Balance_Roth": balance_roth,
                "Balance_Taxable": balance_taxable,
                "Total_Balance": balance_pretax + balance_roth + balance_taxable,
                "Tax_On_Brokerage_Gains": tax_on_gains,
                "Income_Tax_Paid_On_Contribution": roth_tax_paid,
                "Tax_Savings": tax_savings,
                "Marginal_Tax_Rate": marginal_rate,
                "Effective_Tax_Rate": effective_tax_rate,
                "Federal_Income_Tax": federal_income_tax,
                "Total_Tax": total_tax,
            }
        )

    return pd.DataFrame(results)


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
