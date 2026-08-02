import pandas as pd
from pathlib import Path


def profile_parquet(file_path):
    """Muestra un perfil básico de un archivo Parquet."""

    file_path = Path(file_path)

    print("\n" + "=" * 70)
    print(f"DATASET: {file_path.name}")
    print("=" * 70)

    if not file_path.exists():
        print("El archivo no existe.")
        return

    df = pd.read_parquet(file_path)

    # Información general
    print(f"\nShape: {df.shape}")
    print(f"Filas   : {df.shape[0]:,}")
    print(f"Columnas: {df.shape[1]}")

    # Columnas
    print("\nColumnas:")
    print(df.columns.tolist())

    # Tipos de datos
    print("\nTipos de datos:")
    print(df.dtypes)

    # Valores nulos
    print("\nValores nulos:")
    nulos = pd.DataFrame({
        "Nulos": df.isnull().sum(),
        "% Nulos": (df.isnull().mean() * 100).round(2)
    })

    print(nulos.sort_values("% Nulos", ascending=False))

    # Duplicados
    print("\nDuplicados:")
    print(df.duplicated().sum())

    # Memoria utilizada
    print("\nMemoria utilizada:")
    print(f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    # Primeros registros
    print("\nPrimeras 5 filas:")
    print(df.head())


if __name__ == "__main__":

    archivos = [
        "data/bronze/bronze_steamspy.parquet",
        "data/bronze/bronze_metacritic.parquet",
        # "data/silver/silver.parquet",
    ]

    for archivo in archivos:
        profile_parquet(archivo)