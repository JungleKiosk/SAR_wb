# Water balance estimation using SAR, LAI, and meteorological data in Python + GoogleEarthEngine:

---

## Preprocessing Data & Analysis (Python + GEE)

| Step              | Objective                        | Output                      | Tool                             |
| ----------------- | ---------------------------------| --------------------------- | -------------------------------- |
| 1️ Setup & AOI     | Import study area                | `ee.Geometry` or shapefile  | `geemap`, `geopandas`            |
| 2️ Soil Texture    | Retrieve sand, silt, clay data   | Local raster or GEE         | SoilGrids via GEE                |
| 3️ SAR Data        | Sentinel-1 VV backscatter        | Time series raster          | GEE (`COPERNICUS/S1_GRD`)        |
| 4️ Soil Moisture   | VV ➜ % volumetric soil moisture | Soil moisture raster        | Empirical (calibrated) formula   |
| 5️ Vegetation      | LAI calculation or import        | Daily LAI series            | MODIS/Sentinel-2 LAI             |
| 6️ Meteorology     | Precipitation + ET0 data         | Daily meteorological series | NASA POWER / Open-Meteo          |
| 7️ Dynamic ETc     | ETc = ET0 × Kc(LAI)              | Daily ETc raster            | Python calculation               |
| 8️ Water Balance   | SM + rainfall – ETc              | Deficit (mm)                | Irrigation decision model        |

---

## Datasets & Requirements 

| Name                    | Dataset                                    | Source    |
| ----------------------- | ------------------------------------------ | --------- |
| Sentinel-1 VV           | `COPERNICUS/S1_GRD`                        | GEE       | 
| Sentinel-2 / MODIS LAI  | `COPERNICUS/S2_SR` or `MODIS/006/MCD15A3H` | GEE       | 
| Soil Texture            | `ISDAS/SoilGrids250m` (SAND, SILT, CLAY)   | GEE       | 
| Precipitation           | `NASA/POWER`, `CHIRPS`, `ERA5_LAND`        | GEE / API | 
| ET0                     | `ERA5_LAND`, `Open-Meteo`, `NASA/POWER`    | GEE / API | 
| AOI                     | Shapefile, GeoJSON                         | Local     |              |

---

| Library           | Purpose in Project                                                                                              |
| ----------------- | --------------------------------------------------------------------------------------------------------------- |
| `earthengine-api` | Provides access to Google Earth Engine from Python – for querying, filtering, and downloading satellite data.   |
| `geopandas`       | Handles geospatial vector data (e.g., shapefiles, field boundaries, AOIs) using a pandas-like interface.        |
| `pandas`          | Data manipulation and analysis – perfect for working with time series of soil moisture, precipitation, ET, etc. |
| `shapely`         | Underlying library for geometric operations (points, polygons, intersections); powers `geopandas`.              |
| `rasterio`        | Reads and writes raster datasets (e.g., GeoTIFFs) – useful for local processing of backscatter, LAI, SM maps.   |
| `matplotlib`      | Visualization of time series, charts, and static maps (e.g., water balance graphs, LAI evolution).              |
| `ipykernel`       | Enables interactive notebook execution, required for running Python kernels in Jupyter/VSCode/Colab.            |

---

# PROJECT setup

```bash
SAR_wb/
├─ assets/
│  └─ img/
│     └─ phenological_stages_and_leaf.png
├─ data/
│  ├─ local/
│  │  ├─ aoi.cpg
│  │  ├─ aoi.dbf
│  │  ├─ aoi.prj
│  │  ├─ aoi.qmd
│  │  ├─ aoi.shp
│  │  └─ aoi.shx
│  └─ outputs/
│     ├─ raster/
│     │   ├─ isric/
│     │   │    ├─ raster/
│     │   │    ├─ stack/
│     │   ├─ sentinel/
│     │
│     └─ shapefile/
│           ├─ isric/
├─ doc/
│  └─ remotesensing-17-00542.pdf
├─ notebook/
│  ├─ main.ipynb
│  └─ map_aoi.html
├─ scripts/ # This folder contains modular Python functions used across the project
│  ├─ __pycache__/
│  │  └─ aoi_loader.cpython-312.pyc
│  ├─ __init__.py
│  └─ aoi_loader.py
├─ venv/
├─ .gitignore
├─ README.md
└─ requirements.txt
```

---

# 1. Reference Documentation

**Reference**: Stanyer et al. (2025), _Remote Sensing_, 17(542),
**https://doi.org/10.3390/rs17030542**
<br>
doc path: SAR\doc\sar_moisture\remotesensing-17-00542.pdf

## Summary

### Title

**Soil Texture, Soil Moisture, and Sentinel-1 Backscattering: Towards the Retrieval of Field-Scale Soil Hydrological Properties**  
_Stanyer et al., Remote Sens. 2025, 17, 542_

### 1.1 Introduction

Soil moisture is a key variable for agriculture, climate regulation, and hydrology.  
Radar satellites (such as Sentinel-1) can monitor soil moisture regardless of cloud cover, but their accuracy is limited when **soil texture** (a key factor influencing the radar signal) **is not considered.**

This study investigates how **Sentinel-1 VV radar backscatter** varies in relation to both **soil moisture (SM)** and **soil texture**, using data from the ([COSMOS-UK](https://cosmos.ceh.ac.uk/data/near-real-time-data)) monitoring network.

### 2.1 Materials and Methods

#### 2.1.1 Study Sites

- 17 agricultural sites in the UK, part of the **COSMOS-UK** network.
- Each site includes a sensor that measures soil moisture using **cosmic-ray neutron probes**.

#### 2.1.2 Data Sources

- **Soil Moisture (SM)** from COSMOS (0–20 cm depth, ~200 m footprint).
- **VV Backscatter** from Sentinel-1 (C-band, GRD IW mode, 10 m resolution).
- **NDVI** from Sentinel-2, used to detect low-vegetation periods.
- **Soil Texture** from the UK Soil Observatory [UKSO](https://mapapps2.bgs.ac.uk/ukso/home.html).

#### 2.1.3 Methodology

- Agricultural **Field Sectors** were defined around each COSMOS sensor.
- **Low Vegetation Periods (L-periods)** were selected where **NDVI < 0.35**.
- Sentinel-1 data were **corrected for orbit-related biases**.
- For each sector and L-period:
  - A **linear regression** was performed between VV and SM.
  - The **slope** (sensitivity: %VWC per dB) was calculated.
- The slopes were then compared with the corresponding **soil texture classes**.

### 2.1.4 Results and Discussion

A **significant linear relationship** was found between SM and VV backscatter under bare-soil conditions:
- The **slope of the regression** varied depending on soil texture:
  - **Sandy soils** showed higher sensitivity (e.g., 1.69% VWC/dB).
  - **Clay soils** showed lower sensitivity (e.g., 4.81% VWC/dB).
- Slopes remained **stable over time** for each site, indicating their dependence on texture.

The results suggest that **VV backscatter can serve as a proxy for soil texture**, especially when combined with rainfall data and hydrological models.

### 2.1.5 Conclusions

- The influence of **soil texture** on the Sentinel-1 VV radar response to soil moisture has been confirmed.
- This paves the way for retrieving **soil hydrological properties** (e.g., infiltration potential) **using satellite data alone**.
- The approach can support:
  - Precision agriculture,
  - Field-scale water balance modelling,
  - Irrigation decision support systems.

### 2.1.6 Citation

> Stanyer, C., Seco-Rizo, I., Atzberger, C., Marti-Cardona, B.  
> _Soil Texture, Soil Moisture, and Sentinel-1 Backscattering: Towards the Retrieval of Field-Scale Soil Hydrological Properties_.  
> Remote Sens. 2025, 17, 542. https://doi.org/10.3390/rs17030542

---

# 2. Using Sentinel-1 SAR for Soil Moisture and Crop Irrigation Needs

When using **Sentinel-1 SAR imagery** for agricultural applications—especially to estimate **soil moisture (SM)** and calculate **crop irrigation requirements** — you must always **convert the backscatter values (VV in dB) into actual soil moisture (%)**.

---

# 3. THIS PROJECT: Dynamic Water Balance for Summer Crops (April–September in Italy)

## 3.1 intro

**Summer crops** refer to annual crops sown in spring and harvested in late summer or early autumn.
In the context of **Southern Europe and the Mediterranean basin** (e.g., Northern and Central Italy), this typically includes:

* 🌽 **Maize (corn)**
* 🌻 **Sunflower**
* 🌾 **Sorghum**
* 🍉 **Summer vegetables** (e.g., zucchini, tomato, melon...)

### 3.1.2 Geographic context: Italy

In **Italy**, summer crops are generally grown from **April to September**, depending on region and elevation:

| Area                              | Sowing      | Harvest          |
| ----------------------------------| ----------- | ---------------- |
| Northern Italy (Po river Valley)  | April–May   | August–September |
| Central Italy                     | March–April | July–August      |
| Southern Italy                    | March       | June–July        |

> The warm Mediterranean climate allows for a **full vegetative cycle** between spring and early autumn.

This project focuses on optimizing irrigation during this **growing window (gw)** using:

* Satellite-derived **soil moisture (VV from Sentinel-1)**
* Vegetation indicators like **LAI (from MODIS/Sentinel-2)**
* Meteorological data (precipitation, ET0)
* Soil texture maps

In this gw:

  * **LAI (Leaf Area Index)** is **low**.
  * Vegetation has **little influence on SAR signal** → backscatter (VV) is still mainly controlled by **soil moisture**.
* This is the **ideal window** to use **Sentinel-1 SAR (VV)** combined with a **hydrological model**.

**Phenological stages and leaf elongation in maize**

![Maize Growth Stages](/src/assets/img/phenological_stages_and_leaf.png)

---

## 3.2 Building the Model

### 3.2.1 Main Inputs

| Type          | Variable                            | Source                                    |
| ------------- | ----------------------------------- | ----------------------------------------- |
| Weather    | Precipitation, ET0, Temperature     | ERA5, NASA POWER, Open-Meteo              |
| SAR        | VV backscatter ➜ Soil Moisture (SM) | Sentinel-1                                |
| Vegetation | **LAI** (Leaf Area Index)           | Sentinel-2, MODIS, Copernicus Global Land |
| Crop Data  | Target SM threshold, Root depth     | Agronomic literature                      |

---

### 3.2.2 Water Balance Model Steps

1. **Estimate current soil moisture (SM)**
   SM = function(VV), calibrated for your soil texture (e.g. loamy or clayey).

2. **Estimate future SM**
   Water Balance:
   `SM_t+1 = SM_t + rainfall - evapotranspiration`

3. **Compute actual evapotranspiration (ETc)**
   `ETc = ET0 × Kc`
   But Kc (crop coefficient) **varies by growth stage**, so we can **derive Kc from LAI**!

---

## 3.3 How to Use **LAI** in the Model

### 3.3.1 Two Main Options

1. **Use LAI to infer phenological stage**

* Example ranges:

  * LAI < 0.5 → emergence/post-sowing
  * 0.5 < LAI < 1.5 → vegetative growth
  * 1.5 < LAI < 3 → flowering
* This allows you to apply a **dynamic Kc** based on the actual growth stage.

2. **Derive Kc directly from LAI**

> Empirical formula (e.g., Allen et al., 1998):

```python
Kc = 1.2 * (1 - exp(-0.5 * LAI))
```

* This lets you compute **ETc dynamically** based on actual canopy cover.
* Much more accurate than fixed calendars.

---

## 3.4 Final Outcome

You’ll be able to estimate, on a daily basis:

* Current soil moisture (from SAR)
* Water balance (from rainfall and ETc)
* Phenological stage (from LAI)
* Irrigation requirement (if SM < threshold)

---

### 3.4.1 Example Output Table

```python
Date       | LAI | SM (%) | ETc (mm) | Precip. | Deficit (mm)
-----------|-----|--------|----------|---------|--------------
2025-05-01 | 0.3 | 22.1   | 1.4      | 0.0     | 3.5
2025-05-04 | 0.9 | 19.2   | 2.0      | 2.5     | 0.0
2025-05-07 | 1.2 | 16.8   | 2.5      | 0.0     | 4.2
```

---

# 4. Methods

## 4.1 Download SAR tir from Sentinel-1 VV collection

To retrieve reliable SAR backscatter data for soil moisture estimation, this workflow utilizes the VV polarization from the `Sentinel-1 Ground Range Detected (GRD)` collection in `Interferometric Wide (IW)` mode.

The download and export process is automated and iterated `for` each month, resulting in one raster file per month, plus an additional seasonal average image (mean of all valid monthly composites). All exports are clipped to the predefined Area of Interest (AOI) and saved to Google Drive.

```python
for month in months:
    start = ee.Date(f'{year}-{month:02d}-01')
    end = start.advance(1, 'month')
    
    s1_month = ee.ImageCollection('COPERNICUS/S1_GRD') \
        .filterBounds(aoi) \
        .filterDate(start, end) \
        .filter(ee.Filter.eq('instrumentMode', 'IW')) \
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
        .select('VV')
```
For each month in the growing season (April to September), it is generated a monthly composite using the pixel-wise median of all available scenes.
The `median()` is chosen instead of the mean because it is more robust against speckle noise, acquisition anomalies, and temporal outliers, which are common in radar data. This approach ensures cleaner and more stable backscatter images suitable for time-series analysis.

```python
    vv_image = s1_month.median().clip(aoi)
    monthly_vv_images.append(vv_image)
    valid_months.append(month)
```

### 4.1.2 Explanation step by step:

```python
vv_image = s1_month.median().clip(aoi)
```

* `s1_month.median()` → computes the **pixel-wise median** of all Sentinel-1 VV images for that month. This is useful to **eliminate noise**, speckle, or acquisition artifacts common in SAR data.

* `.clip(aoi)` → restricts the image to your **Area of Interest (AOI)**, reducing file size and processing time.

---

```python
monthly_vv_images.append(vv_image)
```

Adds the monthly composite to a list (`monthly_vv_images`) so that you can:

* Export all images together
* Later compute an **overall seasonal mean**

---

```python
valid_months.append(month)
```

Stores the **month number** (e.g., `4` for April) **only if the month has valid images**, which is useful for:

* Logs
* Legends
* Filtering in dashboards or reports

---

This structure allows:

* Avoid reprocessing the same composites multiple times
* Build a **true seasonal average** using only valid months
* Keep track of what was actually processed

---

### 4.1.3 Why use `.median()` instead of `.mean()`?

```python
vv_image = s1_month.median().clip(aoi)
```

The **median** is more robust than the **mean** when dealing with:
* **Outliers** (e.g., very high or low VV values due to acquisition noise)
* **SAR speckle effects**
* **Temporal artifacts** (rain, incidence angle variation)

**Median vs. Mean (assuming 3+ SAR images/month)**

| Composite Type | Pros                                               | Cons                                    |
| -------------- | -------------------------------------------------- | --------------------------------------- |
| `median()`     | Robust to outliers, ideal for radar backscatter    | Less sensitive to small variations      |
| `mean()`       | True average value, good for consistent conditions | Sensitive to noise, outliers distort it |

**Practical Example**

Imagine 5 SAR images for May, but one has a temporary acquisition anomaly (e.g., rain):

| Image | VV (dB) |
| ----- | ------- |
| 1     | -12     |
| 2     | -11.5   |
| 3     | -30 ❗   |
| 4     | -11.7   |
| 5     | -12.2   |

* `mean()` = heavily influenced by -30 → **biased value**
* `median()` = discards the anomaly → **more reliable composite**

---

## When should you prefer `mean()`?

You might choose `.mean()` if:

* You have **many SAR scenes** per month (e.g., >10), and
* The data are **stable and clean**, with few outliers
* You're doing **dense time-series analysis** (e.g., daily, 3-day composites)
* You're using **optical indices** (like NDVI), where mean is often used

---

Assolutamente! Ecco una versione aggiornata del blocco per il `README.md`, con incluso il link ufficiale alla documentazione ISRIC:

---

## 4.2 Soil Texture Data (Sand, Silt, Clay) — Download from ISRIC SoilGrids

To calibrate SAR-derived soil moisture with field conditions, we use **soil texture maps** (sand, silt, clay) from the official [ISRIC SoilGrids](https://soilgrids.org/) platform.

### 4.2.1 How to download:

1. Visit **[https://soilgrids.org](https://soilgrids.org)**
2. Navigate or zoom to your **Area of Interest (AOI)**.
3. In the right-side panel:

   * Select **Soil Properties**: choose `Sand`, `Silt`, and `Clay`
   * Select **Depths**: typically `0–5 cm` for surface moisture studies
   * Choose **Statistics**: use `Mean` values
4. Click the **Download** button to receive a ZIP file containing GeoTIFF rasters.
5. Extract the files into your project folder:

in thi case:
```bash
   /data/outputs/raster/isric/raster/clay_0-5cm_mean.tif

```

Typical output files:

* `sand_0-5cm_mean.tif`
* `silt_0-5cm_mean.tif`
* `clay_0-5cm_mean.tif`

These files can be loaded in Python using `rasterio`, `rioxarray`, or `xarray` for further geospatial analysis and integration.

For more details, refer to the official documentation:
[ISRIC SoilGrids FAQ](https://www.isric.org/explore/soilgrids/faq-soilgrids)


### 4.2.2 Stack the Soil Texture Rasters (Sand, Silt, Clay)

After downloading the individual GeoTIFF files for sand, silt, and clay, we stack them into a **multiband raster** to simplify spatial processing and sampling.

This creates a single raster where:

* Band 1 = Sand (%)
* Band 2 = Silt (%)
* Band 3 = Clay (%)

```python
import rasterio
import os

# Input paths
sand_path = "../data/outputs/raster/isric/raster/sand_0_5_div10.tif"
silt_path = "../data/outputs/raster/isric/raster/silt_0_5_div10.tif"
clay_path = "../data/outputs/raster/isric/raster/clay_0_5_div10.tif"

# Output stacked raster
stacked_path = "../data/outputs/raster/isric/stack/soil_texture_stack.tif"
os.makedirs(os.path.dirname(stacked_path), exist_ok=True)

# Read and stack bands
with rasterio.open(sand_path) as src_sand, \
     rasterio.open(silt_path) as src_silt, \
     rasterio.open(clay_path) as src_clay:

    sand = src_sand.read(1)
    silt = src_silt.read(1)
    clay = src_clay.read(1)

    meta = src_sand.meta.copy()
    meta.update({
        "count": 3,
        "dtype": sand.dtype
    })

# Write multiband GeoTIFF
with rasterio.open(stacked_path, 'w', **meta) as dst:
    dst.write(sand, 1)
    dst.write(silt, 2)
    dst.write(clay, 3)

print(f"✅ Saved raster stack: {stacked_path}")
```

### 4.2.3 Generate Soil Texture Centroids as Shapefile

To prepare for point-based analysis (e.g., interpolation, sampling, classification), we extract **centroids of each valid raster pixel** and save them as point geometries in a shapefile.

Each point contains:

* Sand (%)
* Silt (%)
* Clay (%)
* Geometry (centroid of the raster cell)

```python
import rasterio
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from rasterio.transform import xy
import os

# Load sand, silt, clay rasters
paths = {
    'sand': "../data/outputs/raster/isric/raster/sand_0_5_div10.tif",
    'silt': "../data/outputs/raster/isric/raster/silt_0_5_div10.tif",
    'clay': "../data/outputs/raster/isric/raster/clay_0_5_div10.tif"
}

arrays = {}
transform = None
crs = None

# Read rasters and store metadata
for name, path in paths.items():
    with rasterio.open(path) as src:
        arrays[name] = src.read(1)
        transform = transform or src.transform
        crs = crs or src.crs

# Filter valid pixels (non-NaN in all three layers)
mask = (~np.isnan(arrays['sand'])) & (~np.isnan(arrays['silt'])) & (~np.isnan(arrays['clay']))
rows, cols = np.where(mask)

# Create points
geoms = []
data = {'sand': [], 'silt': [], 'clay': []}

for r, c in zip(rows, cols):
    x, y = xy(transform, r, c, offset='center')
    geoms.append(Point(x, y))
    data['sand'].append(arrays['sand'][r, c])
    data['silt'].append(arrays['silt'][r, c])
    data['clay'].append(arrays['clay'][r, c])

# Create GeoDataFrame
gdf = gpd.GeoDataFrame(data, geometry=geoms, crs=crs)

# Export to shapefile
output_shp = "../data/outputs/shapefile/soiltexture_centroids.shp"
os.makedirs(os.path.dirname(output_shp), exist_ok=True)
gdf.to_file(output_shp)

print("✅ Shapefile created:", output_shp)
print("— Number of points:", len(gdf))
```

This shapefile is ready to be used for classification using soil texture systems such as USDA or FAO, interpolation, or as reference for SAR backscatter calibration.

You can proceed to classify these points using packages like [`soiltexture`](https://pypi.org/project/soiltexture/) or:

```python

def classify_usda(sand, silt, clay):
    if 0 <= sand <= 45 and 40 <= clay <= 100 and 0 <= silt <= 40:
        return 'Cl'  # Clay
    elif 45 <= sand <= 65 and 35 <= clay <= 55 and 0 <= silt <= 20:
        return 'SaCl'  # Sandy Clay
    elif 0 <= sand <= 20 and 40 <= clay <= 60 and 40 <= silt <= 60:
        return 'SiCl'  # Silty Clay
    elif 20 <= sand <= 45 and 25 <= clay <= 40 and 15 <= silt <= 55:
        return 'ClLo'  # Clay Loam
    elif 0 <= sand <= 20 and 25 <= clay <= 40 and 40 <= silt <= 75:
        return 'SiClLo'  # Silty Clay Loam
    elif 45 <= sand <= 80 and 20 <= clay <= 35 and 0 <= silt <= 25:
        return 'SaClLo'  # Sandy Clay Loam
    elif 25 <= sand <= 55 and 5 <= clay <= 25 and 25 <= silt <= 50:
        return 'Lo'  # Loam
    elif 85 <= sand <= 100 and 0 <= clay <= 10 and 0 <= silt <= 15:
        return 'Sa'  # Sand
    elif 70 <= sand <= 90 and 0 <= clay <= 15 and 0 <= silt <= 30:
        return 'LoSa'  # Loamy Sand
    elif 45 <= sand <= 85 and 0 <= clay <= 20 and 0 <= silt <= 50:
        return 'SaLo'  # Sandy Loam
    elif 0 <= sand <= 50 and 0 <= clay <= 25 and 50 <= silt <= 85:
        return 'SiLo'  # Silty Loam
    elif 0 <= sand <= 20 and 0 <= clay <= 15 and 80 <= silt <= 100:
        return 'Si'  # Silt
    else:
        return 'Unk'  # Unknown or outside defined ranges


```

