# 401k vs Roth Analysis

A comprehensive Streamlit application designed to simulate and compare the long-term financial impact of contributing to a **Traditional 401k** (Pre-Tax) versus a **Roth 401k** (After-Tax).

This tool helps users make informed decisions by visualizing lifetime wealth accumulation, tax implications, and net spendable income during retirement.

## Features

- **Lifetime Wealth Trajectory**: Visualize how your balance grows during the accumulation phase and draws down during retirement.
- **Comparative Analysis**: Directly compare Traditional and Roth strategies side-by-side.
- **Cashflow & Advantage**: Analyze net spendable income and cumulative advantages of one strategy over the other.
- **Deep Dive Metrics**: Explore detailed breakdowns of wealth composition, effective tax rates, and annual contributions.
- **Interactive Simulation**: Adjust parameters like income, age, contribution limits, and market returns to see real-time updates.

## Getting Started

### Prerequisites

- **Python 3.12** or higher.
- **uv**: An extremely fast Python package installer and resolver.

### Installation

This project uses `uv` for dependency management.

1.  **Install uv** (if you haven't already):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd 401k-v-roth
    ```

3.  **Install dependencies**:
    ```bash
    uv sync
    ```

## Usage

To start the application, run the following command:

```bash
uv run streamlit run app/main.py
```

This will launch the Streamlit server and open the application in your default web browser (usually at `http://localhost:8501`).

## Development

### Project Structure

- `app/`: Contains the source code for the Streamlit application.
    - `main.py`: Entry point of the app.
    - `analysis.py`: Core simulation logic.
    - `charts.py`: Visualization functions using Altair.
    - `ui.py`: UI components and sidebar configuration.
- `tests/`: Contains pytest test suites.

### Running Tests

To run the test suite and ensure everything is working correctly:

```bash
uv run pytest
```

### Code Quality & Hooks

This project uses `ruff` for linting and formatting, and `prek` (via `uvx`) for git hooks.

1.  **Install Hooks**:
    ```bash
    uvx prek install
    ```

2.  **Run Linter & Formatter**:
    ```bash
    uv run ruff check .
    uv run ruff format .
    ```

3.  **Run Tests with Coverage**:
    ```bash
    uv run pytest --cov --cov-fail-under=80
    ```
