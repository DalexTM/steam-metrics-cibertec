import pandas as pd
from sklearn.impute import SimpleImputer

print("=" * 70)
print("GENERACIÓN DE LA CAPA SILVER")
print("=" * 70)

# 1. Cargar datos Bronze
metacritic = pd.read_parquet("data/bronze/bronze_metacritic.parquet")
steamspy = pd.read_parquet("data/bronze/bronze_steamspy.parquet")

# 2. Estandarizar nombres de columnas
metacritic = metacritic.rename(columns={
    "AppID": "appid",
    "Name": "name"
})

# 3. Integrar datasets
silver = pd.merge(
    metacritic,
    steamspy,
    on="appid",
    how="inner"
)

# 4. Unificar la columna name
silver["name"] = (
    silver["name_y"]
    .fillna(silver["name_x"])
    .str.replace("™", "", regex=False)
    .str.replace("®", "", regex=False)
    .str.strip()
)

# 5. Eliminar columnas duplicadas
silver.drop(columns=["name_x", "name_y"], inplace=True)

# 6. Eliminar registros duplicados
silver = silver.drop_duplicates()

# ======================================================
# 7. IMPUTACIÓN DE VALORES FALTANTES
# ======================================================

# Columnas numéricas
numeric_cols = silver.select_dtypes(include=["number"]).columns

# Columnas categóricas
categorical_cols = silver.select_dtypes(include=["object", "category"]).columns

# Imputar variables numéricas con la mediana
if len(numeric_cols) > 0:
    num_imputer = SimpleImputer(strategy="median")
    silver[numeric_cols] = num_imputer.fit_transform(silver[numeric_cols])

# Imputar variables categóricas con la moda
if len(categorical_cols) > 0:
    cat_imputer = SimpleImputer(strategy="most_frequent")
    silver[categorical_cols] = cat_imputer.fit_transform(silver[categorical_cols])

# 8. Guardar Silver
silver.to_parquet(
    "data/silver/silver.parquet",
    index=False
)

print("Silver generado correctamente.")
print(f"Registros: {len(silver):,}")
print(f"Columnas : {len(silver.columns)}")

# Verificar valores faltantes
print("\nValores nulos restantes:")
print(silver.isnull().sum()[silver.isnull().sum() > 0])