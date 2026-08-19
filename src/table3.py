"""
table3.py

Reproduces Table 3: Average Employment Per Store Before and After the Rise
in New Jersey Minimum Wage (columns i, ii, iii only: PA / NJ / Difference).

Run from the project root:
    python3 src/table3.py

Saves output/table3.md
"""

import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

pd.set_option("display.max_colwidth", None)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEAN_DATA_PATH = PROJECT_ROOT / "output" / "clean_data.csv"

df = pd.read_csv(CLEAN_DATA_PATH)

# Row 5's sample: same as the balanced subsample, but temporarily closed
# stores get FTE2 set to 0 instead of staying missing.
df_row5 = df.copy()
temporarily_closed = df["STATUS2"].isin([2, 4, 5])
df_row5.loc[temporarily_closed, "FTE2"] = 0.0


def avg_fte_employment_full_sample(df: pd.DataFrame, state, col: str):
    """
    Mean and standard error of one FTE column (e.g. "FTE" or "FTE2"),
    for one state (0=PA, 1=NJ), using all non-missing observations.
    Used for Table 3 rows 1 and 2.
    """
    stores_state = df[df["STATE"] == state]
    fte_state_wave = stores_state[col]
    avg_fte_state_wave = fte_state_wave.mean()
    se_fte_state_wave = fte_state_wave.sem()
    return avg_fte_state_wave, se_fte_state_wave


def change_in_mean_full_sample(df: pd.DataFrame, state):
    """
    Change in mean FTE (wave 2 - wave 1) for one state, using "all
    available observations" for the mean (each wave's own non-missing
    set), but a paired per-store difference for the SE (balanced
    subsample only. 
    Used for Table 3 row 3.
    """
    stores_state = df[df["STATE"] == state]
    change_fte_state = stores_state["FTE Change"] = stores_state["FTE2"] - stores_state["FTE"]
    se_change_mean_fte_state = change_fte_state.sem()
    avg1, se1 = avg_fte_employment_full_sample(df, state, "FTE")
    avg2, se2 = avg_fte_employment_full_sample(df, state, "FTE2")
    avg_change_mean_fte_state = avg2 - avg1
    return avg_change_mean_fte_state, se_change_mean_fte_state


def change_in_mean_balanced_sample(df: pd.DataFrame, state):
    """
    Change in mean FTE (wave 2 - wave 1) for one state, restricted to
    stores with non-missing FTE in BOTH waves (the "balanced subsample").
    Both mean and SE come from the same per-store paired difference.
    Used for Table 3 rows 4 and 5 (row 5 via df_row5 instead of df).
    """
    stores_state = df[df["STATE"] == state]
    change_fte_state = stores_state["FTE Change"] = stores_state["FTE2"] - stores_state["FTE"]
    avg_change_mean_fte_state = change_fte_state.mean()
    se_change_mean_fte_state = change_fte_state.sem()
    return avg_change_mean_fte_state, se_change_mean_fte_state


def diff_nj_pa(results_pa, results_nj):
    """
    Given two (mean, se) results for independent groups (PA and NJ),
    return their difference and combined standard error. Works on the
    output of any of the three functions above. PA and NJ are always
    independent of each other, regardless of which function produced
    each side's numbers.
    """
    avg_pa, se_pa = results_pa
    avg_nj, se_nj = results_nj
    avg_diff = avg_nj - avg_pa
    se_diff = np.sqrt(se_nj**2 + se_pa**2)
    return avg_diff, se_diff


def format_results(results):
    """Format a (mean, se) tuple as 'mean (se)', e.g. '23.33 (1.35)'."""
    avg, se = results
    return f"{avg:.2f} ({se:.2f})"


# --- Compute every (PA, NJ, Diff) triple for all five rows ---------------
results_pa_r1 = avg_fte_employment_full_sample(df, 0, col="FTE")
results_nj_r1 = avg_fte_employment_full_sample(df, 1, col="FTE")
results_diff_r1 = diff_nj_pa(results_pa_r1, results_nj_r1)

results_pa_r2 = avg_fte_employment_full_sample(df, 0, col="FTE2")
results_nj_r2 = avg_fte_employment_full_sample(df, 1, col="FTE2")
results_diff_r2 = diff_nj_pa(results_pa_r2, results_nj_r2)

results_pa_r3 = change_in_mean_full_sample(df, 0)
results_nj_r3 = change_in_mean_full_sample(df, 1)
results_diff_r3 = diff_nj_pa(results_pa_r3, results_nj_r3)

results_pa_r4 = change_in_mean_balanced_sample(df, 0)
results_nj_r4 = change_in_mean_balanced_sample(df, 1)
results_diff_r4 = diff_nj_pa(results_pa_r4, results_nj_r4)

results_pa_r5 = change_in_mean_balanced_sample(df_row5, 0)
results_nj_r5 = change_in_mean_balanced_sample(df_row5, 1)
results_diff_r5 = diff_nj_pa(results_pa_r5, results_nj_r5)

# --- Assemble into a table ------------------------------
row1 = {"Row": "FTE Employment Before, all available observations",
        "PA (i)": format_results(results_pa_r1),
        "NJ (ii)": format_results(results_nj_r1),
        "Difference (NJ-PA) (iii)": format_results(results_diff_r1)}

row2 = {"Row": "FTE Employment After, all available observations",
        "PA (i)": format_results(results_pa_r2),
        "NJ (ii)": format_results(results_nj_r2),
        "Difference (NJ-PA) (iii)": format_results(results_diff_r2)}

row3 = {"Row": "Change in Mean FTE employment, all available observations",
        "PA (i)": format_results(results_pa_r3),
        "NJ (ii)": format_results(results_nj_r3),
        "Difference (NJ-PA) (iii)": format_results(results_diff_r3)}

row4 = {"Row": "Change in Mean FTE employment, balanced sample of stores",
        "PA (i)": format_results(results_pa_r4),
        "NJ (ii)": format_results(results_nj_r4),
        "Difference (NJ-PA) (iii)": format_results(results_diff_r4)}

row5 = {"Row": "Change in Mean FTE employment, setting FTE at temporarily closed stores to 0",
        "PA (i)": format_results(results_pa_r5),
        "NJ (ii)": format_results(results_nj_r5),
        "Difference (NJ-PA) (iii)": format_results(results_diff_r5)}

table3 = pd.DataFrame([row1, row2, row3, row4, row5])

print(table3.to_string(index=False))

table3.to_markdown(PROJECT_ROOT / "output" / "table3.md", index=False)

"""
# to print the output of the table3.py in lines

def print_avg_fte_employment(label: str, avg: float, se: float):
	print(f"{label} {avg:.2f} ({se:.2f})")

print_avg_fte_employment(f"PA FTE Employment Before, all available observations:", *avg_fte_employment_full_sample(df, 0, col="FTE"))
print_avg_fte_employment(f"NJ FTE Employment Before, all available observations:", *avg_fte_employment_full_sample(df, 1, col="FTE"))
print_avg_fte_employment(f"Difference (NJ-PA) FTE Employment Before, all available observations:", *diff_nj_pa(results_pa_r1, results_nj_r1))
print_avg_fte_employment(f"PA FTE Employment After, all available observations:", *avg_fte_employment_full_sample(df, 0, col="FTE2"))
print_avg_fte_employment(f"NJ FTE Employment After, all available observations:", *avg_fte_employment_full_sample(df, 1, col="FTE2"))
print_avg_fte_employment(f"Difference (NJ-PA) FTE Employment After, all available observations:", *diff_nj_pa(results_pa_r2, results_nj_r2))
print_avg_fte_employment(f"PA Change in Mean FTE employment, all available observations:", *change_in_mean_full_sample(df, 0))
print_avg_fte_employment(f"NJ Change in Mean FTE employment, all available observations:", *change_in_mean_full_sample(df, 1))
print_avg_fte_employment(f"Difference (NJ-PA) Change in Mean FTE Employment, all available observations:", *diff_nj_pa(results_pa_r3, results_nj_r3))
print_avg_fte_employment(f"PA Change in Mean FTE employment, balanced sample of stores:", *change_in_mean_balanced_sample(df, 0))
print_avg_fte_employment(f"NJ Change in Mean FTE employment, balanced sample of stores:", *change_in_mean_balanced_sample(df, 1))
print_avg_fte_employment(f"Difference (NJ-PA) FTE Change in Mean, balanced sample of stores:", *diff_nj_pa(results_pa_r4, results_nj_r4))
print_avg_fte_employment(f"PA Change in Mean FTE employment, setting FTE at temporarily closed stores to 0:", *change_in_mean_balanced_sample(df_row5, 0))
print_avg_fte_employment(f"NJ Change in Mean FTE employment, setting FTE at temporarily closed stores to 0:", *change_in_mean_balanced_sample(df_row5, 1))
print_avg_fte_employment(f"Difference (NJ-PA) FTE Change in Mean, setting FTE at temporarily closed stores to 0:", *diff_nj_pa(results_pa_r5, results_nj_r5))
"""