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
        30,
        60,
        90,
        100000,
        23000,
    ]  # Age, RetAge, FinalAge, Income, Contribution
    mock_st.sidebar.slider.side_effect = [
        2.0,
        10,
        0,
        50,
        7.0,
        5.0,
    ]  # Raise, Match%, MatchLimit, RothSplit, AccRet, RetRet
    mock_st.sidebar.radio.return_value = "Custom Amount"
    mock_st.sidebar.checkbox.return_value = True

    config = render_sidebar()

    assert config["current_age"] == 30
    assert config["retirement_age"] == 60
    assert config["final_age"] == 90
    assert config["annual_income"] == 100000
    assert not config["use_max_contribution"]
    assert config["invest_tax_savings"]
    assert config["roth_split_percent"] == 0.5


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

    mock_dist_401k = MagicMock()
    mock_dist_401k.__getitem__.return_value.mean.return_value = 50000
    mock_dist_401k.__getitem__.return_value.sum.return_value = 10000

    mock_dist_roth = MagicMock()
    mock_dist_roth.__getitem__.return_value.mean.return_value = 55000
    mock_dist_roth.__getitem__.return_value.sum.return_value = 0

    # Mock columns to return 3 mocks
    mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]

    render_summary_metrics(
        mock_acc_401k, mock_acc_roth, mock_dist_401k, mock_dist_roth, 60, True
    )

    # Verify cols were created
    mock_st.columns.assert_called_with(3)
    # Verify metrics were displayed
    assert mock_st.metric.call_count >= 6
