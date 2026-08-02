import pandas as pd
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.ensemble import RandomForestRegressor

# --------------------------------------------------
# Cargar datos Bronze
# --------------------------------------------------
steamspy = pd.read_parquet("data/bronze/bronze_steamspy.parquet")

# Variables numéricas con nulos
columnas = [
    "price",
    "discount",
    "initialprice"
]

df = steamspy[columnas].copy()

print("=" * 70)
print("VALORES NULOS ANTES DE LA IMPUTACIÓN")
print("=" * 70)
print(df.isnull().sum())

# ==================================================
# Método 1 - SimpleImputer (Media)
# ==================================================
simple = SimpleImputer(strategy="mean")

df_simple = pd.DataFrame(
    simple.fit_transform(df),
    columns=columnas
)

# ==================================================
# Método 2 - KNNImputer
# ==================================================
knn = KNNImputer(n_neighbors=5)

df_knn = pd.DataFrame(
    knn.fit_transform(df),
    columns=columnas
)

# ==================================================
# Método 3 - IterativeImputer + RandomForest
# ==================================================
iterative = IterativeImputer(
    estimator=RandomForestRegressor(
        n_estimators=50,
        random_state=42
    ),
    random_state=42
)

df_iter = pd.DataFrame(
    iterative.fit_transform(df),
    columns=columnas
)

# --------------------------------------------------
# Comparación
# --------------------------------------------------
print("\n" + "=" * 70)
print("VALORES NULOS DESPUÉS DE LA IMPUTACIÓN")
print("=" * 70)

print("\nSimpleImputer")
print(df_simple.isnull().sum())

print("\nKNNImputer")
print(df_knn.isnull().sum())

print("\nIterativeImputer")
print(df_iter.isnull().sum())

# --------------------------------------------------
# Comparar algunos registros imputados
# --------------------------------------------------
print("\n" + "=" * 70)
print("REGISTROS IMPUTADOS")
print("=" * 70)

filas_nulas = df[df.isnull().any(axis=1)].index

comparacion = pd.DataFrame({
    "price_original": df.loc[filas_nulas, "price"],
    "price_simple": df_simple.loc[filas_nulas, "price"],
    "price_knn": df_knn.loc[filas_nulas, "price"],
    "price_iterative": df_iter.loc[filas_nulas, "price"]
})

print(comparacion.head(10))