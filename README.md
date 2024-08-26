# 🌍 trade_network: Desentrañando las Complejidades del Comercio Global

![Versión de Python](https://img.shields.io/badge/python-3.7%2B-blue)
![Licencia](https://img.shields.io/badge/license-MIT-green)

`trade_network` es una poderosa biblioteca de Python diseñada para limpiar y analizar la compleja red del comercio internacional.

## 🚀 Funcionalidades

- **Limpieza de Datos**: Procesa fácilmente los datos crudos de BACI CEPII y del Banco Mundial
- **Creación de Redes**: Construye redes comercio internacional para años específicos
- **Análisis de Diversidad**: Calcula la diversidad de exportaciones e importaciones utilizando la entropía de Shannon
- **Clasificación Flexible**: Agrupa países según varios esquemas (región, nivel de ingresos, etc.)
- **Complejidad Económica**: Analiza métricas de complejidad de productos y países

También contamos con una app en Streamlit para analizar la diversidad económica. Puedes explorarla en [este enlace](https://diversidad-economica.streamlit.app/).

## 🛠 Instalación

```bash
git clone https://github.com/complexluise/Flujos_Diversidad_Comercio_Internacional.git
```

Proximamente instalación por setup o Pypi

## 📊 Inicio Rápido

```python
from complex_trade_flow.networks import TradeNetwork
from complex_trade_flow.utils import ClassificationScheme
from complex_trade_flow.diversity_metrics import DiversityCalculator

# Crear un esquema de clasificación
esquema_regional = ClassificationScheme(
   name="by_region",
   file_path="data/raw_data/world_bank_data/countries.csv",
   key_column="id",
   value_column="region.value"
)

# Inicializar la red comercial
trade_network = TradeNetwork(
   year=2020,
   classification_schemes=[esquema_regional]
)

# Calcular la diversidad de exportación para el sur de Asia
data = trade_network.filter_data_by_entities(
   scheme_name=str(esquema_regional),
   exporters=['South Asia']
)

export_diversity = DiversityCalculator.calculate_diversity_index(data=data)
print(f"Diversidad de productos de exportación para el sur de Asia: {export_diversity:.2f}")
```

## 🧹 Limpieza de Datos

Antes de usar la biblioteca, asegúrate de tener los siguientes archivos de datos:

1. BACI CEPII: Datos de comercio internacional
   - Ubicación: `data/raw_data/BACI_HS92_V202401b/`
   - Archivos: `BACI_HS92_Y{year}_V202401b.csv` para cada año
   - Archivo de códigos de países: `country_codes_V202401b.csv`

2. Datos del Banco Mundial:
   - Ubicación: `data/raw_data/world_bank_data/`
   - Archivo de países: `countries.csv`
   - Archivo del deflactor del PIB: `NY.GDP.DEFL.ZS.AD_1995-2023.csv`

Para limpiar los datos:

```python
from complex_trade_flow.clean_trade_data import DataCleaner

DataCleaner.clean_trade_data()
```

## 🧮 Análisis Avanzado

### Análisis de Complejidad Económica

```python
from complex_trade_flow.analyzers import EconomicComplexityAnalyzer
from complex_trade_flow.constants import EconomicComplexity

EconomicComplexityAnalyzer.run_analysis(
   type_analysis=EconomicComplexity.ENTITY_PRODUCT_DIVERSIFICATION,
   output_directory="data/processed_data/BACI_HS92_V202401b/by_region/diversity/"
)
```


## Contribuciones

Si quieres contribuir puedes empezar solucionando los TODO en el código.

## 🙏 Agradecimientos

- A BACI CEPII por proporcionar completos datos de comercio internacional.
- Al Banco Mundial por indicadores económicos adicionales.
- A GEINCyR por brindar un espacio de aprendizajes y discusión de la complejidad no solo desde un punto de vista técnico sino como un cambio de visión de mundo

---

Construido con 💖 por entusiastas del comercio para entusiastas del comercio. ¡Feliz análisis! 🌐📈