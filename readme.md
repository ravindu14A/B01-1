# Predicting the Next Magnitude 9+ Earthquake at the Sumatra-Andaman Subduction Interface


This project analyzes GNSS time-series data from Malaysian and Thai stations to forecast the next magnitude 9+ 
earthquake occurrence at the Sumatra-Andaman subduction interface. 

## Key Findings

- **Earthquake Prediction**: Next large earthquake predicted between **2208-2228** (95% confidence interval)
- **Station-Specific Predictions**:
  - ARAU (Malaysia): 2257 ± 22.1 years
  - KUAL (Malaysia): 2308 ± 62.7 years
  - USMP (Malaysia): 2227 ± 17.1 years
  - BEHR (Malaysia): 2240 ± 71.9 years
  - PHUK (Thailand): 2241 ± 19.3 years

## Project Structure

```
B01/
├── data/
│   ├── raw/                    # Raw GNSS data files
│   ├── processed/              # Cleaned and processed data
│   └── partially_processed_steps/ # Data at different stages of preprocessing 
├── preprocessing/
│   ├── convert.py              # Data conversion
│   ├── coordinate.py           # Coordinate system transformations
│   ├── data_transfer.py        # Organizing, converting and filtering station data
│   ├── delete_earthquakes.py   # Earthquake discontinuities removal
│   ├── pca.py                  # Principal Component Analysis
│   └── plate_motion.py         # Plate motion calculations
├── predictions/
│   ├── main.py                 # Main prediction script
│   └── predictions.py          # Core prediction algorithms
└── README.md
```


## Installation

1. Clone the repository:
```bash
    git clone [repository-url]
    cd B01
```

2. Install required dependencies:
```bash
    pip install -r requirements.txt
```

3. Ensure you have the GNSS data files in the `data/raw/` directory. To allow for easier usage, there are additional 
folders with the data after each stage of preprocessing. If one wants to directly generate predictions, the files 
in the `data/processed/` directory, already include all preprocessing. 

### Running the Analysis

1. **Data Preprocessing**:
```bash
    python preprocessing/convert.py          # Convert data formats
    python preprocessing/coordinate.py       # Transform coordinates to NEU
    python preprocessing/delete_earthquakes.py  # Remove discontinuities
    python preprocessing/plate_motion.py     # Remove absolute plate motion
    python preprocessing/pca.py              # Apply pca transformation
```

2. **Generate Predictions**:
```bash
    python results/main.py
```

## Methodology

### Data Processing Pipeline

1. **Coordinate Transformation**: Convert coordinates to North-East-Up (NEU)
2. **Discontinuity Detection**: Identify and remove earthquake-caused jumps from the time series
3. **Plate Motion Removal**: Subtract absolute plate movement
4. **Principal Component Analysis**: Reduce dimensionality and focus on main deformation direction
5. **Regression Modeling**: Fit post-seismic deformation using exponential decay model

### Mathematical Model

The post-seismic deformation is modeled using:

```
f(t) = vt + c₁e^(-u₁t) + c₂e^(-u₂t) + d
```

Where:
- `v`: velocity of station before earthquake

### Error Estimation

Monte Carlo simulation with 1000 iterations to calculate prediction uncertainty:
- Generate synthetic datasets within measurement uncertainty (From the provided covariance)
- Determine 95% confidence intervals

## Study Area

The analysis focuses on:
- **Countries**: Thailand and Malaysia
- **Stations**: 5 long-duration GNSS stations (1999-2024)

## Limitations & Considerations

- **Data Length**: Limited to ~25 years of observations
- **Seismic Cycle**: Analysis based on single major earthquake (2004)
- **Model Assumptions**: Assumes repeating seismic cycle behavior

## Usage Examples

### Basic Prediction Run

```python
from results.predictions import monte

# Set parameters
country = "thailand"
station = "PHUK"
N = 50  # Monte Carlo samples
years_predict = 300
confidence_level = 95

# Run prediction
monte(country, station, N, years_predict, confidence_level, offset=60, pred_pos=4)
```

## Contributing

This project was developed as part of the Test, Analysis and Simulation course (AE2224-1) at TU Delft's Aerospace Faculty. 

**Team Members**:
- Ravindu Kalinga Bandara
- Nikolai Da Silva
- Laura Kaczmarzyk
- Aleksandra Pawlik
- Andrei Potfalean
- Maxim Shcherbina
- Lowie Thierens
- Nicolas Vardon
- Viktor Velichkov
- Toine van Wassenaar
