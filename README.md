# Replicating Card & Krueger (1994): Minimum Wages and Employment

A from-scratch Python replication of David Card and Alan B. Krueger's
["Minimum Wages and Employment: A Case Study of the Fast-Food Industry in
New Jersey and Pennsylvania"](https://www.jstor.org/stable/2118030)
(American Economic Review, 84(4), 772-793, 1994). The paper uses a natural
experiment, New Jersey's 1992 minimum wage increase with Pennsylvania as a
control group, to test whether minimum wage increases reduce employment.

This project uses the paper's original public data release (`public.dat`,
410 fast-food stores surveyed before and after the wage increase) and
rebuilds its descriptive statistics, core difference-in-differences
result, and regression tables in Python. Every number is checked against
the published paper.

## Project structure

```
ck1994-replication/
├── data/raw/public.dat          # original survey data (unmodified)
├── docs/                        # paper PDF + variable codebook
├── src/                         # analysis scripts, one per table/figure
├── output/                      # generated CSVs, tables, figures
├── requirements.txt
└── README.md
```

## Setup

```bash
git clone https://github.com/thibjn/Card_Krueger_1994_Replication.git
cd ck1994-replication
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the analysis

Each script is self-contained and reads from `output/clean_data.csv`,
which is produced by `load_data.py` and must be run first.

```bash
python3 src/load_data.py     # parses public.dat -> output/clean_data.csv
python3 src/table3.py        # core difference-in-differences result -> output/table3.md
```

## Progress

| Table / Figure | Status | Notes |
|---|---|---|
| Table 1, sample design and response rates | In progress | Partial, see limitations below |
| Table 2, means of key variables | In progress | |
| Figure 1, distribution of starting wages | In progress | |
| Table 3, employment before/after (columns i-iii) | Done | All values match paper |
| Table 4, regression-adjusted models | Not started | |
| Table 5, specification tests | Will not be replicated | |
| Tables 6 to 8 | Will not be replicated | |

## Limitations and Explanations

**1. Table 1's full sample frame can't be reproduced from `public.dat`.**
The raw data file only contains the 410 stores that completed a Wave 1
interview. The paper's Table 1 also reports the full sample frame that was
contacted (473 stores) and the 63 that refused outright. That information
was never in the public data release, so those specific rows of Table 1
are not reproducible here. Only the Wave 1 to Wave 2 transition (closures,
response rate) among the 410 stores we do have can be reproduced.

**2. `FTE` (full-time-equivalent employment).** Defined directly from the
paper's p. 775. `FTE = EMPFT + NMGRS + 0.5 * EMPPT`. This is full-time
employees plus managers, plus half of part-time employees.

**3. `PCT_FT` (percentage full-time employees) is genuinely non-obvious.**
The intuitive formula, `(EMPFT + NMGRS) / (EMPFT + NMGRS + EMPPT)`, does
not match the paper's reported values. The actual formula, found by
testing candidates numerically against the paper's reported 32.8% (NJ)
and 35.0% (PA), is the following.
```
PCT_FT = EMPFT / FTE * 100,  where FTE = EMPFT + NMGRS + 0.5*EMPPT
```
The numerator excludes managers and only counts non-manager full-timers,
while the denominator is the FTE-weighted total, with managers at full
weight and part-timers at half weight.

**4. `PRICE_MEAL` (price of a "full meal").** The paper describes this
quantity in two places. On p. 775 it is described as "a 'full meal'
(medium soda, small fries, and an entree)," and on p. 787 it is described
as "the after-tax price of a medium soda, a small order of french fries,
and a main course." Both describe the same quantity. The p. 775 wording
is used here because it uses the term "entree," which matches the
dataset's `PENTREE` variable directly. `PRICE_MEAL = PSODA + PFRY +
PENTREE`, the medium soda, small fries, and entree prices added together.

**5. Closed-store handling in `FTE2`.** Per the paper's Table 2 notes,
permanently closed stores (`STATUS2 == 3`) get `FTE2` set to exactly 0,
counted as a real employment loss. Temporarily closed stores (`STATUS2`
in `{2, 4, 5}`, covering renovation, highway construction, and fire) are
left as missing. This is implemented once in `load_data.py` and inherited
by every downstream table automatically.

**6. Table 3, Row 3's standard error is an approximation.** Row 3
("Change in mean FTE employment, all available observations") computes
its mean using each wave's own independent set of non-missing stores,
which can differ in composition from wave to wave. A statistically valid
paired-difference standard error requires the same stores in both waves.
The paper doesn't specify how it resolves this. This replication uses the
balanced-subsample (Row 4) paired standard error as a documented
approximation for Row 3, rather than using an invalid formula silently.

**7. Independent versus paired standard errors.** Table 3's column (iii)
compares New Jersey to Pennsylvania, which are two separate, independent
groups of stores. No store appears in both states, so there is no
correlation between a NJ store's employment and a PA store's employment.
For this comparison the standard error is computed with the
independent-samples formula, `SE(diff) = sqrt(SE_NJ^2 + SE_PA^2)`.

Rows 3, 4, and 5 of columns (i) and (ii) are a different situation. Each
of these rows compares wave 1 employment to wave 2 employment within the
same set of stores. A store's wave 1 and wave 2 employment levels are not
independent of each other. A store that is large in February is likely
still large in November, and a store that is small in February is likely
still small in November, so the two waves share common information about
each store's size. This means the two samples are correlated.

Because of this correlation, using the independent-samples formula for a
within-store change would be wrong. The correct variance of a difference
between two correlated variables is `Var(X - Y) = Var(X) + Var(Y) - 2 *
Cov(X, Y)`, and ignoring the covariance term overstates the true
variance. To handle this correctly, the change in employment is computed
per store first, as a new column equal to wave 2 employment minus wave 1
employment for that same store. The mean and standard error are then
computed directly on this column of per-store changes. This works because
the covariance between the two waves is automatically built into the
variance of the per-store difference, since each store's own pair of
values is never separated into two independent groups before the
subtraction happens.

## Data source

Card, D. and Krueger, A.B. (1994). Public data release accompanying
"Minimum Wages and Employment: A Case Study of the Fast-Food Industry in
New Jersey and Pennsylvania," available at
[https://davidcard.berkeley.edu/data_sets.html](https://davidcard.berkeley.edu/data_sets.html).
Codebook cross-referenced against the
[MHE Data Archive](https://economics.mit.edu/people/faculty/josh-angrist/mhe-data-archive).