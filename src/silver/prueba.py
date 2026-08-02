import pandas as pd


def revisar_nulos(ruta, nombre):
    print("=" * 70)
    print(f"DATASET: {nombre}")
    print("=" * 70)

    df = pd.read_parquet(ruta)

    # Cantidad de nulos
    nulos = df.isnull().sum()

    # Porcentaje de nulos
    porcentaje = (df.isnull().mean() * 100).round(2)

    # Reporte
    reporte = pd.DataFrame({
        "Nulos": nulos,
        "% Nulos": porcentaje
    }).sort_values("% Nulos", ascending=False)

    print(reporte)

    print("\nColumnas con nulos:")
    con_nulos = reporte[reporte["Nulos"] > 0]

    if con_nulos.empty:
        print("✅ No se encontraron valores nulos.")
    else:
        print(con_nulos)

    print("\n")


revisar_nulos(
    "data/bronze/bronze_metacritic.parquet",
    "Metacritic"
)

revisar_nulos(
    "data/bronze/bronze_steamspy.parquet",
    "SteamSpy"
)