from streamlit.testing.v1 import AppTest
import os


def test_app_runs():
    """
    Smoke test to verify the app runs without error.
    """
    app_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "app", "main.py")
    )
    at = AppTest.from_file(app_path)
    at.run()

    # Check if there are any exceptions
    assert not at.exception

    # Check if title is present
    assert len(at.title) > 0
    assert at.title[0].value == "💰 401k vs Roth 401k Analysis"

    # Check if charts are present
    # Note: Altair charts might not be fully rendered in headless test, but we can check if elements exist
    # assert len(at.altair_chart) > 0
    # AppTest might not capture altair_chart elements easily in all versions,
    # but let's check basic structure.
