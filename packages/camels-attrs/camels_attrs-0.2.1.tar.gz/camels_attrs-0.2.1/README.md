# CAMELS Attrs

![CAMELS Attrs](assets/thumbnail.png)

[![PyPI version](https://badge.fury.io/py/camels-attrs.svg)](https://pypi.org/project/camels-attrs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/camels-attrs)](https://pepy.tech/project/camels-attrs)

A Python package for extracting CAMELS-like catchment attributes for any USGS gauge site in the United States.

## Overview

This package provides a simple, reproducible way to extract comprehensive catchment attributes following the CAMELS (Catchment Attributes and Meteorology for Large-sample Studies) methodology. It automates the extraction of topographic, climatic, soil, vegetation, geological, and hydrological characteristics for any USGS-monitored watershed.
Additionally, it can fetch daily hydrometeorological forcing data (precipitation, temperature, solar radiation, wind speed, humidity) from the GridMET dataset for user-defined date ranges. The package also includes a new feature to create a comprehensive multi-panel watershed map that visualizes key attributes and spatial context.

## Features

### Static Catchment Attributes
- **Watershed Delineation**: Automated watershed boundary extraction using NLDI
- **Topographic Attributes**: Elevation, slope, and drainage area from 3DEP DEM
- **Climate Indices**: Precipitation, temperature, aridity, seasonality from GridMET
- **Soil Characteristics**: Texture, porosity, conductivity from gNATSGO and POLARIS
- **Vegetation Metrics**: LAI, NDVI/GVF, land cover from MODIS and NLCD
- **Geological Properties**: Lithology and permeability from GLiM and GLHYMPS
- **Hydrological Signatures**: Flow statistics, baseflow index, event characteristics

### Hydrometeorological Timeseries Data
- **Daily Forcing Data**: Precipitation, temperature (min/max/avg), solar radiation, wind speed, humidity
- **PET Calculations**: GridMET PET and Hargreaves-Samani PET
- **Monthly Aggregations**: Automatically compute monthly statistics
- **Water Balance**: Calculate annual water surplus and aridity indices

### Comprehensive Watershed Visualization (NEW!)
- **Multi-Panel Dashboard**: 20"×12" publication-ready watershed maps
- **DEM Elevation Background**: High-resolution terrain visualization
- **Stream Network Overlay**: NLDI-derived drainage network
- **Location Context**: USA map showing watershed location
- **Statistics Panel**: All key attributes displayed (topography, climate, vegetation, hydrology)
- **Analytical Charts**: Elevation profile, land cover pie chart, water balance comparison
- **Cartographic Elements**: Scale bar, north arrow, proper projections
- **Export Options**: High-DPI PNG/PDF for publications

## Installation

```bash
pip install camels-attrs
```

Or install from source:

```bash
git clone https://github.com/galib9690/camels-attrs.git
cd camels-attrs
pip install -e .
```

### Optional Dependencies

For geological attribute extraction (GLiM, GLHYMPS), you may need to install `pygeoglim` separately if it's not available on PyPI:

```bash
pip install git+https://github.com/galib9690/pygeoglim.git
```

If `pygeoglim` is not installed, the package will still work but will return default values for geological attributes.

## Quick Start

### Static Attributes Extraction

#### Python API

```python
from camels_attrs import CamelsExtractor

# Extract static attributes for a single gauge
extractor = CamelsExtractor('01031500')  # USGS gauge ID
attributes = extractor.extract_all()

# Save to CSV
extractor.save('attributes.csv')

# Or get as DataFrame
df = extractor.to_dataframe()
```

#### Command Line Interface

```bash
# Extract static attributes only
camels-extract 01031500 -o attributes.csv

# Multiple gauges
camels-extract 01031500 02177000 06803530 -o combined.csv

# Custom date ranges for hydrological signatures
camels-extract 01031500 --hydro-start 2010-01-01 --hydro-end 2020-12-31
```

### Hydrometeorological Timeseries Data

#### Python API

```python
from camels_attrs import CamelsExtractor, fetch_forcing_data, get_monthly_summary

# Extract timeseries data using the extractor class
extractor = CamelsExtractor('01031500')
forcing_data = extractor.extract_timeseries('2020-01-01', '2020-12-31')

# Or use standalone functions
forcing_data = fetch_forcing_data(watershed_geometry, '2020-01-01', '2020-12-31')

# Calculate monthly aggregations
monthly_data = get_monthly_summary(forcing_data)

# Calculate water balance
from camels_attrs import calculate_water_balance
water_balance = calculate_water_balance(forcing_data)
```

#### Command Line Interface

```bash
# Extract both static attributes AND timeseries data
camels-extract 01031500 -o attributes.csv --timeseries

# Extract only timeseries data (skip static attributes)
camels-extract 01031500 -o forcing_data.csv --timeseries-only

# Include monthly aggregations in output
camels-extract 01031500 -o data.csv --timeseries --monthly

# Custom date ranges for timeseries
camels-extract 01031500 --climate-start 2010-01-01 --climate-end 2020-12-31 --timeseries
```

### Comprehensive Watershed Visualization (NEW!)

#### Python API

```python
from camels_attrs import CamelsExtractor

# Extract attributes
extractor = CamelsExtractor('01031500')
attributes = extractor.extract_all()

# Create comprehensive multi-panel watershed map
fig = extractor.create_comprehensive_map(
    save_path='watershed_comprehensive_map.png',
    show=True
)

# The map includes:
# - DEM elevation background with terrain colors
# - Watershed boundary (red) and stream network (blue)
# - Gauge location marker (yellow star)
# - USA context map showing watershed location
# - Statistics panel with all key attributes
# - Elevation profile bar chart
# - Land cover distribution pie chart
# - Climate water balance comparison
```

#### Standalone Visualization Function

```python
from camels_attrs import create_comprehensive_watershed_map

# Use the standalone function for custom workflows
fig = create_comprehensive_watershed_map(
    watershed_gdf=extractor.watershed_gdf,
    watershed_geom=extractor.watershed_geom,
    metadata=extractor.metadata,
    attributes=extractor.attributes,
    gauge_id='01031500',
    save_path='custom_map.png'
)
```

#### Visualization Features

- **6-Panel Dashboard** (20"×12" figure)
  - Large main map with DEM, streams, boundary
  - Location context (USA map)
  - Comprehensive statistics text panel
  - Elevation profile
  - Land cover pie chart
  - Climate water balance

- **Professional Elements**
  - Scale bar and north arrow
  - OpenStreetMap basemap overlay
  - High-DPI export (300 DPI)
  - Publication-ready styling

- **Use Cases**
  - Research papers and reports
  - Presentations and posters
  - Watershed characterization studies
  - Model setup documentation

### Advanced Usage Examples

#### Batch Processing Multiple Gauges

```python
from camels_attrs import extract_multiple_gauges

# Process multiple gauges
gauge_ids = ['01031500', '02177000', '06803530']
df = extract_multiple_gauges(gauge_ids)
df.to_csv('multiple_gauges_attributes.csv', index=False)
```

#### Custom PET Calculations

```python
# Extract timeseries with Hargreaves-Samani PET
extractor = CamelsExtractor('01031500')
forcing_data = extractor.extract_timeseries(
    '2020-01-01', '2020-12-31',
    include_hargreaves_pet=True
)
```

#### Climate Statistics from Timeseries

```python
from camels_attrs import calculate_forcing_statistics

# Calculate comprehensive climate statistics
stats = extractor.get_forcing_statistics(forcing_data)
print(f"Mean annual precipitation: {stats['mean_annual_precip_mm']:.1f} mm")
print(f"Aridity index: {stats['aridity_index']:.2f}")
```

## Hydrometeorological Timeseries Data

### Timeseries Variables

The package extracts daily hydrometeorological forcing data from GridMET:

| Variable | Description | Units | Source |
|----------|-------------|-------|--------|
| `date` | Date (YYYY-MM-DD) | - | - |
| `prcp_mm` | Daily precipitation | mm/day | GridMET |
| `tmin_C` | Minimum daily temperature | °C | GridMET |
| `tmax_C` | Maximum daily temperature | °C | GridMET |
| `tavg_C` | Average daily temperature | °C | Calculated |
| `srad_Wm2` | Shortwave solar radiation | W/m² | GridMET |
| `wind_ms` | Wind speed | m/s | GridMET |
| `sph_kgkg` | Specific humidity | kg/kg | GridMET |
| `pet_mm` | Potential evapotranspiration | mm/day | GridMET |
| `pet_hargreaves_mm` | PET (Hargreaves-Samani) | mm/day | Calculated |

### Timeseries Functions

#### Core Timeseries Functions

```python
from camels_attrs import (
    fetch_forcing_data,
    calculate_pet_hargreaves,
    get_monthly_summary,
    calculate_water_balance,
    calculate_forcing_statistics
)

# Fetch daily forcing data for a watershed
forcing_df = fetch_forcing_data(watershed_geometry, '2020-01-01', '2020-12-31')

# Calculate Hargreaves-Samani PET
forcing_with_hargreaves = calculate_pet_hargreaves(forcing_df, latitude)

# Get monthly aggregated statistics
monthly_stats = get_monthly_summary(forcing_df)

# Calculate annual water balance
water_balance = calculate_water_balance(forcing_df)

# Calculate comprehensive climate statistics
climate_stats = calculate_forcing_statistics(forcing_df)
```

#### Using the CamelsExtractor Class

```python
# Extract timeseries using the main extractor class
extractor = CamelsExtractor('01031500')

# Extract timeseries data
forcing_data = extractor.extract_timeseries('2020-01-01', '2020-12-31')

# Include Hargreaves-Samani PET calculation
forcing_data = extractor.extract_timeseries(
    '2020-01-01', '2020-12-31',
    include_hargreaves_pet=True
)

# Get climate statistics from timeseries
stats = extractor.get_forcing_statistics(forcing_data)
```

### Timeseries Applications

#### Hydrological Modeling Input

```python
# Prepare forcing data for hydrological models
forcing_data = extractor.extract_timeseries('2010-01-01', '2020-12-31')

# Calculate monthly aggregations for model spin-up
monthly_data = get_monthly_summary(forcing_data)

# Export in format suitable for models like SUMMA, VIC, or SWAT
monthly_data.to_csv('model_input_monthly.csv', index=False)
```

#### Climate Trend Analysis

```python
# Analyze long-term climate trends
forcing_data = fetch_forcing_data(watershed_geom, '2000-01-01', '2023-12-31')
stats = calculate_forcing_statistics(forcing_data)

# Calculate annual statistics
annual_precip = forcing_data.groupby(forcing_data['date'].dt.year)['prcp_mm'].sum()
annual_temp = forcing_data.groupby(forcing_data['date'].dt.year)['tavg_C'].mean()

# Trend analysis
print(f"Annual precipitation trend: {annual_precip.corr(range(len(annual_precip))):.3f}")
print(f"Annual temperature trend: {annual_temp.corr(range(len(annual_temp))):.3f}")
```

#### Water Balance Studies

```python
# Calculate catchment water balance
water_balance = calculate_water_balance(forcing_data)

print("Annual Water Balance:")
print(water_balance[['prcp_mm', 'pet_mm', 'water_surplus_mm']])

# Calculate aridity trends
aridity_trend = water_balance['aridity_index'].corr(range(len(water_balance)))
print(f"Aridity trend: {aridity_trend:.3f}")
```

## Extracted Attributes

The package extracts 70+ static attributes organized into categories:

### Metadata
- `gauge_id`, `gauge_name`, `gauge_lat`, `gauge_lon`, `huc_02`

### Topography
- `elev_mean`, `elev_min`, `elev_max`, `elev_std`
- `slope_mean`, `slope_std`
- `area_geospa_fabric`

### Climate (customizable date range)
- `p_mean`, `pet_mean`, `temp_mean`
- `aridity`, `p_seasonality`, `temp_seasonality`
- `frac_snow`
- `high_prec_freq`, `high_prec_dur`, `high_prec_timing`
- `low_prec_freq`, `low_prec_dur`, `low_prec_timing`

### Soil
- `soil_porosity`, `soil_depth_statsgo`, `max_water_content`
- `sand_frac`, `silt_frac`, `clay_frac`
- `soil_conductivity`

### Vegetation
- `lai_max`, `lai_min`, `lai_diff`
- `gvf_max`, `gvf_diff`, `gvf_mean`
- `frac_forest`, `frac_cropland`, `water_frac`
- `dom_land_cover`, `dom_land_cover_frac`
- `root_depth_50`, `root_depth_99`

### Geology
- `geol_1st_class`, `geol_2nd_class`
- `glim_1st_class_frac`, `glim_2nd_class_frac`
- `carbonate_rocks_frac`
- `geol_permeability`, `geol_porostiy`

### Hydrology (customizable date range)
- `q_mean`, `q_std`, `q5`, `q95`, `q_median`
- `baseflow_index`, `runoff_ratio`, `stream_elas`
- `slope_fdc`, `flow_variability`
- `high_q_freq`, `high_q_dur`
- `low_q_freq`, `low_q_dur`
- `zero_q_freq`
- `hfd_mean`, `half_flow_date_std`

## Requirements

- Python >=3.8
- numpy, pandas, geopandas
- xarray, rioxarray, rasterio
- pynhd, py3dep, pygridmet, pygeohydro
- pygeoglim, planetary-computer
- scipy, matplotlib

See `pyproject.toml` for complete dependency list.

## Data Sources

- **Watershed boundaries**: USGS NLDI
- **Topography**: USGS 3DEP
- **Climate**: GridMET
- **Soil**: gNATSGO, POLARIS
- **Vegetation**: MODIS (LAI, NDVI), NLCD
- **Geology**: GLiM, GLHYMPS
- **Streamflow**: USGS NWIS

## References

This package implements the methodology described in:

- Newman et al. (2015). Development of a large-sample watershed-scale hydrometeorological dataset. NCAR Technical Note
- Addor et al. (2017). The CAMELS data set: catchment attributes and meteorology for large-sample studies. Hydrology and Earth System Sciences

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Citation

If you use this package in your research, please cite:

```
Galib, M. & Merwade, V. (2025). camels-attrs: A Python package for extracting 
CAMELS-like catchment attributes. Lyles School of Civil Engineering, Purdue University.
```

## Contact

Mohammad Galib - mgalib@purdue.edu  
Venkatesh Merwade - vmerwade@purdue.edu

## Acknowledgments

We acknowledge the support and resources provided by Purdue University and the hydrological research community.
