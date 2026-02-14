# %%
import requests
import polars as pl
import os
from datetime import date

# Download data using requests
url = "https://repodatos.atdt.gob.mx/api_update/inah/visitantes_zonas_arqueologicas/INAH_visitantes_zonas_general_ok.csv"

headers = {
    # Pretend to be a normal browser
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.8" 
}

resp = requests.get(url, headers=headers)
resp.raise_for_status()

# Load dataset using Polars
df = pl.read_csv(resp.content)

# Add metadata
today = date.today()
df = df.with_columns(
    pl.lit(url).alias('source'),
    pl.lit(today).alias('processed_date')
)

# Create folder for saving dataset
current_path = os.path.dirname(os.path.dirname(__file__))
db_folder = os.path.join(current_path, 'DB', '0_Raw')
os.makedirs(db_folder, exist_ok=True)

# Saving
file_path = os.path.join(db_folder, 'archaelogical_tourism.parquet')
df.write_parquet(file_path)
# %%
