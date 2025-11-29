from unittest.mock import MagicMock, patch
import sys
import os

# Ensure app is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ui import render_sidebar, render_summary_metrics


@patch("app.ui.st")
def test_render_sidebar(mock_st):
    # Setup mock return values for sidebar inputs
    mock_st.sidebar.number_input.side_effect = [
        25,  # Current Age
        65,  # Ret Age
        90,  # Final Age
        80000,  # Income
        0,  # Retirement Income
        # Contribution input is skipped if mode is Percentage
    ]
    mock_st.sidebar.slider.side_effect = [
        2.0,  # Raise
        10,  # Contribution % (since default mode is Percentage)
        50,  # Match %
        6,  # Match Limit
        100,  # Invest Tax Savings %
        50,  # Roth Split
        8.0,  # Acc Ret
        6.0,  # Ret Ret
        0.0,  # Extra buffer
        0.0,  # Extra buffer
    ]
    mock_st.sidebar.radio.return_value = "Percentage of Income"
    mock_st.sidebar.checkbox.return_value = True

    config = render_sidebar()

    # Check return values
    assert config["current_age"] == 25
    assert config["retirement_age"] == 65
    assert config["annual_income"] == 80000
    assert config["retirement_income"] == 0
    assert config["contribution_input"] == 0.10
    assert config["match_percent"] == 50
    assert config["match_limit"] == 6
    assert config["invest_tax_savings_percent"] == 1.0  # Default 100%
    assert config["roth_split_percent"] == 0.5  # Default 50%


@patch("app.ui.st")
def test_render_summary_metrics(mock_st):
    # Mock dataframes
    mock_acc_401k = MagicMock()
    mock_acc_401k.iloc.__getitem__.return_value = {
        "Total_Balance": 1000000,
        "Contribution": 50000,
        "Match": 10000,
    }

    mock_acc_roth = MagicMock()
    mock_acc_roth.iloc.__getitem__.return_value = {"Total_Balance": 1000000}

    mock_acc_split = MagicMock()
    mock_acc_split.iloc.__getitem__.return_value = {"Total_Balance": 1000000}

    mock_dist_401k = MagicMock()
    mock_dist_401k.__getitem__.return_value.mean.return_value = 50000
    mock_dist_401k.__getitem__.return_value.sum.return_value = 10000

    mock_dist_roth = MagicMock()
    mock_dist_roth.__getitem__.return_value.mean.return_value = 55000
    mock_dist_roth.__getitem__.return_value.sum.return_value = 0

    mock_dist_split = MagicMock()
    mock_dist_split.__getitem__.return_value.mean.return_value = 60000  # Split wins
    mock_dist_split.__getitem__.return_value.sum.return_value = 5000

    # Mock columns to return 4 mocks
    mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]

    render_summary_metrics(
        mock_acc_401k,
        mock_acc_roth,
        mock_acc_split,
        mock_dist_401k,
        mock_dist_roth,
        mock_dist_split,
        60,
        1.0,  # invest_tax_savings_percent
    )

    # Verify cols were created
    mock_st.columns.assert_called_with(4)
    # Verify metrics were displayed
    assert mock_st.metric.call_count >= 9

    # Verify success message (Split wins)
    # We can check if st.success was called with a string containing "Split Wins"
    args, _ = mock_st.success.call_args
    assert "Split Wins" in args[0]
