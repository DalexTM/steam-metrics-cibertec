import pandas as pd

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

# 8. Revisión de duplicados
print(
    "Duplicados:",
    silver.duplicated().sum()
)

# 9. Revisión de valores nulos
print(
    (silver.isnull().mean()*100)
    .sort_values(ascending=False)
)