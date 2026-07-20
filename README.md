# 🎮 Proyecto: Sistema de Métricas e Insights de Steam y Metacritic

## 1. Descripción del Proyecto
Este proyecto consiste en la creación de una plataforma de datos que centraliza, procesa y analiza la información de miles de videojuegos de PC. La idea principal es unir los datos de rendimiento en tiempo real de **SteamSpy** con las calificaciones y detalles de **Metacritic**, permitiendo evaluar qué factores hacen que un videojuego sea exitoso en el mercado actual.

El sistema toma datos crudos en formatos diversos (archivos JSON y tablas de Excel/CSV), los limpia, estandariza y guarda en un formato optimizado (`Parquet`) para que luego puedan ser analizados fácilmente a través de gráficos e indicadores clave.

---

## 2. Alcance del Proyecto
* **Ingesta de Datos:** Descarga automática y periódica de datos de la API de SteamSpy y lectura de archivos locales de Metacritic.
* **Procesamiento y Limpieza (Capa Bronze):** Conversión de formatos heterogéneos (JSON/CSV) a archivos `Parquet`, corrigiendo nombres de columnas, rellenando valores faltantes y asegurando que cada variable tenga el tipo de dato correcto (números, texto, booleanos).
* **Reglas de Negocio:** Algoritmos para estimar métricas faltantes, como la generación de *scores* sintéticos para juegos sin puntuación en Metacritic basados en sus picos de jugadores simultáneos.
* **Trazabilidad:** Generación automática de archivos de bitácora (`.log`) para registrar cada etapa del proceso y detectar fallos a tiempo.
* **Visualización (Fase Futura):** Consumo de la información procesada dentro de una aplicación web para la creación de gráficos interactivos y dashboards.

---

## 3. Preguntas de Negocio a Resolver
A través de la información procesada, el proyecto busca dar respuesta a las siguientes interrogantes:

1. **¿Existe relación entre la nota de la crítica (Metacritic) y la cantidad de jugadores simultáneos (Peak CCU)?**
2. **¿Qué géneros y categorías de juegos concentran la mayor cantidad de horas jugadas en promedio?**
3. **¿Afecta la compatibilidad con diferentes sistemas operativos (Windows, Mac, Linux) al éxito del juego?**
4. **¿Cuáles son los desarrolladores y distribuidores (*publishers*) con mejor rendimiento y volumen de ventas?**
5. **¿Qué impacto tienen los descuentos de precio en la acumulación de opiniones positivas por parte de la comunidad?**

---

## 4. Estructura de Carpetas del Proyecto

A continuación se muestra el árbol organizativo del proyecto:

```text
SISTEMA DE METRICAS STEAM/
├── data/
│   ├── raw/                      # Archivos originales sin modificar
│   │   ├── metacritic/           # Datasets de Metacritic (metacritic.csv / .xlsx)
│   │   └── steamspy/             # Archivos JSON descargados desde SteamSpy (page_0.json, etc.)
│   └── bronze/                   # Archivos procesados y optimizados (.parquet)
│       ├── bronze_metacritic.parquet
│       └── bronze_steamspy.parquet
├── logs/                         # Archivos de registro de ejecución por script
│   ├── ingest_steamspy.log
│   ├── transform_metacritic_parquet.log
│   └── transform_steamspy_parquet.log
├── src/                          # Código fuente del proyecto
│   └── bronze/                   # Scripts de carga y transformación inicial
│       ├── ingest_steamspy.py
│       ├── transform_metacritic_parquet.py
│       └── transform_steamspy_parquet.py
├── main.py                       # Script principal para ejecutar todo el flujo
├── pyproject.toml                # Configuración del entorno de Python
├── README.md                     # Documentación general del proyecto
└── uv.lock                       # Archivo de control de dependencias