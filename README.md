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
│     └─ shapefile/
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