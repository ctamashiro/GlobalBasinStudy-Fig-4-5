from pathlib import Path
import rioxarray
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# PATHS

SCRIPT_DIR = Path(__file__).resolve().parent

RASTER_DIR = SCRIPT_DIR / "raster_data"
SHAPE_DIR  = SCRIPT_DIR.parent / "basin_shapefiles"
FIG_DIR    = SCRIPT_DIR / "figures"

FIG_DIR.mkdir(exist_ok=True)

DRY_FILE = RASTER_DIR / "MODIS_ET_Anomaly_Mekong_2005_3.tif"
WET_FILE = RASTER_DIR / "MODIS_ET_Anomaly_Mekong_2011_9.tif"

GEOJSON_FILE = SHAPE_DIR / "Mekong.geojson"

print("Dry exists:", DRY_FILE.exists())
print("Wet exists:", WET_FILE.exists())
print("GeoJSON exists:", GEOJSON_FILE.exists())

# LOAD BASIN

basins = gpd.read_file(GEOJSON_FILE)

if basins.crs != "EPSG:4326":
    basins = basins.to_crs("EPSG:4326")

basin_geoms = basins.geometry.values

# FIXED ±10 SCALE (MATCH PAPER EXACTLY)

vmin = -10
vmax = 10

norm = colors.TwoSlopeNorm(
    vmin=vmin,
    vcenter=0,
    vmax=vmax
)

# PAPER MATCH COLORMAP
# Negative = Red
# 0 = White
# Positive = Blue
cmap = plt.get_cmap("RdYlBu")


# FUNCTION TO PLOT

def plot_map(tif_path, label, output_name):

    da = rioxarray.open_rasterio(tif_path).squeeze()

    if da.rio.crs is None:
        da = da.rio.write_crs("EPSG:4326")

    da = da.rio.reproject("EPSG:4326")

    clipped = da.rio.clip(basin_geoms, basins.crs, drop=True)

    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())

    clipped.plot(
        ax=ax,
        cmap=cmap,
        norm=norm,
        add_colorbar=True,
        robust=False,
        cbar_kwargs={
            "label": "Evapotranspiration Anomaly (mm)",
            "ticks": [-10, -5, 0, 5, 10],
            "extend": "both"
        }
    )

    # Basin boundary
    basins.boundary.plot(ax=ax, edgecolor="black", linewidth=2)

    # Map features
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.LAND, facecolor="lightgray", alpha=0.5)

    ax.set_title(f"Mekong Basin ET Anomaly ({label})")

    # Mekong geographic extent
    ax.set_extent([92, 110, 5, 30])

    outfile = FIG_DIR / output_name
    plt.savefig(outfile, dpi=400, bbox_inches="tight")
    plt.close()

    print(f"Saved: {outfile}")

# GENERATE BOTH MAPS

plot_map(DRY_FILE, "DRY", "Fig4_Mekong_DRY.png")
plot_map(WET_FILE, "WET", "Fig4_Mekong_WET.png")