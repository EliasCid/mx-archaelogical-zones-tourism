#%%
import polars as pl
import os
import glob

# Folder and file identification
current_path = os.path.dirname(os.path.dirname(__file__))
db_raw = os.path.join(current_path, 'DB', '0_Raw')
db_raw_files = glob.glob(os.path.join(db_raw, '**', '*.parquet'), recursive=True) 

db_bronze = os.path.join(current_path, 'DB', '1_Bronze')
os.makedirs(db_bronze, exist_ok=True)

# Load data
df = pl.read_parquet(db_raw_files[0])

# Unpivot data
months = {
    'enero': 1,
    'febrero': 2,
    'marzo': 3,
    'abril': 4,
    'mayo': 5,
    'junio': 6,
    'julio': 7,
    'agosto': 8,
    'septiembre': 9,
    'octubre': 10,
    'noviembre': 11,
    'diciembre': 12
}

columns_to_unpivot = [
    col for col in df.columns
    if any(month in col.lower() for month in list(months.keys()))
]

df_unpivoted = df.unpivot(
    index=[col for col in df.columns if col not in columns_to_unpivot],
    on=columns_to_unpivot,
    variable_name='month_type',
    value_name='number_of_tourists'
)

# Transform df
df_transformed = df_unpivoted.with_columns(
    pl.when(pl.col('month_type').str.contains('nac')).then(pl.lit('National'))
      .when(pl.col('month_type').str.contains('ext')).then(pl.lit('Foreign'))
      .otherwise(None)
      .alias('tourist_type')
).with_columns(
    pl.col('month_type').str.replace_many(['_nac','_ext'], [''])
).with_columns(
    pl.col('month_type').replace(months).cast(pl.Int8)
).with_columns(
    pl.date(
        pl.col('anio'),
        pl.col('month_type'),
        1
    ).alias('date')
).select([
    'date',
    'estado',
    'clave_siinah',
    'recinto',
    'tourist_type',
    'number_of_tourists',
    'source',
    'processed_date'
]).rename({
    'estado': 'state',
    'clave_siinah': 'id_siinah',
    'recinto': 'archaeological_zone',
}).with_columns(
    pl.col('id_siinah').cast(pl.String)
).sort('date')

# Saving
file_path = os.path.join(db_bronze, 'archaelogical_tourism.parquet')
df_transformed.write_parquet(file_path)
# %%
