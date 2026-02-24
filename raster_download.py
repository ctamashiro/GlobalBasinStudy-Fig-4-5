import ee
import json

ee.Initialize(project='piechota-et-research')

# SETTINGS

BASELINE_START = 2000
BASELINE_END   = 2015

TARGET_YEAR  = 2011
TARGET_MONTH = 9   # change to dry/wet month

BASIN_NAME = "Mekong"
GEOJSON = f"../basin_shapefiles/{BASIN_NAME}.geojson"

# LOAD BASIN

with open(GEOJSON) as f:
    basin_geojson = json.load(f)

basin = ee.FeatureCollection(basin_geojson)
geometry = basin.geometry()

# LOAD MODIS ET (8-day → mm)

et_8day = (
    ee.ImageCollection("MODIS/061/MOD16A2GF")
    .select("ET")
    .filterDate(f"{BASELINE_START}-01-01", f"{BASELINE_END}-12-31")
    .map(lambda img: img.multiply(0.1)
         .copyProperties(img, ["system:time_start"]))
)

# FUNCTION: CONVERT TO MONTHLY TOTAL

def monthly_sum(year, month):
    start = ee.Date.fromYMD(year, month, 1)
    end   = start.advance(1, 'month')
    
    monthly = (
        et_8day
        .filterDate(start, end)
        .sum()   # IMPORTANT → sum not mean
        .set("year", year)
        .set("month", month)
        .set("system:time_start", start.millis())
    )
    
    return monthly

# BUILD FULL MONTHLY COLLECTION (2000–2015)

years  = ee.List.sequence(BASELINE_START, BASELINE_END)
months = ee.List.sequence(1, 12)

monthly_collection = ee.ImageCollection.fromImages(
    years.map(lambda y:
        months.map(lambda m:
            monthly_sum(y, m)
        )
    ).flatten()
)


# COMPUTE MONTHLY CLIMATOLOGY

def climatology(month):
    return (
        monthly_collection
        .filter(ee.Filter.eq("month", month))
        .mean()
        .set("month", month)
    )

climatology_collection = ee.ImageCollection(
    months.map(climatology)
)

# SELECT TARGET MONTH IMAGE

target = (
    monthly_collection
    .filter(ee.Filter.eq("year", TARGET_YEAR))
    .filter(ee.Filter.eq("month", TARGET_MONTH))
    .first()
)

climo_month = (
    climatology_collection
    .filter(ee.Filter.eq("month", TARGET_MONTH))
    .first()
)

# COMPUTE ANOMALY

anomaly = target.subtract(climo_month)

# MASK TO BASIN


anomaly_clipped = anomaly.clip(geometry)

# EXPORT

task = ee.batch.Export.image.toDrive(
    image=anomaly_clipped,
    description=f"MODIS_ET_Anomaly_{BASIN_NAME}_{TARGET_YEAR}_{TARGET_MONTH}",
    folder="EarthEngine",
    fileNamePrefix=f"MODIS_ET_Anomaly_{BASIN_NAME}_{TARGET_YEAR}_{TARGET_MONTH}",
    region=geometry,
    scale=500,
    maxPixels=1e13
)

task.start()

print(" Monthly anomaly export started.")