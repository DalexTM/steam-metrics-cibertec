import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import numpy as np
import time


def standardize_columns(metacritic_df: pd.DataFrame) -> pd.DataFrame:
    """Estandariza los nombres de las columnas de Metacritic."""
    return metacritic_df.rename(columns={"AppID": "appid", "Name": "name"})


def remove_duplicates(df: pd.DataFrame, key: str) -> pd.DataFrame:
    """
    Elimina registros duplicados según una llave.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame a limpiar.
    key : str
        Columna llave para identificar duplicados.

    Returns
    -------
    pd.DataFrame
        DataFrame sin duplicados.
    """

    before = len(df)

    df = df.drop_duplicates(subset=[key], keep="first")

    removed = before - len(df)

    print(f"Duplicados eliminados por '{key}': {removed}")

    return df




def validate_and_merge(
    metacritic_df: pd.DataFrame, steamspy_df: pd.DataFrame
) -> pd.DataFrame:
    """Imprime diagnósticos de llaves y realiza el inner join."""
    # Impresiones de diagnóstico
    print("\n--- Diagnóstico de Llaves de Integración ---")
    print(f"Tipo dato appid - Metacritic: {metacritic_df['appid'].dtype}")
    print(f"Tipo dato appid - SteamSpy: {steamspy_df['appid'].dtype}")
    print(f"IDs únicos - Metacritic: {metacritic_df['appid'].nunique()}")
    print(f"IDs únicos - SteamSpy: {steamspy_df['appid'].nunique()}")

    coincidencias = set(metacritic_df["appid"]) & set(
        steamspy_df["appid"]
    )
    print(f"Juegos en común: {len(coincidencias):,}")

    # Integración de bases de datos
    silver_df = pd.merge(
        metacritic_df, steamspy_df, on="appid", how="inner"
    )
    print(f"Dataset tras inner join: {silver_df.shape}")
    return silver_df


def clean_game_names(silver_df: pd.DataFrame) -> pd.DataFrame:
    """Compara, resuelve nulos y limpia caracteres especiales de los nombres."""
    df = silver_df.copy()

    # Diagnóstico de diferencias
    print("\n--- Análisis de Nombres (x vs y) ---")
    iguales = (df["name_x"] == df["name_y"]).all()
    print(f"¿Los nombres son 100% iguales?: {iguales}")

    if not iguales:
        diferencias = df[df["name_x"] != df["name_y"]]
        print("Muestra de diferencias:")
        print(diferencias[["appid", "name_x", "name_y"]].head(5))

    # Limpieza de nombres
    df["name"] = df["name_y"].fillna(df["name_x"])
    df["name"] = (
        df["name"]
        .str.replace("™", "", regex=False)
        .str.replace("®", "", regex=False)
        .str.strip()
    )

    # Eliminar columnas sobrantes
    df.drop(columns=["name_x", "name_y"], inplace=True)
    return df


def verify_final_quality(silver_df: pd.DataFrame):
    """Realiza la revisión final de duplicados y nulos para los logs."""
    print("\n--- Reporte Final de Calidad Silver ---")
    print(f"Columnas finales: {silver_df.columns.tolist()}")
    print(f"Estructura final: {silver_df.shape}")
    print(f"Duplicados totales: {silver_df.duplicated().sum()}")
    print("\nPorcentaje de valores nulos por columna:")
    print((silver_df.isnull().mean() * 100).sort_values(ascending=False))


def standardize_data_types(silver_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte las columnas a su tipo de dato correspondiente.
    """

    df = silver_df.copy()

    # ==========================
    # Variables de fecha
    # ==========================
    if "Release_date" in df.columns:
        df["Release_date"] = pd.to_datetime(
            df["Release_date"],
            errors="coerce"
        )

    # ==========================
    # Variables numéricas
    # ==========================
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
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    # ==========================
    # Variables booleanas
    # ==========================
    columnas_bool = [
        "Windows",
        "Mac",
        "Linux"
    ]

    for col in columnas_bool:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .map({
                    "True": True,
                    "False": False
                })
            )

    return df


def create_features(silver_df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea variables derivadas (Feature Engineering)
    y clasificaciones para el dataset Silver.
    """

    df = silver_df.copy()

    # ==========================
    # Variables derivadas
    # ==========================

    # Total de reseñas
    df["total_reviews"] = (
        df["positive"] + df["negative"]
    )

    # Tasa de aprobación
    df["approval_rate"] = (
        df["positive"] / df["total_reviews"]
    )

    # Año de lanzamiento
    df["release_year"] = (
        df["Release_date"].dt.year
    )

    # Antigüedad del juego
    df["game_age"] = (
        2026 - df["release_year"]
    )

    # Diferencia entre crítica y usuarios
    df["score_gap"] = (
        df["Metacritic_score"] - df["userscore"]
    )

    print("\n--- Variables Derivadas ---")
    print(
        df[
            [
                "total_reviews",
                "approval_rate",
                "release_year",
                "game_age",
                "score_gap",
            ]
        ].head()
    )

    # ==========================
    # Binning
    # ==========================

    df["price_range"] = pd.cut(
        df["price"],
        bins=[0, 1000, 3000, 6000, float("inf")],
        labels=[
            "Bajo",
            "Medio",
            "Alto",
            "Premium",
        ],
        include_lowest=True,
    )

    print("\n--- Binning Precio ---")
    print(df[["price", "price_range"]].head())

    return df


def normalize_features(silver_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza variables numéricas utilizando Min-Max Scaling.
    """

    df = silver_df.copy()

    # ==========================
    # Conversión de precio
    # ==========================

    # Precio original viene en centavos
    df["price_usd"] = df["price"] / 100

    # ==========================
    # Normalización
    # ==========================

    scaler = MinMaxScaler()

    df["price_norm"] = scaler.fit_transform(
        df[["price_usd"]]
    )

    print("\n--- Normalización de Precio ---")
    print(df[["price", "price_usd", "price_norm"]].head())

    return df



def optimize_memory(silver_df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimiza el uso de memoria mediante downcasting y
    conversión de columnas categóricas.
    """

    df = silver_df.copy()

    def memory_mb(dataframe):
        return dataframe.memory_usage(deep=True).sum() / (1024 ** 2)

    before = memory_mb(df)

    print("\n--- Optimización de Memoria ---")
    print(f"Memoria antes: {before:.2f} MB")

    # ==========================
    # Downcasting enteros
    # ==========================
    integer_columns = [
        "appid",
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
        "ccu",
        "release_year",
        "game_age",
        "total_reviews",
    ]

    for col in integer_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                downcast="integer"
            )

    # ==========================
    # Downcasting float
    # ==========================
    float_columns = [
        "userscore",
        "price",
        "initialprice",
        "discount",
        "approval_rate",
        "score_gap",
        "price_usd",
        "price_norm",
    ]

    for col in float_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                downcast="float"
            )

    # ==========================
    # Variables categóricas
    # ==========================
    category_columns = [
        "Genres",
        "Developers",
        "Publishers",
        "Categories",
        "price_range",
    ]

    for col in category_columns:
        if col in df.columns:
            df[col] = df[col].astype("category")

    after = memory_mb(df)

    print(f"Memoria después: {after:.2f} MB")
    print(f"Ahorro: {(1 - after / before) * 100:.2f}%")

    return df



def plot_memory_optimization(
    before_df: pd.DataFrame,
    after_df: pd.DataFrame,
) -> None:
    """
    Genera un gráfico comparando el uso de memoria
    antes y después del downcasting.
    """

    mem_before = (
        before_df.memory_usage(deep=True)[1:] / 1024
    )

    mem_after = (
        after_df.memory_usage(deep=True)[1:] / 1024
    )

    total_before = before_df.memory_usage(deep=True).sum()
    total_after = after_df.memory_usage(deep=True).sum()

    saving = (
        1 - (total_after / total_before)
    ) * 100

    x = np.arange(len(mem_before.index))
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 5))

    ax.bar(
        x - width / 2,
        mem_before,
        width,
        label="Antes"
    )

    ax.bar(
        x + width / 2,
        mem_after,
        width,
        label="Después"
    )

    ax.set_xticks(x)
    ax.set_xticklabels(
        mem_before.index,
        rotation=45,
        ha="right"
    )

    ax.set_ylabel("KB")

    ax.set_title(
        f"Uso de memoria por columna\n"
        f"Ahorro total: {saving:.2f}%"
    )

    ax.legend()

    plt.tight_layout()

    plt.savefig(
        "data/silver/memory_optimization.png",
        dpi=300
    )

    plt.close()

    print(
        "Gráfico guardado en:"
        " data/silver/memory_optimization.png"
    )




def benchmark_vectorization(silver_df: pd.DataFrame) -> None:
    """
    Compara el rendimiento entre un loop, apply()
    y una operación vectorizada.
    """

    print("\n--- Benchmark de Vectorización ---")

    df = silver_df[["price", "discount"]].copy()

    # =====================
    # Loop
    # =====================
    t0 = time.perf_counter()

    result_loop = []

    for row in df.itertuples(index=False):
        value =  row[0] * (1 - row[1])
        result_loop.append(value)

    t_loop = time.perf_counter() - t0

    # =====================
    # Apply
    # =====================
    t0 = time.perf_counter()

    result_apply = df.apply(
        lambda r: r["price"] * (1 - r["discount"]),
        axis=1
    )

    t_apply = time.perf_counter() - t0

    # =====================
    # Vectorizado
    # =====================
    t0 = time.perf_counter()

    result_vector = (
        df["price"] * (1 - df["discount"])
    )

    t_vector = time.perf_counter() - t0

    print(f"Loop:        {t_loop:.4f} s")
    print(f"Apply:       {t_apply:.4f} s")
    print(f"Vectorizado: {t_vector:.4f} s")

    print(
        f"Speedup Loop → Vectorizado: "
        f"{t_loop / t_vector:.1f}x"
    )

    print(
        f"Speedup Apply → Vectorizado: "
        f"{t_apply / t_vector:.1f}x"
    )

    print(
        "Resultados iguales:",
        np.allclose(result_loop, result_vector)
    )
