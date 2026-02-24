import ee
import json

ee.Initialize(project='piechota-et-research')


# SETTINGS

START_YEAR = 2000
END_YEAR   = 2024
BASIN_NAME = "Yangtze"   # change per run
GEOJSON = f"../basin_shapefiles/Yangtze.geojson"


# LOAD BASIN

with open(GEOJSON) as f:
    basin_geojson = json.load(f)

basin = ee.FeatureCollection(basin_geojson)


# MODIS ET (MOD16A2GF, 8-day, kg/m²)

et = (
    ee.ImageCollection("MODIS/061/MOD16A2GF")
    .select("ET")
    .filterDate(f"{START_YEAR}-01-01", f"{END_YEAR}-12-31")
)

# Convert to monthly mm
def monthly_et(year, month):
    start = ee.Date.fromYMD(year, month, 1)
    end   = start.advance(1, "month")

    img = et.filterDate(start, end).sum().multiply(0.1)  # mm
    mean = img.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=basin.geometry(),
        scale=500,
        maxPixels=1e13
    )

    return ee.Feature(None, {
        "year": year,
        "month": month,
        "ET_mm": mean.get("ET")
    })

features = []
for y in range(START_YEAR, END_YEAR + 1):
    for m in range(1, 13):
        features.append(monthly_et(y, m))

fc = ee.FeatureCollection(features)


# EXPORT TO DRIVE

task = ee.batch.Export.table.toDrive(
    collection=fc,
    description=f"MODIS_ET_{BASIN_NAME}_{START_YEAR}_{END_YEAR}",
    fileFormat="CSV"
)

task.start()
print("Export started — check Earth Engine Tasks tab")
