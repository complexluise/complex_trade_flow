# Flujos_Diversidad_Comercio_Internacional
# Sistema de Análisis de Datos Comerciales con Grafos

Este proyecto implementa un sistema completo para la extracción, transformación, carga (ETL), análisis y visualización de datos comerciales utilizando una base de datos de grafos Neo4j. El objetivo es analizar la balanza de poder y las estructuras centro-periferia en los datos comerciales globales, proporcionando herramientas de visualización para interpretar estos análisis.

## Características

- **Extracción de Datos**: Automatiza la extracción de datos desde la base de datos BACII y la API del Banco Mundial.
- **Procesamiento ETL**: Transforma y carga los datos en Neo4j para un análisis eficiente con grafos.
- **Análisis de Grafos**: Calcula métricas como centralidad, detecta comunidades y encuentra caminos mínimos.
- **Visualización de Datos**: Genera visualizaciones interactivas de grafos y estadísticas para facilitar la interpretación de los datos.

## Tecnologías Utilizadas

- **Python**: Lenguaje de programación principal.
- **Neo4j**: Base de datos de grafos para almacenamiento y análisis.
- **Py2neo**: Biblioteca Python para interactuar con Neo4j.
- **NetworkX**: Usado para cálculos adicionales de teoría de grafos.
- **Pandas**: Para la manipulación y transformación de datos.
- **Matplotlib/Plotly**: Para la creación de visualizaciones gráficas.
- **Flask/Django**: Para implementar la interfaz de usuario web (opcional).

## Estructura del Proyecto

```plaintext
/proyecto_analisis_grafos
|
|-- graph_database.py       # Define la clase GraphDatabase para interactuar con Neo4j
|-- etl_processor.py        # Implementa la clase ETLProcessor para manejar el proceso ETL
|-- graph_analysis_service.py # Contiene la clase GraphAnalysisService para análisis de grafos
|-- data_visualization_system.py # Define la clase DataVisualizationSystem para visualización de datos
|-- main.py                 # Archivo principal que configura y ejecuta todos los componentes
|-- requirements.txt        # Dependencias de Python necesarias para ejecutar el proyecto
