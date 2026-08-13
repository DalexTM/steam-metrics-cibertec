# 🎮 Sistema de Métricas e Insights de Steam y Metacritic

**Curso:** Lenguaje de Ciencia de Datos II (4364)  
**Institución:** CIBERTEC · Ciclo 4 · 2026  
**Requisitos de Python:** `Python >= 3.12`

---

## 📌 1. Descripción del Proyecto

Este proyecto consiste en una plataforma integral de datos que centraliza, limpia, estandariza, enriquece y visualiza la información de más de **78,000 videojuegos de PC**. Unifica los datos de rendimiento en tiempo real descargados desde la API de **SteamSpy** con las calificaciones y críticas especializadas del dataset de **Metacritic** (descargado automáticamente desde Kaggle).

El sistema sigue una **Arquitectura en Capas Medallion (Bronze ➔ Silver ➔ Gold)** que optimiza el almacenamiento en archivos columnares comprimidos (`Parquet`), culminando en una **Data App interactiva desarrollada en Streamlit** en modo oscuro que responde a las preguntas clave de negocio del mercado de videojuegos.

---

## 🏛️ 2. Arquitectura de Datos (Medallion Architecture)

```text
       ┌────────────────────────┐         ┌────────────────────────┐
       │   API REST SteamSpy    │         │  KaggleHub Metacritic  │
       └───────────┬────────────┘         └───────────┬────────────┘
                   │                                  │
                   ▼                                  ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │ CAPA BRONZE (Ingesta e Inmutabilidad)                            │
 │ - Descarga de datos en formato Avro con esquema .avsc (SteamSpy) │
 │ - Ingesta/Descarga automática de metacritic.csv desde Kaggle     │
 │ - Conversión inicial a Parquet (data/bronze/)                    │
 └────────────────────────────────┬─────────────────────────────────┘
                                  │
                                  ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │ CAPA SILVER (Limpieza, Calidad y Feature Engineering)            │
 │ - Estandarización de nombres de columnas y tipos de datos        │
 │ - Deduplicación por AppID e integración (Merge)                  │
 │ - Imputación de notas faltantes con KNNImputer (Scikit-Learn)    │
 │ - Validación rigurosa de esquema de datos con Pandera            │
 │ - Persistencia limpia en data/silver/silver.parquet             │
 └────────────────────────────────┬─────────────────────────────────┘
                                  │
                                  ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │ CAPA GOLD (Datamart de Negocio Optimizado)                       │
 │ - Cálculo de ventas/ingresos estimados (estimated_revenue_usd)   │
 │ - Clasificación de precios e indicador de discrepancia           │
 │ - Optimización de memoria (reducción a 5.05 MB en Parquet)       │
 │ - Persistencia optimizada en data/gold/steam_metrics_gold.parquet│
 └────────────────────────────────┬─────────────────────────────────┘
                                  │
                                  ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │ DATA APP (Interfaz de Usuario en Streamlit - app.py)             │
 │ - Dashboard interactivo con tema oscuro (Steam Navy)             │
 │ - 5 Pestañas de Análisis y Filtros dinámicos en Sidebar          │
 └──────────────────────────────────────────────────────────────────┘
```

---

## ⚡ 3. Instrucciones de Instalación y Ejecución Local

### Requisitos Previos
* **Python 3.12 o superior** instalado.
* **Git** configurado.

---

### Opción A: Ejecución recomendada con `uv` (Ultra Rápido)

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/DalexTM/steam-metrics-cibertec.git
   cd steam-metrics-cibertec
   ```

2. **Ejecutar el Dashboard en Streamlit:**
   *(uv instalará automáticamente el entorno y las dependencias indicadas en pyproject.toml / uv.lock)*
   ```bash
   uv run streamlit run app.py
   ```

3. **(Opcional) Ejecutar el Pipeline CLI de procesamiento por consola:**
   ```bash
   uv run main.py
   ```

---

### Opción B: Ejecución tradicional con `pip` y `venv`

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/DalexTM/steam-metrics-cibertec.git
   cd steam-metrics-cibertec
   ```

2. **Crear y activar entorno virtual:**
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Linux/Mac:
   source .venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la Data App de Streamlit:**
   ```bash
   streamlit run app.py
   ```

---

## 📂 4. Estructura de Carpetas del Proyecto

```text
steam-metrics-cibertec/
├── .gitignore                    # Excluye .venv, .env, .log y Parquets locales pesados
├── pyproject.toml                # Gestión moderna de dependencias (uv)
├── requirements.txt              # Exportación de dependencias para Streamlit Cloud
├── README.md                     # Documentación principal del proyecto
├── main.py                       # Menú interactivo CLI para ejecutar el pipeline completo
├── app.py                        # Aplicación Web principal en Streamlit (Dashboard UI)
├── tema6_notebook.ipynb          # Notebook de análisis y referencia del curso
├── data/                         # Almacenamiento local de datos por capa
│   ├── raw/
│   │   ├── metacritic/           # metacritic.csv (Descargado de Kaggle)
│   │   └── steamspy/             # Archivos Avro descargados de la API
│   ├── bronze/                   # Parquets iniciales procesados
│   ├── silver/                   # silver.parquet (Limpio e imputado)
│   └── gold/                     # steam_metrics_gold.parquet (Datamart de negocio)
├── logs/                         # Bitácoras de ejecución por script con timestamp
│   ├── main.log
│   ├── ingest_steamspy.log
│   ├── ingest_metacritic.log
│   ├── transform_bronze_to_silver.log
│   └── transform_silver_to_gold.log
└── src/                          # Código fuente modularizado
    ├── bronze/                   # Ingesta y conversión inicial
    │   ├── ingest_steamspy.py
    │   ├── ingest_metacritic.py
    │   ├── transform_steamspy_parquet.py
    │   └── transform_metacritic_parquet.py
    ├── silver/                   # Limpieza, KNN e integración
    │   ├── transform_bronze_to_silver.py
    │   ├── data_quality.py
    │   └── schema_validation.py
    └── gold/                     # Datamart y métricas analíticas
        └── transform_silver_to_gold.py
```

---

## 📊 5. Preguntas de Negocio Resueltas en el Dashboard (`app.py`)

El Dashboard se encuentra dividido en **5 Pestañas de Análisis**, ofreciendo respuestas respaldadas por datos a las preguntas fundamentales del proyecto:

| Pestaña | Pregunta de Negocio | Tipo de Gráfico Utilizado | Justificación Analítica |
|---|---|---|---|
| **Tab 1** | *¿Existe relación entre la nota de la crítica y el éxito comercial (ventas/jugadores)?* | **Scatter Plot de Burbujas** (`px.scatter`) y **Barras Horizontales** (`px.bar`) | Permite evaluar la correlación entre `Metacritic Score` vs `Ingresos Estimados USD` con el tamaño representando `Peak CCU`. |
| **Tab 2** | *¿Qué discrepancia existe entre la crítica especializada (Metacritic) y la comunidad (Steam)?* | **Scatter Plot con Línea 1:1** (`px.scatter`) y **Donut Chart** (`px.pie`) | Compara `Metacritic Score` vs `Aprobación Comunidad (%)` con una línea de consenso para identificar juegos sobrevalorados o infravalorados. |
| **Tab 3** | *¿Cuáles son los géneros más rentables y cuáles concentran mayor volumen de jugadores?* | **Barras Horizontales Agrupadas** y **Box Plot de Precios** (`px.box`) | Compara los ingresos e historia de usuarios entre géneros y evalúa la dispersión de precios y outliers en el mercado. |
| **Tab 4** | *Explorador de Datos e inspección individual de videojuegos* | **Tabla Interactiva** (`st.dataframe`) | Búsqueda por texto y filtrado directo sobre la tabla consolidada en la Capa Gold. |
| **Tab 5** | *¿Cómo se correlacionan cuantitativamente las métricas principales?* | **Heatmap de Correlación** (`go.Heatmap`) | Matriz del Coeficiente de Correlación de Pearson entre Score, Aprobación, Precio, Horas, CCU e Ingresos. |

---

## 🌐 6. Despliegue en la Nube (Streamlit Cloud)

El proyecto se encuentra desplegado en la nube pública de Streamlit Cloud:
* **Enlace del Dashboard en Vivo:** `[Insertar Enlace de Streamlit Cloud Aquí]`
* **Repositorio Público de GitHub:** `https://github.com/DalexTM/steam-metrics-cibertec`

---

## 🛡️ 7. Buenas Prácticas Aplicadas

* ✅ **Sin entorno virtual en repositorio:** `.venv` excluido en `.gitignore`.
* ✅ **Sin credenciales expuestas:** Libre de archivos `.env` o llaves privadas.
* ✅ **Código Modular y Limpio:** Separación estricta en carpetas `src/bronze`, `src/silver`, `src/gold`.
* ✅ **Trazabilidad mediante Logs:** Bitácoras continuas en `logs/*.log` con formato estructurado `%(asctime)s [%(levelname)s] %(message)s`.
* ✅ **Optimización Extrema de Datos:** Dataset Gold comprimido de 73 MB a **5.05 MB** en Parquet para carga instantánea en memoria RAM (< 15 MB).