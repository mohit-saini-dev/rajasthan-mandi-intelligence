from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

WEEKDAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

CLASSIFICATION_ORDER = [
    "Commodity-specific",
    "Mixed market activity",
    "Potentially market-wide",
]

FIGURE_DPI = 300


def load_csv(filename, required_columns):
    """Load a processed CSV and verify its required schema."""
    path = PROCESSED_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Required input file not found: {path}")

    if path.stat().st_size == 0:
        raise ValueError(f"Input file is empty: {path}")

    dataframe = pd.read_csv(path)

    if dataframe.empty:
        raise ValueError(f"Input CSV contains no data rows: {path}")

    missing = sorted(set(required_columns) - set(dataframe.columns))

    if missing:
        raise ValueError(
            f"{filename} is missing required columns: {missing}"
        )

    return dataframe


def save_figure(fig, filename):
    """Save a figure and close it to release memory."""
    output_path = FIGURES_DIR / filename

    fig.savefig(
        output_path,
        dpi=FIGURE_DPI,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(fig)

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError(f"Figure was not created correctly: {output_path}")

    print(f"Saved: {output_path.relative_to(PROJECT_ROOT)}")


def prepare_output_directory():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def create_weekday_chart():
    data = load_csv(
        "weekday_reporting_summary.csv",
        [
            "Weekday",
            "Overall_Reporting_Rate_Pct",
        ],
    )

    data["Overall_Reporting_Rate_Pct"] = pd.to_numeric(
        data["Overall_Reporting_Rate_Pct"],
        errors="coerce",
    )

    data = data.dropna(
        subset=["Weekday", "Overall_Reporting_Rate_Pct"]
    )

    data["Weekday"] = pd.Categorical(
        data["Weekday"],
        categories=WEEKDAY_ORDER,
        ordered=True,
    )

    data = data.sort_values("Weekday")

    if data.empty:
        raise ValueError("No valid weekday reporting observations found.")

    fig, ax = plt.subplots(figsize=(10, 5.5))

    bars = ax.bar(
        data["Weekday"].astype(str),
        data["Overall_Reporting_Rate_Pct"],
    )

    ax.set_title(
        "Overall Market–Commodity Reporting Rate by Weekday",
        pad=14,
    )
    ax.set_xlabel("Weekday")
    ax.set_ylabel("Reporting rate (%)")
    ax.set_ylim(0, 65)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)

    ax.bar_label(
        bars,
        fmt="%.1f%%",
        padding=3,
        fontsize=9,
    )

    fig.text(
        0.5,
        0.01,
        "Calendar-span reporting measure; not a verified market operating-day rate.",
        ha="center",
        fontsize=8,
    )

    fig.tight_layout(rect=(0, 0.05, 1, 1))
    save_figure(fig, "01_weekday_reporting_rates.png")


def create_commodity_weekday_chart():
    data = load_csv(
        "commodity_weekday_reporting_summary.csv",
        [
            "Commodity_Name",
            "Weekday",
            "Overall_Reporting_Rate_Pct",
        ],
    )

    data["Overall_Reporting_Rate_Pct"] = pd.to_numeric(
        data["Overall_Reporting_Rate_Pct"],
        errors="coerce",
    )

    data = data.dropna(
        subset=[
            "Commodity_Name",
            "Weekday",
            "Overall_Reporting_Rate_Pct",
        ]
    )

    data["Weekday"] = pd.Categorical(
        data["Weekday"],
        categories=WEEKDAY_ORDER,
        ordered=True,
    )

    pivot = data.pivot(
        index="Weekday",
        columns="Commodity_Name",
        values="Overall_Reporting_Rate_Pct",
    )

    pivot = pivot.reindex(WEEKDAY_ORDER)

    if pivot.empty:
        raise ValueError("No valid commodity-weekday reporting data found.")

    fig, ax = plt.subplots(figsize=(11, 6))

    for commodity in pivot.columns:
        ax.plot(
            pivot.index.astype(str),
            pivot[commodity],
            marker="o",
            linewidth=1.8,
            markersize=4,
            label=commodity,
        )

    ax.set_title(
        "Reporting Rate by Commodity and Weekday",
        pad=14,
    )
    ax.set_xlabel("Weekday")
    ax.set_ylabel("Overall reporting rate (%)")
    ax.grid(alpha=0.25)
    ax.set_axisbelow(True)
    ax.legend(
        title="Commodity",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        fontsize=8,
    )

    fig.text(
        0.5,
        0.01,
        "Rates use the eligible market–commodity pairs for each commodity.",
        ha="center",
        fontsize=8,
    )

    fig.tight_layout(rect=(0, 0.05, 0.82, 1))
    save_figure(fig, "02_commodity_weekday_reporting.png")


def create_monthly_reporting_chart():
    data = load_csv(
        "monthly_reporting_rates_by_commodity_year.csv",
        [
            "Commodity_Name",
            "Year",
            "Month_Num",
            "Month",
            "Calendar_Span_Reporting_Rate_Pct",
            "Is_Incomplete_Month",
        ],
    )

    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
    data["Month_Num"] = pd.to_numeric(
        data["Month_Num"],
        errors="coerce",
    )
    data["Calendar_Span_Reporting_Rate_Pct"] = pd.to_numeric(
        data["Calendar_Span_Reporting_Rate_Pct"],
        errors="coerce",
    )

    incomplete = (
        data["Is_Incomplete_Month"]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes"])
    )

    data = data.loc[~incomplete].copy()

    data = data.dropna(
        subset=[
            "Commodity_Name",
            "Year",
            "Month_Num",
            "Calendar_Span_Reporting_Rate_Pct",
        ]
    )

    data["Period"] = pd.to_datetime(
        {
            "year": data["Year"].astype(int),
            "month": data["Month_Num"].astype(int),
            "day": 1,
        },
        errors="coerce",
    )

    data = data.dropna(subset=["Period"]).sort_values("Period")

    if data.empty:
        raise ValueError("No complete monthly reporting records found.")

    fig, ax = plt.subplots(figsize=(12, 6))

    for commodity, group in data.groupby("Commodity_Name"):
        group = group.sort_values("Period")

        ax.plot(
            group["Period"],
            group["Calendar_Span_Reporting_Rate_Pct"],
            marker="o",
            markersize=2.8,
            linewidth=1.5,
            label=commodity,
        )

    ax.set_title(
        "Monthly Reporting Trends by Commodity",
        pad=14,
    )
    ax.set_xlabel("Month")
    ax.set_ylabel("Calendar-span reporting rate (%)")
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.25)
    ax.set_axisbelow(True)
    ax.legend(
        title="Commodity",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        fontsize=8,
    )

    fig.text(
        0.5,
        0.01,
        "Incomplete months excluded. Rates are based on calendar-span exposure, not verified trading days.",
        ha="center",
        fontsize=8,
    )

    fig.tight_layout(rect=(0, 0.05, 0.82, 1))
    save_figure(fig, "03_monthly_commodity_reporting_trends.png")


def create_market_consistency_chart():
    data = load_csv(
        "market_reporting_consistency.csv",
        [
            "Market_Name",
            "Commodity_Name",
            "Calendar_Span_Reporting_Rate_Pct",
            "Peer_Benchmark_Reporting_Rate_Pct",
            "Adjusted_Rank_Within_Commodity",
        ],
    )

    numeric_columns = [
        "Calendar_Span_Reporting_Rate_Pct",
        "Peer_Benchmark_Reporting_Rate_Pct",
        "Adjusted_Rank_Within_Commodity",
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        )

    data = data.dropna(
        subset=[
            "Market_Name",
            "Commodity_Name",
            *numeric_columns,
        ]
    )

    data = data.sort_values(
        "Adjusted_Rank_Within_Commodity"
    ).head(15).copy()

    if data.empty:
        raise ValueError("No valid market consistency records found.")

    data["Label"] = (
        data["Market_Name"]
        + " | "
        + data["Commodity_Name"]
    )

    data = data.sort_values(
        "Calendar_Span_Reporting_Rate_Pct",
        ascending=True,
    )

    positions = np.arange(len(data))
    bar_height = 0.36

    fig, ax = plt.subplots(figsize=(12, 8))

    ax.barh(
        positions - bar_height / 2,
        data["Calendar_Span_Reporting_Rate_Pct"],
        height=bar_height,
        label="Actual reporting rate",
    )

    ax.barh(
        positions + bar_height / 2,
        data["Peer_Benchmark_Reporting_Rate_Pct"],
        height=bar_height,
        label="Peer benchmark",
    )

    ax.set_yticks(positions)
    ax.set_yticklabels(data["Label"], fontsize=8)
    ax.set_xlabel("Reporting rate (%)")
    ax.set_title(
        "Selected Low-Ranked Market-Commodity Pairs vs. Commodity Peer Benchmarks",
        pad=14,
    )
    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)
    ax.legend(loc="lower right")

    fig.text(
        0.5,
        0.01,
        "Pairs ranked using adjusted reporting consistency within commodity; peer rates are benchmarks, not targets.",
        ha="center",
        fontsize=8,
    )

    fig.tight_layout(rect=(0, 0.05, 1, 1))
    save_figure(fig, "04_market_reporting_vs_peer_benchmark.png")


def create_interruption_classification_chart():
    data = load_csv(
        "interruption_market_activity_summary.csv",
        [
            "Event_ID",
            "Classification",
        ],
    )

    counts = data["Classification"].value_counts()

    ordered_counts = counts.reindex(
        CLASSIFICATION_ORDER,
        fill_value=0,
    )

    ordered_counts = ordered_counts[
        ordered_counts > 0
    ].sort_values(ascending=True)

    if ordered_counts.empty:
        raise ValueError("No interruption classifications found.")

    fig, ax = plt.subplots(figsize=(10, 5.5))

    bars = ax.barh(
        ordered_counts.index,
        ordered_counts.values,
    )

    ax.set_title(
        "Classification of Zero-Reporting Interruption Events",
        pad=14,
    )
    ax.set_xlabel("Number of interruption events")
    ax.set_ylabel("Classification")
    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)

    ax.bar_label(
        bars,
        padding=4,
        fontsize=9,
    )

    total_events = int(ordered_counts.sum())

    fig.text(
        0.5,
        0.01,
        (
            f"{total_events} events. Potentially market-wide means no recorded "
            "commodity activity at the market during the event; it does not prove closure."
        ),
        ha="center",
        fontsize=8,
    )

    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save_figure(fig, "05_interruption_event_classification.png")


def create_trailing_silence_chart():
    data = load_csv(
        "trailing_silence_final_findings.csv",
        [
            "Market_Name",
            "Commodity_Name",
            "Trailing_Silent_Days",
            "Dataset_Cutoff_Date",
            "Finding",
        ],
    )

    data["Trailing_Silent_Days"] = pd.to_numeric(
        data["Trailing_Silent_Days"],
        errors="coerce",
    )

    data = data.dropna(
        subset=[
            "Market_Name",
            "Commodity_Name",
            "Trailing_Silent_Days",
        ]
    )

    data = data.loc[
        data["Trailing_Silent_Days"] > 0
    ].copy()

    if data.empty:
        raise ValueError("No positive trailing-silence records found.")

    data = data.sort_values(
        "Trailing_Silent_Days",
        ascending=False,
    ).head(12)

    data["Label"] = (
        data["Market_Name"]
        + " | "
        + data["Commodity_Name"]
    )

    data = data.sort_values(
        "Trailing_Silent_Days",
        ascending=True,
    )

    fig, ax = plt.subplots(figsize=(11, 7))

    bars = ax.barh(
        data["Label"],
        data["Trailing_Silent_Days"],
    )

    ax.set_title(
        "Longest Trailing Reporting Silence",
        pad=14,
    )
    ax.set_xlabel("Days since last reported observation")
    ax.set_ylabel("Market | Commodity")
    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)

    ax.bar_label(
        bars,
        fmt="%.0f days",
        padding=4,
        fontsize=8,
    )

    cutoff_dates = data["Dataset_Cutoff_Date"].dropna().unique()
    cutoff_text = (
        ", ".join(sorted(cutoff_dates))
        if len(cutoff_dates)
        else "not specified"
    )

    fig.text(
        0.5,
        0.01,
        (
            f"Dataset cutoff: {cutoff_text}. "
            "Source-level reporting silence is not proof of physical market closure."
        ),
        ha="center",
        fontsize=8,
    )

    fig.tight_layout(rect=(0, 0.05, 1, 1))
    save_figure(fig, "06_trailing_reporting_silence.png")


def main():
    prepare_output_directory()

    print("Rajasthan Mandi Intelligence — Analytical Chart Generation")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Matplotlib version: {matplotlib.__version__}")
    print(f"Output directory: {FIGURES_DIR}")
    print()

    chart_generators = [
        create_weekday_chart,
        create_commodity_weekday_chart,
        create_monthly_reporting_chart,
        create_market_consistency_chart,
        create_interruption_classification_chart,
        create_trailing_silence_chart,
    ]

    for generate_chart in chart_generators:
        generate_chart()

    expected_files = [
        "01_weekday_reporting_rates.png",
        "02_commodity_weekday_reporting.png",
        "03_monthly_commodity_reporting_trends.png",
        "04_market_reporting_vs_peer_benchmark.png",
        "05_interruption_event_classification.png",
        "06_trailing_reporting_silence.png",
    ]

    missing_files = [
        filename
        for filename in expected_files
        if not (FIGURES_DIR / filename).exists()
        or (FIGURES_DIR / filename).stat().st_size == 0
    ]

    if missing_files:
        raise RuntimeError(
            f"Chart generation incomplete. Missing files: {missing_files}"
        )

    print()
    print(f"SUCCESS: {len(expected_files)} analytical charts generated.")
    print("All expected figure files exist and are non-empty.")


if __name__ == "__main__":
    main()
