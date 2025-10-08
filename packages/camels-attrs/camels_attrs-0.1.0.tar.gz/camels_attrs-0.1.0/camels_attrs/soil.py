"""
Soil characteristics extraction (aligned with original notebook)
"""

import numpy as np
import xarray as xr
import rioxarray
from pystac_client import Client
import planetary_computer
from pygeohydro import soil_properties, soil_polaris
from pygeoutils import xarray_geomask


def extract_soil_attributes(watershed_geom, crs="EPSG:4326"):
    """
    Extract soil characteristics from multiple sources:
    - Porosity, AWC, FC from USGS ScienceBase datasets (pygeohydro.soil_properties)
    - Texture fractions + Ksat from POLARIS
    - Soil thickness from gNATSGO rasters (Planetary Computer)
    
    Parameters
    ----------
    watershed_geom : shapely.geometry
        Watershed boundary
    crs : str
        Coordinate reference system
    
    Returns
    -------
    dict
        Soil attributes including porosity, conductivity, depth, texture fractions
    """
    try:
        print("  - Extracting soil attributes...")
        
        # Step 1: Porosity, AWC, FC (from soil_properties)
        ds_por = soil_properties("por")
        ds_por = xarray_geomask(ds_por, watershed_geom, crs)
        ds_por = ds_por.where(ds_por.porosity > ds_por.porosity.rio.nodata)
        ds_por["porosity"] = ds_por.porosity.rio.write_nodata(np.nan) / 1000.0
        
        ds_awc = soil_properties("awc")
        ds_awc = xarray_geomask(ds_awc, watershed_geom, crs)
        ds_awc = ds_awc.where(ds_awc.awc > ds_awc.awc.rio.nodata)
        ds_awc["available_water_capacity"] = ds_awc.awc.rio.write_nodata(np.nan) / 1000.0
        
        ds_fc = soil_properties("fc")
        ds_fc = xarray_geomask(ds_fc, watershed_geom, crs)
        ds_fc = ds_fc.where(ds_fc.fc > ds_fc.fc.rio.nodata)
        ds_fc["field_capacity"] = ds_fc.fc.rio.write_nodata(np.nan) / 1000.0
        
        # Step 2: Texture + Hydraulic conductivity (from POLARIS)
        requested = [
            "sand_5", "sand_15", "sand_30",
            "silt_5", "silt_15", "silt_30",
            "clay_5", "clay_15", "clay_30",
            "ksat_5", "ksat_15", "ksat_30"
        ]
        ds_tex = soil_polaris(requested, watershed_geom, geo_crs=crs)
        
        def pick_var(var_base, depth_key):
            name_try = f"{var_base}_{depth_key}"
            if name_try in ds_tex.data_vars:
                return ds_tex[name_try]
            for v in ds_tex.data_vars:
                if v.startswith(var_base) and depth_key in v:
                    return ds_tex[v]
            return None
        
        sand_layers, silt_layers, clay_layers, ksat_layers = [], [], [], []
        for d in ["5", "15", "30"]:
            if (sv := pick_var("sand", d)) is not None: sand_layers.append(sv)
            if (tv := pick_var("silt", d)) is not None: silt_layers.append(tv)
            if (cv := pick_var("clay", d)) is not None: clay_layers.append(cv)
            if (kv := pick_var("ksat", d)) is not None: ksat_layers.append(kv)
        
        if not (sand_layers and silt_layers and clay_layers):
            raise RuntimeError("Could not find matching texture layers in POLARIS")
        
        sand = sum(sand_layers) / len(sand_layers) / 100.0
        silt = sum(silt_layers) / len(silt_layers) / 100.0
        clay = sum(clay_layers) / len(clay_layers) / 100.0
        
        # Soil conductivity
        soil_conductivity_log10 = None
        if ksat_layers:
            soil_conductivity_mps = (sum(ksat_layers) / len(ksat_layers)) * 1e-6
            soil_conductivity_mmhr = soil_conductivity_mps * 3.6e6
            soil_conductivity_log10 = np.log10(soil_conductivity_mmhr.mean(skipna=True).item())
        
        # Step 3: Thickness from gNATSGO
        client = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
        search = client.search(collections=["gnatsgo-rasters"], bbox=watershed_geom.bounds)
        items = list(search.get_items())
        if not items:
            raise ValueError("No gNATSGO items found for this basin.")
        item = planetary_computer.sign(items[0])
        
        thickness = rioxarray.open_rasterio(item.assets["tk0_999a"].href, masked=True)
        thickness = thickness.rio.clip([watershed_geom], crs=crs)
        thickness = thickness.where(thickness < 2e6) * 10  # cm → mm
        thickness = thickness.rio.write_nodata(np.nan)
        
        thickness_resampled = thickness.rio.reproject_match(ds_por["porosity"], resampling=5)
        storage = ds_por["porosity"] * thickness_resampled
        
        # Final scalars
        soil_attrs = {
            "soil_porosity": float(ds_por["porosity"].mean(skipna=True).item()),
            "available_water_capacity": float(ds_awc["available_water_capacity"].mean(skipna=True).item()),
            "field_capacity": float(ds_fc["field_capacity"].mean(skipna=True).item()),
            "sand_frac": float(sand.mean(skipna=True).item()) * 100.0,
            "silt_frac": float(silt.mean(skipna=True).item()) * 100.0,
            "clay_frac": float(clay.mean(skipna=True).item()) * 100.0,
            "soil_depth_statsgo": float(thickness_resampled.mean(skipna=True).item()) * 1e-3,  # mm → m
            "max_water_content": float(storage.mean(skipna=True).item()) * 1e-3,  # mm → m
        }
        if soil_conductivity_log10 is not None:
            soil_attrs["soil_conductivity"] = soil_conductivity_log10
        
        print("  ✓ Soil attributes extracted successfully")
        return soil_attrs
        
    except Exception as e:
        print(f"  ✗ Error extracting soil attributes: {str(e)}")
        print("  Using fallback values...")
        return {
            "soil_porosity": 0.42,
            "available_water_capacity": 0.18,
            "field_capacity": 0.29,
            "sand_frac": 41.0,
            "silt_frac": 36.0,
            "clay_frac": 23.0,
            "soil_depth_statsgo": 1.030,
            "max_water_content": 0.520,
            "soil_conductivity": 1e-6
        }
