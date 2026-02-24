import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# PATHS

SCRIPT_DIR = Path(__file__).resolve().parent

# Change per basin
BASIN = "Murray_Darling"

DATA_FOLDER = "2000-2024"

CSV_FILE = SCRIPT_DIR / "csv" / DATA_FOLDER / f"MODIS_ET_{BASIN}_2000_2024.csv"

OUT_DIR = SCRIPT_DIR / "figures"
OUT_DIR.mkdir(exist_ok=True)

print("\nLooking for file at:")
print(CSV_FILE)

if not CSV_FILE.exists():
    raise FileNotFoundError(f"\nFile not found:\n{CSV_FILE}\n")


# LOAD DATA (RAW ET)

df = pd.read_csv(CSV_FILE)

print("\nColumns in file:")
print(df.columns)

# Create datetime column
df["date"] = pd.to_datetime(
    dict(year=df["year"], month=df["month"], day=1)
)

df = df.sort_values("date")

# Restrict to paper period
df = df[(df["date"].dt.year >= 2000) & (df["date"].dt.year <= 2015)]


# COMPUTE MONTHLY CLIMATOLOGY (2000–2015)
# Assumes raw ET column is named "ET_mm"


climatology = (
    df.groupby(df["date"].dt.month)["ET_mm"]
    .mean()
)

# Compute anomaly
df["ET_anomaly_mm"] = df.apply(
    lambda row: row["ET_mm"] - climatology[row["date"].month],
    axis=1
)


# 3-MONTH CENTERED SMOOTHING (Paper Style)

df["ET_smooth"] = (
    df["ET_anomaly_mm"]
    .rolling(3, center=True)
    .mean()
)

df = df.dropna()


# PLOT

fig, ax = plt.subplots(figsize=(14, 4))

ax.plot(
    df["date"],
    df["ET_smooth"],
    color="black",
    linewidth=0.9,
    marker="o",
    markersize=3,
    markerfacecolor="white",
    markeredgewidth=0.8
)

# Zero line
ax.axhline(0, color="black", linewidth=1)

# Paper-style y-axis
ax.set_ylim(-30, 30)

# January ticks
jan = df[df["date"].dt.month == 1]

ax.set_xticks(jan["date"])
ax.set_xticklabels([f"Jan-{d.year % 100:02d}" for d in jan["date"]])

ax.scatter(
    jan["date"],
    [0] * len(jan),
    marker="|",
    s=140,
    color="black",
    linewidths=1.6
)


# STYLE

title_name = BASIN.replace("_", " ")

ax.set_title(f"MODIS Evapotranspiration Anomaly – {title_name} (2000–2015)")
ax.set_ylabel("Evapotranspiration Anomaly (mm)")
ax.set_xlabel("Year")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.yaxis.grid(True, linestyle="--", alpha=0.3)

plt.tight_layout()


# SAVE

plt.savefig(OUT_DIR / f"Fig4_{BASIN}_Anomaly_2000_2015.png", dpi=300)
plt.savefig(OUT_DIR / f"Fig4_{BASIN}_Anomaly_2000_2015.pdf")

plt.show()
