import pandas as pd

# I. INTEGRACIÒN Y LIMPIEZA DE DATOS

# 1. Cargar datos Bronze
metacritic = pd.read_parquet("data/bronze/bronze_metacritic.parquet")
steamspy = pd.read_parquet("data/bronze/bronze_steamspy.parquet")

# 2. Estandarizar nombres de columnas
metacritic = metacritic.rename(columns={
    "AppID": "appid",
    "Name": "name"
})

# 3. Validar la llave de integración
print("Tipo de dato AppID:")
print(metacritic["appid"].dtype)
print(steamspy["appid"].dtype)

# Cantidad de AppID únicos
print("Metacritic:", metacritic["appid"].nunique())
print("SteamSpy:", steamspy["appid"].nunique())

# Verificar cuantos juegos tienen en común
coincidencias = set(metacritic["appid"]) & set(steamspy["appid"])

print(f"Metacritic: {len(metacritic):,} juegos")
print(f"SteamSpy: {len(steamspy):,} juegos")
print(f"Juegos en común: {len(coincidencias):,}")

# 4. Integración de bases de datos
silver = pd.merge(
    metacritic,
    steamspy,
    on="appid",
    how="inner"
)

print(f"\nDataset integrado: {silver.shape}")

#5. Comparación de columnas
print("\n=== Comparación de columnas ===")
print(
    "¿Los nombres son iguales?:",
    (silver["name_x"] == silver["name_y"]).all()
)

# Mostrar los primeros registros donde los nombres son diferentes
diferencias = silver[silver["name_x"] != silver["name_y"]]

print(diferencias[["appid", "name_x", "name_y"]].head(20))


# 6. Limpieza de nombres
silver["name"] = (
    silver["name_y"]
    .fillna(silver["name_x"])
)

silver["name"] = (
    silver["name"]
    .str.replace("™", "", regex=False)
    .str.replace("®", "", regex=False)
    .str.strip()
)


silver.drop(
    columns=["name_x", "name_y"],
    inplace=True
)

print(silver.columns.tolist())
print(f"\nDataset integrado: {silver.shape}")


# 7. Guardar datos Silver
silver.to_parquet("data/silver/silver.parquet", index=False)


# 8. Revisión de valores nulos
print(
    (silver.isnull().mean()*100)
    .sort_values(ascending=False)
)


# 9. Transformación de tipos de datos
silver.info()

##Variable fecha
silver["Release_date"] = pd.to_datetime(
    silver["Release_date"],
    errors="coerce"
)

##Variables numericas
columnas_numericas = [
    "Peak_CCU",
    "Required_age",
    "Metacritic_score",
    "Recommendations",
    "Average_playtime_forever",
    "Average_playtime_two_weeks",
    "Median_playtime_forever",
    "Median_playtime_two_weeks",
    "positive",
    "negative",
    "userscore",
    "price",
    "initialprice",
    "discount",
    "ccu"
]

for col in columnas_numericas:
    if col in silver.columns:
        silver[col] = pd.to_numeric(silver[col], errors="coerce")
        

##Variables booleanas
columnas_bool = ["Windows", "Mac", "Linux"]

for col in columnas_bool:
    if col in silver.columns:
        silver[col] = silver[col].map({
            "True": True,
            "False": False
        })
        
        
silver.info()


# 10. Revisión de duplicados

duplicados_appid = silver[silver.duplicated(subset=["appid"], keep=False)]

print(duplicados_appid)

silver = silver.drop_duplicates()

print("Duplicados completos:", silver.duplicated().sum())
print("Duplicados por appid:", silver["appid"].duplicated().sum())


# II. TRANSFORMACIÓN DE DATOS

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
import time
import sys

# 1. Feature Engineering (Variables derivadas)

# Variable 1. Total de reseñas
silver["total_reviews"] = (silver["positive"] + silver["negative"])

# Varible 2. Tasa de aprobación
silver["approval_rate"] = (
    silver["positive"] / silver["total_reviews"]
)

# Variable 3. Año de lanzamiento
silver["release_year"] = silver["Release_date"].dt.year

# Variable 4. Antigüedad del juego
silver["game_age"] = 2026 - silver["release_year"]

# Variable 5. Diferencia entre crìtica y usuarios
silver["score_gap"] = silver["Metacritic_score"] - silver["userscore"]

print(silver[["total_reviews", "approval_rate", "release_year", "game_age", "score_gap"]].head())


# 2. Agregaciones

# Agregación 1. Promedio de jugadores por genero
silver.groupby("Genres")["ccu"].mean()

# Agregación 2. Precio promedio por genero
silver.groupby("Genres")["price"].mean()

# Agregación 3. Metacritic promedio
silver.groupby("Genres")["Metacritic_score"].mean()



# 3. Binning (Agrupamiento de datos)

# Binning 1. Categorías de precio

print(silver["price"].dtype)
print(silver["price"].head(10))
print(silver["price"].describe())

silver["price_range"] = pd.cut(
    silver["price"],
    bins=[0, 1000, 3000, 6000, float("inf")],
    labels=[
        "Bajo",
        "Medio",
        "Alto",
        "Premium"
    ],
    include_lowest=True
)

print(silver[["price", "price_range"]].head())


