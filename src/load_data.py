"""
load_data.py

Reads the raw Card & Krueger (1994) survey data (public.dat) and produces
a clean pandas DataFrame with proper column names, correct missing-value
handling, and the derived FTE employment variables for both waves.

Run from the project root:
    python3 src/load_data.py
"""

import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Paths
# ---------------------------------------------------------------------------
# __file__ is this script's own location. .resolve() makes it absolute.
# .parent.parent walks up two levels: src/load_data.py -> src/ -> project root.
# Using this instead of a hardcoded path means the script works no matter
# which directory you happen to run it from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "public.dat"
OUTPUT_PATH = PROJECT_ROOT / "output" / "clean_data.csv"

# ---------------------------------------------------------------------------
# 2. Column names, in the exact order they appear in public.dat
#    (from the codebook in docs/)
# ---------------------------------------------------------------------------
COLUMN_NAMES = [
    "SHEET", "CHAIN", "CO_OWNED", "STATE",
    "SOUTHJ", "CENTRALJ", "NORTHJ", "PA1", "PA2", "SHORE",
    "NCALLS", "EMPFT", "EMPPT", "NMGRS", "WAGE_ST", "INCTIME", "FIRSTINC",
    "BONUS", "PCTAFF", "MEALS", "OPEN", "HRSOPEN", "PSODA", "PFRY", "PENTREE",
    "NREGS", "NREGS11",
    "TYPE2", "STATUS2", "DATE2", "NCALLS2", "EMPFT2", "EMPPT2", "NMGRS2",
    "WAGE_ST2", "INCTIME2", "FIRSTIN2", "SPECIAL2", "MEALS2", "OPEN2R",
    "HRSOPEN2", "PSODA2", "PFRY2", "PENTREE2", "NREGS2", "NREGS112",
]


def load_raw_data() -> pd.DataFrame:
    """Read public.dat into a DataFrame with proper names and NaNs."""
    df = pd.read_csv(
        RAW_DATA_PATH,
        sep=r"\s+",           # fields are separated by any run of whitespace
        header=None,          # the raw file has no header row
        names=COLUMN_NAMES,   # assign our own names, in codebook order
        na_values=".",        # the raw file uses "." to mean missing
    )
    return df


def add_fte_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full-time-equivalent employment, wave 1 and wave 2.
    FTE = full-time employees + managers + 0.5 * part-time employees
    (Card & Krueger 1994, p. 775)
    """
    df["FTE"] = df["EMPFT"] + df["NMGRS"] + 0.5 * df["EMPPT"]
    df["FTE2"] = df["EMPFT2"] + df["NMGRS2"] + 0.5 * df["EMPPT2"]
    return df


def apply_closure_rules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Paper's rule for closed stores (Card & Krueger 1994, p. 775):
      - Permanently closed (STATUS2 == 3): FTE2 set to 0, not missing.
      - Temporarily closed (STATUS2 in {2, 4, 5}): FTE2 stays missing.
    """
    permanently_closed = df["STATUS2"] == 3
    df.loc[permanently_closed, "FTE2"] = 0.0
    return df


def main():
    df = load_raw_data()
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns.")

    df = add_fte_columns(df)
    df = apply_closure_rules(df)

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved cleaned data to {OUTPUT_PATH}")

    # Sanity check against the paper: Table 2 reports wave-1 mean FTE
    # of 20.4 in NJ and 23.3 in PA.
    print(df.groupby("STATE")["FTE"].mean())


if __name__ == "__main__":
    main()
    