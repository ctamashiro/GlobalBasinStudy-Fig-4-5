import pandas as pd
import glob
import os

INPUT_FOLDER = "csv_files"
OUTPUT_FOLDER = "MODIS_ET_Basin_Monthly_Weighted"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for csv_file in glob.glob(os.path.join(INPUT_FOLDER, "*.csv")):
    basin = os.path.basename(csv_file).replace(".csv", "")
    print(f"Processing {basin}")

    df = pd.read_csv(csv_file)
    df["date"] = pd.to_datetime(df["date"])

    records = []

    for year in df["date"].dt.year.unique():
        df_year = df[df["date"].dt.year == year]

        # initialize monthly accumulators (same as xr.zeros_like)
        monthly = {
            1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0,
            5: 0.0, 6: 0.0, 7: 0.0, 8: 0.0,
            9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0
        }

        leap = (year % 4 == 0)

        for _, r in df_year.iterrows():
            et = r["mean"]
            month = r["date"].month
            day = r["date"].day

            # ---- LEAP YEAR LOGIC ----
            if leap:

                if month == 1:
                    if day == 25:
                        monthly[1] += et * 0.875
                        monthly[2] += et * 0.125
                    else:
                        monthly[1] += et

                elif month == 2:
                    if day == 26:
                        monthly[2] += et * 0.500
                        monthly[3] += et * 0.500
                    else:
                        monthly[2] += et

                elif month == 3:
                    if day == 29:
                        monthly[3] += et * 0.375
                        monthly[4] += et * 0.625
                    else:
                        monthly[3] += et

                elif month == 4:
                    if day == 30:
                        monthly[4] += et * 0.125
                        monthly[5] += et * 0.875
                    else:
                        monthly[4] += et

                elif month == 5:
                    monthly[5] += et

                elif month == 6:
                    if day == 25:
                        monthly[6] += et * 0.750
                        monthly[7] += et * 0.250
                    else:
                        monthly[6] += et

                elif month == 7:
                    if day == 27:
                        monthly[7] += et * 0.625
                        monthly[8] += et * 0.375
                    else:
                        monthly[7] += et

                elif month == 8:
                    if day == 28:
                        monthly[8] += et * 0.500
                        monthly[9] += et * 0.500
                    else:
                        monthly[8] += et

                elif month == 9:
                    if day == 29:
                        monthly[9] += et * 0.250
                        monthly[10] += et * 0.750
                    else:
                        monthly[9] += et

                elif month == 10:
                    if day == 31:
                        monthly[10] += et * 0.125
                        monthly[11] += et * 0.875
                    else:
                        monthly[10] += et

                elif month == 11:
                    if day == 24:
                        monthly[11] += et * 0.875
                        monthly[12] += et * 0.125
                    else:
                        monthly[11] += et

                elif month == 12:
                    monthly[12] += et

            # ---- NON-LEAP YEAR LOGIC ----
            else:

                if month == 1:
                    if day == 24:
                        monthly[1] += et * 0.875
                        monthly[2] += et * 0.125
                    else:
                        monthly[1] += et

                elif month == 2:
                    if day == 26:
                        monthly[2] += et * 0.375
                        monthly[3] += et * 0.625
                    else:
                        monthly[2] += et

                elif month == 3:
                    if day == 30:
                        monthly[3] += et * 0.250
                        monthly[4] += et * 0.750
                    else:
                        monthly[3] += et

                elif month == 4:
                    monthly[4] += et

                elif month == 5:
                    if day == 25:
                        monthly[5] += et * 0.875
                        monthly[6] += et * 0.125
                    else:
                        monthly[5] += et

                elif month == 6:
                    if day == 26:
                        monthly[6] += et * 0.625
                        monthly[7] += et * 0.375
                    else:
                        monthly[6] += et

                elif month == 7:
                    if day == 28:
                        monthly[7] += et * 0.500
                        monthly[8] += et * 0.500
                    else:
                        monthly[7] += et

                elif month == 8:
                    if day == 29:
                        monthly[8] += et * 0.375
                        monthly[9] += et * 0.625
                    else:
                        monthly[8] += et

                elif month == 9:
                    if day == 30:
                        monthly[9] += et * 0.125
                        monthly[10] += et * 0.875
                    else:
                        monthly[9] += et

                elif month == 10:
                    monthly[10] += et

                elif month == 11:
                    if day == 25:
                        monthly[11] += et * 0.750
                        monthly[12] += et * 0.250
                    else:
                        monthly[11] += et

                elif month == 12:
                    monthly[12] += et

        for m in range(1, 13):
            records.append({
                "year": year,
                "month": m,
                "monthly_et_mm": monthly[m]
            })

    out = os.path.join(
        OUTPUT_FOLDER,
        basin.replace("2002_2025", "monthly_2002_2025_weighted") + ".csv"
    )

    pd.DataFrame(records).to_csv(out, index=False)
    print(f"Saved {out}")

print(" Monthly ET conversion (original-script-equivalent) complete.")
