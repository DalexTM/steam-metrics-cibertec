# 🎮 Sistema de Métricas e Insights de Steam y Metacritic

**Curso:** Lenguaje de Ciencia de Datos II (4364)  
**Institución:** CIBERTEC · Ciclo 4 · 2026  
**Requisitos de Python:** `Python >= 3.12`

---

## 📌 1. Descripción del Proyecto

Este proyecto consiste en una plataforma integral de datos que centraliza, limpia, estandariza, enriquece y visualiza la información de más de **78,000 videojuegos de PC**. Unifica los datos de rendimiento en tiempo real descargados desde la API de **SteamSpy** con las calificaciones y críticas especializadas del dataset de **Metacritic** (descargado automáticamente desde Kaggle).

El sistema implementa una **Arquitectura en Capas Medallion (Bronze ➔ Silver ➔ Gold)** que optimiza el almacenamiento en archivos columnares comprimidos (`Parquet`), culminando en una **Data App interactiva desarrollada en Streamlit** en modo oscuro (Steam Navy) totalmente **modularizada**, capaz de resolver preguntas estratégicas del mercado de videojuegos.

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
 │ - Optimización de memoria y tipos categóricos                    │
 │ - Persistencia optimizada en data/gold/steam_metrics_gold.parquet│
 └────────────────────────────────┬─────────────────────────────────┘
                                  │
                                  ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │ DATA APP MODULARIZADA (Streamlit - app.py + src/dashboard/)      │
 │ - Dashboard interactivo con tema oscuro (Steam Navy)             │
 │ - Barra lateral con filtros dinámicos multicriterio              │
 │ - Indicadores Globales (KPI Cards)                               │
 │ - 8 Pestañas de Análisis Analítico y Exploración                 │
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
   *(uv gestiona automáticamente el entorno virtual y las dependencias de pyproject.toml / uv.lock)*
   ```bash
   uv run streamlit run app.py
   ```

3. **(Opcional) Ejecutar el Pipeline ETL por consola (CLI interactivo):**
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

El código se encuentra desacoplado y modularizado siguiendo principios de responsabilidad única (SRP):

```text
steam-metrics-cibertec/
├── .gitignore                    # Excluye .venv, logs y archivos pesados
├── pyproject.toml                # Gestión moderna y reproducible de dependencias con uv
├── requirements.txt              # Dependencias principales documentadas y comentadas
├── README.md                     # Documentación principal del proyecto
├── main.py                       # Menú interactivo CLI para orquestar el pipeline ETL
├── app.py                        # Punto de entrada principal de la aplicación Streamlit
├── data/                         # Almacenamiento local particionado por capa
│   ├── raw/                      # Archivos brutos (SteamSpy Avro / Metacritic CSV)
│   ├── bronze/                   # Parquets iniciales procesados
│   ├── silver/                   # silver.parquet (Limpio, validado e imputado)
│   └── gold/                     # steam_metrics_gold.parquet (Datamart de negocio)
├── logs/                         # Bitácoras de ejecución por script con timestamp
│   ├── main.log
│   ├── ingest_steamspy.log
│   ├── ingest_metacritic.log
│   ├── transform_bronze_to_silver.log
│   └── transform_silver_to_gold.log
└── src/                          # Código fuente modularizado
    ├── bronze/                   # Ingesta y conversión inicial a Parquet
    │   ├── ingest_steamspy.py
    │   ├── ingest_metacritic.py
    │   ├── transform_steamspy_parquet.py
    │   └── transform_metacritic_parquet.py
    ├── silver/                   # Limpieza, imputación KNN y validación de esquemas
    │   ├── transform_bronze_to_silver.py
    │   ├── data_quality.py
    │   └── schema_validation.py
    ├── gold/                     # Construcción del Datamart y métricas analíticas
    │   └── transform_silver_to_gold.py
    └── dashboard/                # Módulo desacoplado de la interfaz de usuario
        ├── constants.py          # Estilos CSS (Tema Steam Navy), paletas de color y encabezado
        ├── loader.py             # Carga optimizada y cacheada de datos Gold
        ├── components/           # Componentes reutilizables de UI
        │   ├── sidebar.py        # Barra lateral con filtros dinámicos multicriterio
        │   └── kpi_cards.py      # Tarjetas de métricas e indicadores globales (KPIs)
        └── views/                # Vistas independientes por pestaña de análisis
            ├── tab1_critica_ventas.py        # Pestaña 1: Crítica vs Éxito Comercial
            ├── tab2_discrepancia.py          # Pestaña 2: Discrepancia Crítica vs Comunidad
            ├── tab3_generos_rentables.py      # Pestaña 3: Géneros más Rentables
            ├── tab4_satisfaccion_tiempo.py   # Pestaña 4: Satisfacción vs Tiempo de Juego
            ├── tab5_estrategia_precios.py    # Pestaña 5: Estrategia de Precios
            ├── tab6_generos_ccu.py           # Pestaña 6: Géneros vs Peak CCU
            ├── tab7_explorador_datos.py      # Pestaña 7: Explorador de Datos Interactivo
            └── tab8_correlaciones.py         # Pestaña 8: Matriz de Correlaciones
```

---

## 📊 5. Preguntas de Negocio y Pestañas del Dashboard (`app.py`)

El Dashboard interactivo está organizado en **8 Pestañas Especializadas**, ofreciendo respuestas respaldadas por datos a las preguntas estratégicas del mercado:

| Pestaña | Pregunta de Negocio / Objetivo | Tipos de Gráficos | Justificación Analítica e Insights |
|---|---|---|---|
| **1. Crítica vs Éxito Comercial** | *¿Existe relación entre la nota de la crítica y el éxito comercial (ventas/jugadores)?* | **Scatter Plot de Burbujas** (`px.scatter`) y **Barras Horizontales** (`px.bar`) | Evalúa la correlación entre `Metacritic Score` e `Ingresos Estimados (USD)` donde el tamaño de burbuja refleja el `Peak CCU`. Identifica los títulos líderes en ventas y concurrencia. |
| **2. Discrepancia Crítica vs Comunidad** | *¿Qué brecha existe entre la crítica especializada (Metacritic) y los jugadores (Steam)?* | **Scatter Plot con Línea 1:1** (`px.scatter`) y **Donut Chart** (`px.pie`) | Compara `Metacritic Score` vs `Tasa de Aprobación (%)` con línea de paridad 1:1, clasificando juegos sobrevalorados por la crítica vs joyas aclamadas por la comunidad. |
| **3. Géneros más Rentables** | *¿Cuáles son los géneros más rentables y cómo se distribuye su volumen de mercado?* | **Barras Horizontales Agrupadas** y **Box Plot de Precios** (`px.box`) | Desanida géneros múltiples (`explode`) para calcular ingresos totales y medianos, contrastando volumen de títulos frente a rentabilidad y dispersión de precios. |
| **4. Satisfacción vs Tiempo de Juego** | *¿Mayor tiempo de juego se traduce en una mayor satisfacción de los usuarios?* | **Scatter Plot** (`px.scatter`) y **Histograma / Densidad** | Relaciona las horas promedio de juego (`playtime_hours`) con la aprobación (`approval_rate`), identificando juegos de nicho altamente fidelizados vs títulos con problemas de retención. |
| **5. Estrategia de Precios** | *¿Cómo se distribuyen los videojuegos según su esquema de monetización y precio?* | **Gráfico de Barras por Rango**, **Histograma de Precios** y **Scatter Plot Precio vs Score** | Clasifica el catálogo en Free-to-Play, Económico, Estándar y Premium. Evalúa la distribución real de precios y cómo influye el costo en la percepción de los usuarios. |
| **6. Géneros vs Peak CCU** | *¿Qué géneros concentran el mayor número de usuarios simultáneos en hora pico?* | **Barras Horizontales Ranking** (`px.bar`) | Evalúa la capacidad de retención y concurrencia máxima (`Peak CCU` promedio y mediano) por género, exigiendo un umbral mínimo de juegos para evitar distorsiones por outliers. |
| **7. Explorador de Datos** | *Inspección individual, búsqueda directa y exportación de datos* | **Tabla Interactiva** (`st.dataframe`) | Permite realizar búsquedas por texto, ordenar por cualquier métrica del Datamart Gold y explorar los datos filtrados en tiempo real. |
| **8. Correlaciones** | *¿Cómo se correlacionan cuantitativamente las métricas clave de la plataforma?* | **Heatmap de Correlación** (`go.Heatmap`) | Calcula la matriz de Coeficientes de Correlación de Pearson entre Metascore, Aprobación, Precio, Horas de Juego, Peak CCU e Ingresos Estimados. |

---

## 🧩 6. Arquitectura Modular del Dashboard (`src/dashboard/`)

La interfaz de usuario fue refactorizada a un modelo modular desacoplado para asegurar escalabilidad y fácil mantenimiento:

1. **`loader.py`**: Utiliza `@st.cache_data` para cargar el archivo Parquet de la Capa Gold de forma ultra rápida en memoria.
2. **`constants.py`**: Centraliza el CSS personalizado, paletas de colores corporativas (Steam Navy) y componentes de cabecera.
3. **`components/`**: Módulos reutilizables independientes:
   * **`sidebar.py`**: Gestiona el estado de los filtros (búsqueda de texto, rangos de año, géneros dinámicos, filtros de precios y scores) y devuelve el DataFrame filtrado.
   * **`kpi_cards.py`**: Renderiza tarjetas métricas dinámicas (Total Juegos, Ingresos Estimados, Peak CCU Máximo, Tasa Promedio de Aprobación).
4. **`views/`**: Cada pestaña cuenta con su propio archivo aislado (`tab1` a `tab8`), facilitando la adición o ajuste de nuevos análisis sin afectar el resto del sistema.

---

## 🌐 7. Despliegue en la Nube (Streamlit Cloud)

El proyecto se encuentra preparado para ser desplegado en plataformas en la nube:
* **Enlace del Dashboard en Vivo:** `https://steam-metrics-cibertec.streamlit.app/`
* **Repositorio en GitHub:** `https://github.com/DalexTM/steam-metrics-cibertec`

---

## 🛡️ 8. Buenas Prácticas Aplicadas

* ✅ **Sin entorno virtual en repositorio:** `.venv` correctamente excluido mediante `.gitignore`.
* ✅ **Sin credenciales expuestas:** Libre de secretos, tokens o archivos `.env`.
* ✅ **Arquitectura Modular Extensible:** Separación estricta de responsabilidades entre pipelines ETL (`src/bronze`, `src/silver`, `src/gold`) y frontend (`src/dashboard`).
* ✅ **Validación de Datos Rigurosa:** Control de calidad y consistencia con `pandera` y `scikit-learn` (KNNImputer).
* ✅ **Trazabilidad y Observabilidad:** Registro unificado de eventos en `logs/*.log` con formato estructurado `%(asctime)s [%(levelname)s] %(message)s`.