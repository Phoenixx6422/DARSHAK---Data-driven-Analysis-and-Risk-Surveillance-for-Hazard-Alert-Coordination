# Pre-Disaster Management & Early Warning System - AI/ML Pipelines

This workspace contains two independent modular AI/ML hazard pipelines adhering to the project output contract:
1. **`hazard_cyclone/`** — North Indian Ocean Cyclone Risk Assessment (IBTrACS integration).
2. **`hazard_flood/`** — Indian River Basin Flood Risk Assessment (Central Water Commission / CWC gauge & basin hydrology integration).

## Data Sources & Where to Download Real Data:
- **Cyclone (IBTrACS):** Download the North Indian basin CSV (`ibtracs.NI.list.v04r01.csv`) from NOAA NCEI [cite: 1.2.1] and place it in `data/`.
- **Flood (CWC):** Download historical gauge observations and forecasts from the **Central Water Commission (CWC)** National Water Data Portal or public research repositories like `cwc-flood-forecasts` [cite: 1.2.2] and place `cwc_flood_stations.csv` in `data/`.
*(If real CSV files are not present, both pipelines automatically fall back to robust synthetic data generators so unit testing and training can run offline immediately).*

## Training via Jupyter Notebooks
- **`train_cyclone_pipeline.ipynb`**: Trains the cyclone model using group-aware cross validation and tests live assessment.
- **`train_flood_pipeline.ipynb`**: Trains the flood model using K-Fold cross validation over river basin indicators and tests live assessment.
