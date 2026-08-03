import os
import logging
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsRegressor

carpeta_logs = "logs"
os.makedirs(carpeta_logs, exist_ok=True)
ruta_log = os.path.join(carpeta_logs, "data_quality.log")

logger = logging.getLogger("data_quality")
logger.setLevel(logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(ruta_log, encoding="utf-8")
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)


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

    logger.info(f"Duplicados eliminados por '{key}': {removed}")

    return df


def validate_and_merge(
    metacritic_df: pd.DataFrame, steamspy_df: pd.DataFrame
) -> pd.DataFrame:
    """Imprime diagnósticos de llaves y realiza el inner join."""
    # Impresiones de diagnóstico
    logger.info("\n--- Diagnóstico de Llaves de Integración ---")
    logger.info(f"Tipo dato appid - Metacritic: {metacritic_df['appid'].dtype}")
    logger.info(f"Tipo dato appid - SteamSpy: {steamspy_df['appid'].dtype}")
    logger.info(f"IDs únicos - Metacritic: {metacritic_df['appid'].nunique()}")
    logger.info(f"IDs únicos - SteamSpy: {steamspy_df['appid'].nunique()}")

    coincidencias = set(metacritic_df["appid"]) & set(steamspy_df["appid"])
    logger.info(f"Juegos en común: {len(coincidencias):,}")

    # Integración de bases de datos
    silver_df = pd.merge(metacritic_df, steamspy_df, on="appid", how="inner")
    logger.info(f"Dataset tras inner join: {silver_df.shape}")
    return silver_df


def clean_game_names(silver_df: pd.DataFrame) -> pd.DataFrame:
    """Compara, resuelve nulos y limpia caracteres especiales de los nombres."""
    df = silver_df.copy()

    # Diagnóstico de diferencias
    logger.info("\n--- Análisis de Nombres (x vs y) ---")
    iguales = (df["name_x"] == df["name_y"]).all()
    logger.info(f"¿Los nombres son 100% iguales?: {iguales}")

    if not iguales:
        diferencias = df[df["name_x"] != df["name_y"]]
        logger.info(
            "Muestra de diferencias:\n%s",
            diferencias[["appid", "name_x", "name_y"]].head(5),
        )

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
    logger.info("\n--- Reporte Final de Calidad Silver ---")
    logger.info(f"Columnas finales: {silver_df.columns.tolist()}")
    logger.info(f"Estructura final: {silver_df.shape}")
    logger.info(f"Duplicados totales: {silver_df.duplicated().sum()}")
    logger.info(
        "\nPorcentaje de valores nulos por columna:\n%s",
        (silver_df.isnull().mean() * 100).sort_values(ascending=False),
    )


def standardize_data_types(silver_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte las columnas a su tipo de dato correspondiente.
    """

    df = silver_df.copy()

    # ==========================
    # Variables de fecha
    # ==========================
    if "Release_date" in df.columns:
        df["Release_date"] = pd.to_datetime(df["Release_date"], errors="coerce")

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
        "ccu",
    ]

    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ==========================
    # Variables booleanas
    # ==========================
    columnas_bool = ["Windows", "Mac", "Linux"]

    for col in columnas_bool:
        if col in df.columns:
            df[col] = (
                df[col].astype(str).str.strip().map({"True": True, "False": False})
            )

    return df


def impute_missing_scores(silver_df: pd.DataFrame) -> pd.DataFrame:
    """
    Imputa valores faltantes/cero en Metacritic_score utilizando KNeighborsRegressor
    basado en métricas de precio, reseñas y tiempo de juego.
    """
    df = silver_df.copy()

    logger.info("===== Imputación de Metacritic_score con KNN =====")

    # Reemplazar ceros (ausencia de score) por NaN
    df["Metacritic_score"] = df["Metacritic_score"].replace(0, np.nan)

    nulos_meta = df["Metacritic_score"].isnull().sum()
    logger.info("Registros con Metacritic_score nulos a imputar: %d", nulos_meta)

    # Garantizar presencia de price_usd para la distancia
    if "price_usd" not in df.columns and "price" in df.columns:
        df["price_usd"] = df["price"] / 100

    feature_cols = [
        c for c in ["price_usd", "positive", "negative", "Peak_CCU", "Average_playtime_forever"]
        if c in df.columns
    ]

    if nulos_meta > 0 and len(feature_cols) > 0:
        mask_missing = df["Metacritic_score"].isnull()
        mask_known = ~mask_missing

        if mask_known.sum() > 0 and mask_missing.sum() > 0:
            # Escalar únicamente las variables predictoras
            scaler = MinMaxScaler()
            X_features = df[feature_cols].fillna(0)
            X_scaled = scaler.fit_transform(X_features)

            X_train = X_scaled[mask_known]
            y_train = df.loc[mask_known, "Metacritic_score"]
            X_test = X_scaled[mask_missing]

            # KNeighborsRegressor usa KD-Tree/Ball-Tree y paralelismo (n_jobs=-1)
            knn = KNeighborsRegressor(n_neighbors=5, weights="uniform", n_jobs=-1)
            knn.fit(X_train, y_train)

            df.loc[mask_missing, "Metacritic_score"] = np.round(knn.predict(X_test), 1)

        logger.info(
            "Imputación KNN finalizada con éxito. Nulos restantes en Metacritic_score: %d",
            df["Metacritic_score"].isnull().sum()
        )

    return df


def create_features(silver_df):
    """
    Crea nuevas variables derivadas y realiza agregaciones.
    """

    logger.info("===== Enriquecimiento interno =====")

    df = silver_df.copy()

    # =====================================
    # Variables derivadas
    # =====================================

    # Precio en dólares
    df["price_usd"] = df["price"] / 100

    # Total de reseñas
    df["total_reviews"] = df["positive"] + df["negative"]

    # Tasa de aprobación
    df["approval_rate"] = df["positive"] / df["total_reviews"]

    # Año de lanzamiento
    df["release_year"] = df["Release_date"].dt.year

    # Antigüedad del juego
    df["game_age"] = 2026 - df["release_year"]

    # Diferencia entre crítica y usuarios
    df["score_gap"] = df["Metacritic_score"] - df["userscore"]

    logger.info(
        "\nVariables derivadas:\n%s",
        df[
            ["price_usd", "approval_rate", "release_year", "game_age", "score_gap"]
        ].head(),
    )

    # =====================================
    # Agregaciones
    # =====================================

    logger.info("\n--- Promedio de jugadores por género ---")

    avg_players = (
        df.groupby("Genres", as_index=False)["ccu"]
        .mean()
        .sort_values("ccu", ascending=False)
    )

    logger.info("\n%s", avg_players.head(10).to_string(index=False))

    logger.info("\n--- Precio promedio por género ---")

    avg_price = (
        df.groupby("Genres", as_index=False)["price_usd"]
        .mean()
        .sort_values("price_usd", ascending=False)
    )

    logger.info("\n%s", avg_price.head(10).to_string(index=False))

    logger.info("\n--- Metacritic promedio por género ---")

    avg_metacritic = (
        df.groupby("Genres", as_index=False)["Metacritic_score"]
        .mean()
        .sort_values("Metacritic_score", ascending=False)
    )

    logger.info("\n%s", avg_metacritic.head(10).to_string(index=False))

    # =====================================
    # Binning
    # =====================================

    df["price_range"] = pd.cut(
        df["price_usd"],
        bins=[0, 10, 30, 60, float("inf")],
        labels=["Bajo", "Medio", "Alto", "Premium"],
        include_lowest=True,
    )

    logger.info(
        "\nClasificación por rango de precio:\n%s",
        df[["price_usd", "price_range"]].head(),
    )

    price_counts = df["price_range"].value_counts().sort_index()

    logger.info("\n%s", price_counts)

    price_counts = df["price_range"].value_counts().sort_index()

    plt.figure(figsize=(8, 5))

    plt.bar(price_counts.index.astype(str), price_counts.values)

    plt.title("Distribución de juegos por rango de precio")
    plt.xlabel("Rango de precio (USD)")
    plt.ylabel("Cantidad de juegos")

    # Mostrar la cantidad encima de cada barra
    for i, v in enumerate(price_counts.values):
        plt.text(i, v, str(v), ha="center", va="bottom")

    plt.tight_layout()
    plt.show()

    return df


def normalize_features(silver_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza variables numéricas utilizando Min-Max Scaling.
    """

    df = silver_df.copy()

    # ==========================
    # Normalización
    # ==========================

    scaler = MinMaxScaler()

    df["price_norm"] = scaler.fit_transform(df[["price_usd"]])

    logger.info("\n--- Normalización de Precio ---")
    logger.info("\n%s", df[["price", "price_usd", "price_norm"]].head())

    return df


def optimize_memory(silver_df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimiza el uso de memoria mediante downcasting y
    conversión de columnas categóricas.
    """

    df = silver_df.copy()

    def memory_mb(dataframe):
        return dataframe.memory_usage(deep=True).sum() / (1024**2)

    before = memory_mb(df)

    logger.info("\n--- Optimización de Memoria ---")
    logger.info(f"Memoria antes: {before:.2f} MB")

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
            df[col] = pd.to_numeric(df[col], downcast="integer")

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
            df[col] = pd.to_numeric(df[col], downcast="float")

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

    logger.info(f"Memoria después: {after:.2f} MB")
    logger.info(f"Ahorro: {(1 - after / before) * 100:.2f}%")

    return df


def plot_memory_optimization(
    before_df: pd.DataFrame,
    after_df: pd.DataFrame,
) -> None:
    """
    Genera un gráfico comparando el uso de memoria
    antes y después del downcasting.
    """

    mem_before = before_df.memory_usage(deep=True)[1:] / 1024

    mem_after = after_df.memory_usage(deep=True)[1:] / 1024

    total_before = before_df.memory_usage(deep=True).sum()
    total_after = after_df.memory_usage(deep=True).sum()

    saving = (1 - (total_after / total_before)) * 100

    x = np.arange(len(mem_before.index))
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 5))

    ax.bar(x - width / 2, mem_before, width, label="Antes")

    ax.bar(x + width / 2, mem_after, width, label="Después")

    ax.set_xticks(x)
    ax.set_xticklabels(mem_before.index, rotation=45, ha="right")

    ax.set_ylabel("KB")

    ax.set_title(f"Uso de memoria por columna\n" f"Ahorro total: {saving:.2f}%")

    ax.legend()

    plt.tight_layout()

    plt.savefig("data/silver/memory_optimization.png", dpi=300)

    plt.close()

    logger.info("Gráfico guardado en: data/silver/memory_optimization.png")


def benchmark_vectorization(silver_df: pd.DataFrame) -> None:
    """
    Compara el rendimiento entre un loop, apply()
    y una operación vectorizada.
    """

    logger.info("\n--- Benchmark de Vectorización ---")

    df = silver_df[["price", "discount"]].copy()

    # =====================
    # Loop
    # =====================
    t0 = time.perf_counter()

    result_loop = []

    for row in df.itertuples(index=False):
        value = row[0] * (1 - row[1])
        result_loop.append(value)

    t_loop = time.perf_counter() - t0

    # =====================
    # Apply
    # =====================
    t0 = time.perf_counter()

    result_apply = df.apply(lambda r: r["price"] * (1 - r["discount"]), axis=1)

    t_apply = time.perf_counter() - t0

    # =====================
    # Vectorizado
    # =====================
    t0 = time.perf_counter()

    result_vector = df["price"] * (1 - df["discount"])

    t_vector = time.perf_counter() - t0

    logger.info(f"Loop:        {t_loop:.4f} s")
    logger.info(f"Apply:       {t_apply:.4f} s")
    logger.info(f"Vectorizado: {t_vector:.4f} s")

    logger.info(f"Speedup Loop → Vectorizado: {t_loop / t_vector:.1f}x")

    logger.info(f"Speedup Apply → Vectorizado: {t_apply / t_vector:.1f}x")

    logger.info(f"Resultados iguales: {np.allclose(result_loop, result_vector)}")
