import pandas as pd
# Importamos las funciones del archivo de calidad
import data_quality
import schema_validation


def main():
    print("========================================")
    print("INICIANDO PIPELINE: BRONZE -> SILVER")
    print("========================================")

    # 1. Cargar datos Bronze
    print("\n[1/14] Cargando archivos Parquet desde Bronze...")
    metacritic = pd.read_parquet("data/bronze/bronze_metacritic.parquet")
    steamspy = pd.read_parquet("data/bronze/bronze_steamspy.parquet")

    # 2. Estandarizar columnas
    print("\n[2/14] Estandarizando nombres de columnas...")
    metacritic = data_quality.standardize_columns(metacritic)


    # 3. Eliminar duplicados
    print("\n[3/14] Eliminando registros duplicados...")
    metacritic = data_quality.remove_duplicates(
    metacritic,
    "appid"
    )

    steamspy = data_quality.remove_duplicates(
    steamspy,
    "appid"
    )


    # 4. Validar e Integrar
    print("\n[4/14] Validando llaves e integrando datasets...")
    silver = data_quality.validate_and_merge(metacritic, steamspy)

    # 5. Limpieza de calidad sobre el dataset integrado
    print("\n[5/14] Ejecutando limpieza de nombres y caracteres...")
    silver = data_quality.clean_game_names(silver)


    # 6. Estandarización de tipos de datos
    print("\n[6/14] Estandarizando tipos de datos...")
    silver = data_quality.standardize_data_types(silver)


    # 7. Feature Engineering
    print("\n[7/14] Creando variables derivadas...")
    silver = data_quality.create_features(silver)

    # 8. Pandera
    print("\n[8/14] Validando esquema Pandera...")
    silver = schema_validation.validate_schema(silver)


    # 9. Normalizando variables
    print("\n[9/14] Normalizando variables...")
    silver = data_quality.normalize_features(silver)


    # 10. Optimización de memoria
    print("\n[10/14] Optimizando memoria...")

    silver_before = silver.copy()
    silver = data_quality.optimize_memory(silver)


   # 11. Benchmark de vectorización
    print("\n[11/14] Ejecutando benchmark de vectorización...")
    data_quality.benchmark_vectorization(silver)


    # 12. Gráfico de optimización
    print("\n[12/14] Generando gráfico de memoria...")

    data_quality.plot_memory_optimization(
    silver_before,
    silver
    )


    # 13. Control de calidad final (Auditoría)
    print("\n[13/14] Ejecutando auditoría final...")
    data_quality.verify_final_quality(silver)


    # 14. Guardar datos en Silver
    print("\n[14/14] Guardando dataset limpio en Capa Silver...")
    silver.to_parquet("data/silver/silver.parquet", index=False)


    print("\n========================================")
    print("PIPELINE FINALIZADO CON ÉXITO")
    print("========================================")
 
if __name__ == "__main__":
    main()