"""
Created on Sat Jan 21 13:40:01 2023
@author: aebrahimi

Description:
Script to download and process ERA5 weather data, including computing air density 
using the ideal gas law from retrieved temperature, pressure, and optional humidity data.
"""

# Import necessary libraries for API calls, data handling, and calculations
import cdsapi  # API for accessing Copernicus Climate Data Store
from netCDF4 import Dataset  # Library for handling netCDF files
import numpy as np
import pandas as pd
import os
import numpy.ma as ma  # Library for handling masked arrays
from datetime import datetime, timedelta

def compute_air_density(temp_col, pres_col, humi_col=None):
    """
    Calculate air density from temperature, pressure, and optional relative humidity 
    using the ideal gas law as defined by IEC 61400-12.

    Parameters:
        temp_col (array-like): Array of temperature values (in Kelvin).
        pres_col (array-like): Array of pressure values (in Pascals).
        humi_col (array-like, optional): Array of relative humidity values (0-1 range).

    Returns:
        pandas.Series: Calculated air density values (kg/m³).
    """
    # Set default relative humidity to 0.5 if not provided
    rel_humidity = humi_col if humi_col is not None else np.repeat(0.5, temp_col.shape[0])

    # Raise exception if any values are negative
    if np.any(temp_col < 0) or np.any(pres_col < 0) or np.any(rel_humidity < 0):
        raise Exception("Temperature, pressure, or humidity data contains negative values. Please check the data.")

    # Convert temperature and pressure to floats for calculations
    temp_col, pres_col = temp_col.astype(float), pres_col.astype(float)

    # Constants for ideal gas law
    R_const, Rw_const = 287.05, 461.5  # Constants for dry air and water vapor in J/kg/K
    rho = (1 / temp_col) * (pres_col / R_const - rel_humidity * (0.0000205 * np.exp(0.0631846 * temp_col)) * (1 / R_const - 1 / Rw_const))

    return rho

# Initialize API client for data retrieval
c = cdsapi.Client()

# Coordinates dictionary for different sites
Corrd = {
    'SL': [49.5, -98.125, 49.499, -98.124],
    'AMHST': [44.15, -76.700, 44.149, -76.699],
    'MN': [40.530, -88.590, 40.529, -88.589],
    # Add more sites as needed
}

path = './ERA5_20yrs/'
SiteCorrd = Corrd['SL']

# Define yearly blocks for data retrieval to manage large files
years = [['2001', '2002', '2003'], ['2004', '2005', '2006'], ...]

# Empty DataFrame to collect all data
result_df = pd.DataFrame()

# Loop over years and retrieve ERA5 data
for yr in years:
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'variable': [
                '100m_u_component_of_wind', '100m_v_component_of_wind', 
                '2m_temperature', 'surface_pressure'
            ],
            'year': yr,
            'month': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'],
            'day': ['01', '02', '03', '04', ..., '31'],
            'time': ['00:00', '01:00', ..., '23:00'],
            'area': SiteCorrd,
            'format': 'netcdf',
        },
        path + f'ERA5_{yr}.nc'  # File path for saving data
    )

    # Load and process downloaded data
    data = Dataset(path + f'ERA5_{yr}.nc', 'r')
    u_100 = data.variables['u100'][:]
    v_100 = data.variables['v100'][:]
    t_2m = data.variables['t2m'][:]
    surf_pres = data.variables['sp'][:]

    # Calculate wind speed at 100m using Pythagorean theorem
    ws_100m = np.sqrt(v_100**2 + u_100**2)

    # Extract data from masked arrays
    ws_100m = [val[0][0] for val in ma.getdata(ws_100m[:])]
    u_100 = [val[0][0] for val in ma.getdata(u_100[:])]
    v_100 = [val[0][0] for val in ma.getdata(v_100[:])]
    t_2m = [val[0][0] for val in ma.getdata(t_2m[:])]
    surf_pres = [val[0][0] for val in ma.getdata(surf_pres[:])]

    # Convert time from ERA reference date (1900-01-01)
    ERA_start = datetime(1900, 1, 1, 0, 0, 0)
    ERA_datetime = [ERA_start + timedelta(hours=int(dt)) for dt in ma.getdata(data.variables['time'][:])]

    # Create DataFrame with retrieved data
    df = pd.DataFrame({
        'datetime': ERA_datetime, 
        'u_100': u_100, 
        'v_100': v_100, 
        't_2m': t_2m, 
        'surf_pres': surf_pres, 
        'ws_100m': ws_100m
    })

    # Calculate air density and add to DataFrame
    df['dens_100m'] = compute_air_density(df['t_2m'], df['surf_pres'])

    # Append data to result DataFrame
    result_df = pd.concat([result_df, df], axis=0, ignore_index=True)
    data.close()

    print(f'{yr} data processed successfully.')

# Save final DataFrame to CSV file
result_df.to_csv('./ERA5_20yrs/ERA5_20yrs.csv')
