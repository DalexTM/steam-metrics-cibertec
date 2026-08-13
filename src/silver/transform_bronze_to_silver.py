import os
import logging
import pandas as pd
from src.silver import data_quality, schema_validation

carpeta_logs = "logs"
os.makedirs(carpeta_logs, exist_ok=True)
ruta_log = os.path.join(carpeta_logs, "transform_bronze_to_silver.log")

logger = logging.getLogger("transform_bronze_to_silver")
logger.setLevel(logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(ruta_log, encoding="utf-8")
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)


def main():
    logger.info("========================================")
    logger.info("INICIANDO PIPELINE: BRONZE -> SILVER")
    logger.info("========================================")

    # 1. Cargar datos Bronze
    logger.info("\n[1/14] Cargando archivos Parquet desde Bronze...")
    metacritic = pd.read_parquet("data/bronze/bronze_metacritic.parquet")
    steamspy = pd.read_parquet("data/bronze/bronze_steamspy.parquet")

    logger.info("===== Dimensiones de los datasets =====")
    logger.info(
        f"Metacritic: {metacritic.shape[0]:,} filas y {metacritic.shape[1]} columnas"
    )
    logger.info(f"SteamSpy: {steamspy.shape[0]:,} filas y {steamspy.shape[1]} columnas")

    # 2. Estandarizar columnas
    logger.info("\n[2/14] Estandarizando nombres de columnas...")
    metacritic = data_quality.standardize_columns(metacritic)

    # 3. Eliminar duplicados
    logger.info("\n[3/14] Eliminando registros duplicados...")
    metacritic = data_quality.remove_duplicates(metacritic, "appid")

    steamspy = data_quality.remove_duplicates(steamspy, "appid")

    # 4. Validar e Integrar
    logger.info("\n[4/14] Validando llaves e integrando datasets...")
    silver = data_quality.validate_and_merge(metacritic, steamspy)

    # 5. Limpieza de calidad sobre el dataset integrado
    logger.info("\n[5/14] Ejecutando limpieza de nombres y caracteres...")
    silver = data_quality.clean_game_names(silver)

    # 6. Estandarización de tipos de datos
    logger.info("Tipos de datos antes de la estandarización:\n%s", silver.dtypes)
    logger.info("\n[6/14] Estandarizando tipos de datos...")
    silver = data_quality.standardize_data_types(silver)
    logger.info("\n%s", silver.dtypes)

    # 6.5. Imputación KNN de Metacritic
    logger.info("\n[6.5/14] Imputando Metacritic_score mediante KNNImputer...")
    silver = data_quality.impute_missing_scores(silver)

    # 7. Feature Engineering
    logger.info("\n[7/14] Creando variables derivadas...")
    silver = data_quality.create_features(silver)

    # 8. Pandera
    logger.info("\n[8/14] Validando esquema Pandera...")
    silver = schema_validation.validate_schema(silver)

    # 9. Normalizando variables
    logger.info("\n[9/14] Normalizando variables...")
    silver = data_quality.normalize_features(silver)

    # 10. Optimización de memoria
    logger.info("\n[10/14] Optimizando memoria...")

    silver_before = silver.copy()
    silver = data_quality.optimize_memory(silver)

    # 11. Benchmark de vectorización
    logger.info("\n[11/14] Ejecutando benchmark de vectorización...")
    data_quality.benchmark_vectorization(silver)

    # 12. Gráfico de optimización
    logger.info("\n[12/14] Generando gráfico de memoria...")

    data_quality.plot_memory_optimization(silver_before, silver)

    # 13. Control de calidad final (Auditoría)
    logger.info("\n[13/14] Ejecutando auditoría final...")
    data_quality.verify_final_quality(silver)

    # 14. Guardar datos en Silver
    logger.info("\n[14/14] Guardando dataset limpio en Capa Silver...")
    silver.to_parquet("data/silver/silver.parquet", index=False)

    logger.info("\n========================================")
    logger.info("PIPELINE FINALIZADO CON ÉXITO")
    logger.info("========================================")


if __name__ == "__main__":
    main()
