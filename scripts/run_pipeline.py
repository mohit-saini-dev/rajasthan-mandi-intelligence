from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback


# ---------------------------------------------------------
# Project configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
TESTS_DIR = PROJECT_ROOT / "tests"
LOGS_DIR = PROJECT_ROOT / "logs"

TIMESTAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

BACKUP_ROOT = PROJECT_ROOT.parent / (
    f"{PROJECT_ROOT.name}-backup-{TIMESTAMP}"
)

LOG_FILE = LOGS_DIR / f"pipeline_{TIMESTAMP}.log"


# ---------------------------------------------------------
# Pipeline stages
# Each stage specifies:
#   - script to execute
#   - files expected after successful execution
# ---------------------------------------------------------

PIPELINE_STAGES = [
    {
        "name": "Build calendar dimension",
        "script": "build_calendar.py",
        "outputs": [
            "data/processed/dim_date.csv",
        ],
    },
    {
        "name": "Build star schema",
        "script": "build_star_schema.py",
        "outputs": [
            "data/processed/dim_market.csv",
            "data/processed/dim_commodity.csv",
            "data/processed/fact_market_arrivals.csv",
        ],
    },
    {
        "name": "Validate pipeline structure",
        "script": "validate_pipeline.py",
        "outputs": [],
    },
    {
        "name": "Temporal gap analysis",
        "script": "temporal_gap_analysis.py",
        "outputs": [
            "data/processed/temporal_gap_report_refined.csv",
        ],
    },
    {
        "name": "Consecutive gap analysis",
        "script": "detect_consecutive_gaps.py",
        "outputs": [
            "data/processed/temporal_gap_report_with_gaps.csv",
        ],
    },
    {
        "name": "Monthly reporting rates",
        "script": "analyze_monthly_reporting_rates.py",
        "outputs": [
            "data/processed/monthly_reporting_pair_month_panel.csv",
            "data/processed/monthly_reporting_rates_by_commodity_year.csv",
        ],
    },
    {
        "name": "Weekday reporting analysis",
        "script": "analyze_weekday_reporting.py",
        "outputs": [
            "data/processed/weekday_reporting_by_pair.csv",
            "data/processed/weekday_reporting_summary.csv",
        ],
    },
    {
        "name": "Commodity weekday reporting analysis",
        "script": "analyze_commodity_weekday_reporting.py",
        "outputs": [
            "data/processed/commodity_weekday_reporting_by_pair.csv",
            "data/processed/commodity_weekday_reporting_summary.csv",
        ],
    },
    {
        "name": "Market reporting consistency",
        "script": "analyze_market_reporting_consistency.py",
        "outputs": [
            "data/processed/market_reporting_consistency.csv",
            "data/processed/market_reporting_consistency_summary.csv",
        ],
    },
    {
        "name": "Low-reporting monthly patterns",
        "script": "analyze_low_reporting_monthly_patterns.py",
        "outputs": [
            "data/processed/low_reporting_monthly_profile.csv",
            "data/processed/low_reporting_yearly_profile.csv",
            "data/processed/low_reporting_seasonal_profile.csv",
        ],
    },
    {
        "name": "Low-reporting monthly peer comparison",
        "script": "analyze_low_reporting_monthly_peer_comparison.py",
        "outputs": [
            "data/processed/low_reporting_monthly_peer_comparison.csv",
            "data/processed/low_reporting_seasonal_peer_comparison.csv",
        ],
    },
    {
        "name": "Zero-reporting streak diagnostics",
        "script": "diagnose_zero_reporting_streaks.py",
        "outputs": [
            "data/processed/zero_reporting_monthly_diagnostic.csv",
            "data/processed/zero_reporting_yearly_diagnostic.csv",
            "data/processed/zero_reporting_streak_summary.csv",
        ],
    },
    {
        "name": "Extract interruption events",
        "script": "extract_zero_reporting_interruption_events.py",
        "outputs": [
            "data/processed/zero_reporting_interruption_events.csv",
        ],
    },
    {
        "name": "Classify interruption market activity",
        "script": "classify_market_wide_reporting_interruptions.py",
        "outputs": [
            "data/processed/interruption_market_activity_by_month.csv",
            "data/processed/interruption_market_activity_summary.csv",
        ],
    },
    {
        "name": "Exact interruption reconciliation",
        "script": "reconcile_interruption_periods_exact.py",
        "outputs": [
            "data/processed/exact_interruption_raw_reconciliation.csv",
        ],
    },
    {
        "name": "Monthly interruption raw/processed audit",
        "script": "audit_interruption_monthly_activity.py",
        "outputs": [
            "data/processed/interruption_monthly_raw_processed_audit.csv",
        ],
    },
    {
        "name": "Build interruption audit summary",
        "script": "build_interruption_audit_summary.py",
        "outputs": [
            "data/processed/interruption_audit_summary.csv",
            "reports/source_level_reporting_interruption_audit.md",
        ],
    },
    {
        "name": "Analyze trailing reporting silence",
        "script": "analyze_trailing_reporting_silence.py",
        "outputs": [
            "data/processed/trailing_silence_monthly_diagnostic.csv",
            "data/processed/trailing_silence_summary.csv",
        ],
    },
    {
        "name": "Classify trailing silence market activity",
        "script": "classify_trailing_silence_market_activity.py",
        "outputs": [
            "data/processed/trailing_silence_market_wide_audit.csv",
        ],
    },
    {
        "name": "Reconcile trailing silence raw/processed records",
        "script": "reconcile_trailing_silence_raw_processed.py",
        "outputs": [
            "data/processed/trailing_silence_raw_processed_audit.csv",
        ],
    },
    {
        "name": "Build final trailing silence findings",
        "script": "build_trailing_silence_final_findings.py",
        "outputs": [
            "data/processed/trailing_silence_final_findings.csv",
            "data/processed/trailing_silence_market_month_findings.csv",
        ],
    },
]


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

def log(message=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}"

    print(formatted, flush=True)

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(formatted + "\n")


# ---------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------

def check_project_structure():
    required_paths = [
        RAW_DIR,
        SCRIPTS_DIR,
        TESTS_DIR,
        PROJECT_ROOT / "requirements.txt",
        PROJECT_ROOT / "requirements-dev.txt",
        TESTS_DIR / "conftest.py",
    ]

    missing = [
        str(path)
        for path in required_paths
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "Required project paths are missing:\n"
            + "\n".join(missing)
        )

    for stage in PIPELINE_STAGES:
        script_path = SCRIPTS_DIR / stage["script"]

        if not script_path.is_file():
            raise FileNotFoundError(
                f"Pipeline script not found: {script_path}"
            )

    test_files = list(TESTS_DIR.glob("test_*.py"))

    if not test_files:
        raise FileNotFoundError(
            "No pytest test files found in tests/."
        )

    log(f"Project root: {PROJECT_ROOT}")
    log(f"Pytest files discovered: {len(test_files)}")


def check_raw_exports():
    import pandas as pd

    if not RAW_DIR.is_dir():
        raise FileNotFoundError(
            f"Raw data directory does not exist: {RAW_DIR}"
        )

    raw_files = sorted(RAW_DIR.glob("*.csv"))

    if not raw_files:
        raise FileNotFoundError(
            "No raw CSV exports found in data/raw/. "
            "Place the official AGMARKNET CSV exports there."
        )

    required_headers = {
        "state/ut",
        "district",
        "market",
        "commodity group",
        "commodity",
        "date",
        "arrival unit",
        "price unit",
    }

    log(f"Raw CSV exports found: {len(raw_files)}")

    for path in raw_files:
        try:
            header = pd.read_csv(
                path,
                skiprows=1,
                nrows=0,
                encoding="utf-8-sig",
            )

            normalized_headers = {
                str(column).strip().lstrip("\ufeff").casefold()
                for column in header.columns
            }

            missing_headers = (
                required_headers - normalized_headers
            )

            if missing_headers:
                raise ValueError(
                    "Missing expected columns: "
                    f"{sorted(missing_headers)}"
                )

            sample = pd.read_csv(
                path,
                skiprows=1,
                nrows=1,
                encoding="utf-8-sig",
            )

            if sample.empty:
                raise ValueError(
                    "CSV contains headers but no data rows."
                )

            log(f"  PASS raw export: {path.name}")

        except Exception as exc:
            raise RuntimeError(
                f"Raw export preflight failed for {path.name}: {exc}"
            ) from exc

    return raw_files


# ---------------------------------------------------------
# Backup existing generated data and reports
# ---------------------------------------------------------

def create_backup():
    BACKUP_ROOT.mkdir(parents=True, exist_ok=False)

    backup_items = [
        ("data/processed", PROCESSED_DIR),
        ("reports", REPORTS_DIR),
    ]

    copied = []

    for relative_name, source in backup_items:
        if source.exists():
            destination = BACKUP_ROOT / relative_name

            shutil.copytree(
                source,
                destination,
                dirs_exist_ok=True,
            )

            copied.append(relative_name)

    log(f"Backup created: {BACKUP_ROOT}")

    for item in copied:
        log(f"  Backed up: {item}")

    if not copied:
        log("No existing processed data or reports required backup.")


# ---------------------------------------------------------
# Execute one script with live console/file logging
# ---------------------------------------------------------

def run_script(script_name):
    script_path = SCRIPTS_DIR / script_name

    log("")
    log("=" * 65)
    log(f"RUNNING: {script_name}")
    log("=" * 65)

    start = time.perf_counter()

    process = subprocess.Popen(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    if process.stdout is not None:
        for line in process.stdout:
            print(line, end="", flush=True)

            with LOG_FILE.open("a", encoding="utf-8") as file:
                file.write(line)

    return_code = process.wait()
    duration = time.perf_counter() - start

    if return_code != 0:
        raise RuntimeError(
            f"{script_name} failed with exit code "
            f"{return_code} after {duration:.2f} seconds."
        )

    log(
        f"SUCCESS: {script_name} "
        f"({duration:.2f} seconds)"
    )


# ---------------------------------------------------------
# Verify stage outputs
# ---------------------------------------------------------

def verify_outputs(output_paths):
    missing = []

    for relative_path in output_paths:
        path = PROJECT_ROOT / relative_path

        if not path.is_file():
            missing.append(relative_path)
        elif path.stat().st_size == 0:
            missing.append(
                f"{relative_path} (empty file)"
            )

    if missing:
        raise FileNotFoundError(
            "Expected pipeline outputs are missing or empty:\n"
            + "\n".join(missing)
        )

    for relative_path in output_paths:
        log(f"  VERIFIED: {relative_path}")


# ---------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------

def main():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    log("=" * 65)
    log("RAJASTHAN MANDI INTELLIGENCE PIPELINE")
    log("=" * 65)

    log(f"Python executable: {sys.executable}")
    log(f"Python version: {sys.version.split()[0]}")
    log(f"Execution log: {LOG_FILE}")

    # Preflight before modifying generated outputs.
    log("\n--- PREFLIGHT ---")

    check_project_structure()
    check_raw_exports()

    # Back up existing generated outputs before rebuilding.
    log("\n--- BACKUP ---")

    create_backup()

    # Execute stages in dependency order.
    log("\n--- PIPELINE EXECUTION ---")

    total_stages = len(PIPELINE_STAGES)

    for index, stage in enumerate(PIPELINE_STAGES, start=1):
        log("")
        log(
            f"STAGE {index}/{total_stages}: "
            f"{stage['name']}"
        )

        run_script(stage["script"])
        verify_outputs(stage["outputs"])

    # Final automated regression suite.
    log("")
    log("=" * 65)
    log("FINAL REGRESSION TEST SUITE")
    log("=" * 65)

    run_script_for_tests = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "-v",
        ],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    if run_script_for_tests.stdout is not None:
        for line in run_script_for_tests.stdout:
            print(line, end="", flush=True)

            with LOG_FILE.open("a", encoding="utf-8") as file:
                file.write(line)

    test_return_code = run_script_for_tests.wait()

    if test_return_code != 0:
        raise RuntimeError(
            "The final pytest regression suite failed."
        )

    log("\n" + "=" * 65)
    log("PIPELINE COMPLETED SUCCESSFULLY")
    log("=" * 65)

    log(f"Stages completed: {total_stages}/{total_stages}")
    log("Regression suite: PASSED")
    log(f"Backup location: {BACKUP_ROOT}")
    log(f"Execution log: {LOG_FILE}")


if __name__ == "__main__":
    try:
        main()

    except Exception as exc:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

        log("")
        log("=" * 65)
        log("PIPELINE FAILED")
        log("=" * 65)
        log(f"Error: {exc}")
        log(traceback.format_exc())
        log("Existing files were not automatically deleted.")
        log("Review the backup and execution log before retrying.")

        sys.exit(1)
