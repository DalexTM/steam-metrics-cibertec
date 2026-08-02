import pandas as pd
from profile_parquet import profile_parquet

print("=" * 70)
print("VALIDACIÓN DE CALIDAD - BRONZE")
print("=" * 70)

# ------------------------------------------------------------------
# 1. Perfil de los datasets Bronze
# ------------------------------------------------------------------
profile_parquet("data/bronze/bronze_metacritic.parquet")
profile_parquet("data/bronze/bronze_steamspy.parquet")

# ------------------------------------------------------------------
# 2. Cargar datos Bronze
# ------------------------------------------------------------------
metacritic = pd.read_parquet("data/bronze/bronze_metacritic.parquet")
steamspy = pd.read_parquet("data/bronze/bronze_steamspy.parquet")

# ------------------------------------------------------------------
# 3. Estandarizar nombres de columnas
# ------------------------------------------------------------------
metacritic = metacritic.rename(columns={
    "AppID": "appid",
    "Name": "name"
})

print("=" * 70)
# ------------------------------------------------------------------
# 4. Validación de la llave de integración
# ------------------------------------------------------------------
print("\n=== Validación de AppID ===")

print("Tipo de dato:")
print("Metacritic:", metacritic["appid"].dtype)
print("SteamSpy  :", steamspy["appid"].dtype)

print("\nAppID únicos:")
print("Metacritic:", metacritic["appid"].nunique())
print("SteamSpy  :", steamspy["appid"].nunique())

coincidencias = set(metacritic["appid"]) & set(steamspy["appid"])

print(f"\nTotal Metacritic : {len(metacritic):,}")
print(f"Total SteamSpy   : {len(steamspy):,}")
print(f"AppID en común   : {len(coincidencias):,}")

# ------------------------------------------------------------------
# 5. Merge temporal para validar consistencia
# ------------------------------------------------------------------
comparacion = pd.merge(
    metacritic,
    steamspy,
    on="appid",
    how="inner"
)

print(f"\nRegistros integrados: {comparacion.shape}")

# ------------------------------------------------------------------
# 6. Comparación de nombres
# ------------------------------------------------------------------
print("\n=== Comparación de nombres ===")

diferencias = comparacion[
    comparacion["name_x"] != comparacion["name_y"]
]

print("¿Todos los nombres coinciden?:", diferencias.empty)
print("Cantidad de diferencias:", len(diferencias))

if not diferencias.empty:
    print(
        diferencias[
            ["appid", "name_x", "name_y"]
        ].head(20)
    )

# ------------------------------------------------------------------
# 7. Duplicados del dataset integrado
# ------------------------------------------------------------------
print("\n=== Duplicados ===")
print(comparacion.duplicated().sum())

# ------------------------------------------------------------------
# 8. Valores nulos
# ------------------------------------------------------------------
print("\n=== Valores nulos (%) ===")
print(
    (comparacion.isnull().mean() * 100)
    .sort_values(ascending=False)
)