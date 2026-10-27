# Nabd Tadawul — Saudi Stock Market Insights

A bilingual (English / العربية), light & dark Streamlit web app built on an EDA of the Saudi Stock Exchange
(Tadawul), organised as **four services**:

| Service | What it offers |
|---|---|
| **Market Today** | Today's market from Yahoo Finance (≈15-min delay), refreshed automatically: market status, live ticker tape, a one-sentence summary of the day, the TASI index with its chart, market breadth (stocks up / down / unchanged), top gainers / losers / most traded, sectors today (Tadawul industry groups) and a searchable table of every share on the main market (official list + newer listings found automatically; REIT funds excluded). If the live feed is unreachable it falls back to the last session in the dataset. |
| **Historical Analysis** | The Jupyter notebook as a website, in the same order: The data (cleaning), Distributions, Relationships, Q1 Sectors, Q2 Volume spikes, Q3 Correlation, Q4 Volatility, Conclusions, plus a Investment simulator. Every chart follows the filters. |
| **Settings & accessibility** | Language (English / العربية, RTL), theme (light / dark / high contrast), text size (90–130%), colour-blind-friendly colours (blue / orange, Okabe-Ito palette) and extra text spacing, with a mini live preview. Choices are saved in the page URL. Always on: ▲/▼ arrows besides colour and right-to-left layout for Arabic. |
| **Developer Corner** (زاوية المبرمج) | Downloads: the original Kaggle data, the cleaned dataset, the Jupyter notebook and the company list. |

**Author:** Tarfah Alsunaidi
**Data:** [Saudi Arabian Stock Market Data – Kaggle](https://www.kaggle.com/datasets/abdelrahmanalimo/saudi-arabian-stock-market-data) (history) · Yahoo Finance via `yfinance` (live, delayed)

## Project structure
```
stock_project/
├── app.py                              # Streamlit app (all four services)
├── assets/logo.png                     # site logo / browser-tab icon
├── Tarfah_Alsunaidi_EDA_Project.ipynb  # the EDA notebook 
├── data/
│   ├── ALL_SAUDI_STOCKS_2022_TO_TODAY.csv  # raw Kaggle file (input of the notebook)
│   ├── Saudi_Tadawul_Cleaned_Dataset.csv   # cleaned data produced by the notebook
│   └── tadawul_companies.csv               # official company names and industry groups by symbol
├── requirements.txt
├── .streamlit/config.toml              
└── README.md
```

## How to run
```bash
python -m venv .venv
source .venv/bin/activate    
pip install -r requirements.txt
streamlit run app.py
```
The app opens at http://localhost:8501. Market Today needs an internet connection; everything else works offline.


## Interface
- App shell: sticky top app bar (logo + navigation), page banner on every service, and a footer with links and credits.
- Responsive: on tablets the cards wrap into rows; below 1150 px the navigation collapses into a hamburger menu.
- An animated splash screen appears on first load and whenever you switch service, and stays until the new page has finished loading.
- The site logo is embedded in the code, so the browser-tab icon works even without the `assets` folder.

## Filters
- Market Today: small refresh button in the page banner; auto-refresh interval at the bottom of the page.
- Historical Analysis filter panel.


## Limitations
- Prices come from Yahoo Finance , not Tadawul's official feed.
- Names and sectors attached from Yahoo Finance during preparation had to be checked and aligned with the official list of Tadawul companies.
- Short history for 2024–25 listings
- Equal weights, not the official TASI