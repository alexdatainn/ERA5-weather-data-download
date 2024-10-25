# ERA5 Data Processing

This project fetches and processes ERA5 reanalysis data from the Copernicus Climate Data Store using the CDS API. The data includes wind components, temperature, and surface pressure, allowing the computation of additional metrics such as air density. This project also prepares and exports the final dataset to CSV format for further analysis.

## Table of Contents
- [Features](#features)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features
- Fetches ERA5 reanalysis data from the Copernicus API.
- Computes air density using IEC 61400-12 guidelines.
- Outputs data in CSV format with wind speed, air density, and other essential variables.

## Getting Started

### Prerequisites
- Python 3.8 or above
- CDS API key (obtainable from the [Copernicus Climate Data Store](https://cds.climate.copernicus.eu))

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ERA5_Data_Processing.git
   cd ERA5_Data_Processing
