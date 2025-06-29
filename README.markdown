🚁 Simulador de Logística con Drones - Fase 2
Universidad Católica de TemucoFacultad de Ingeniería - Departamento de Ingeniería InformáticaINFO 1126 - Programación 3

Descripción del Proyecto
Este proyecto implementa un sistema avanzado para la simulación y optimización de una red logística de drones autónomos, desarrollado como solución a la problemática propuesta por Correos Chile. La aplicación permite generar redes de transporte complejas, visualizar nodos y rutas sobre un mapa interactivo georreferenciado (Temuco), calcular trayectos óptimos considerando la autonomía de los drones y generar analíticas detalladas sobre el rendimiento de la red.
El sistema cuenta con una interfaz de usuario interactiva construida con Streamlit y una potente API RESTful desarrollada con FastAPI, permitiendo tanto la operación visual como la integración con servicios externos.
Características Principales

Visualización Geoespacial Interactiva: Mapa dinámico con Folium que muestra nodos (almacenes, estaciones de recarga, clientes), aristas y rutas calculadas en tiempo real.
Simulación de Rutas con Autonomía: Implementación del algoritmo de Dijkstra para encontrar la ruta más corta, con una lógica avanzada que fuerza paradas en estaciones de recarga si la autonomía del dron (50 unidades de costo) es superada en un tramo.
Análisis de Red: Visualización del Árbol de Expansión Mínima (MST) sobre el mapa usando el algoritmo de Kruskal para analizar la conectividad mínima de la red.
API RESTful Completa: Backend robusto con FastAPI que expone endpoints para gestionar y consultar clientes, órdenes, y obtener estadísticas y reportes de la simulación.
Reportes en PDF: Generación de informes detallados y profesionales bajo demanda, tanto desde la interfaz como desde la API, con resúmenes, tablas y gráficos.
Analítica de Datos Avanzada: Uso de un Árbol AVL para registrar la frecuencia de las rutas y ofrecer estadísticas sobre los nodos y clientes más visitados.

Guía de Instalación
Sigue estos pasos para configurar y ejecutar el proyecto en un entorno local.
1. Clonar el Repositorio
git clone https://github.com/HectorLep/Proyecto1-Progra3.git
cd Proyecto1-Progra3

2. Crear y Activar un Entorno Virtual
Es fundamental usar un entorno virtual para aislar las dependencias del proyecto.
Opción A (Usando venv - Estándar de Python):
# Crear el entorno
python3 -m venv venv

# Activar el entorno (en Linux/macOS)
source venv/bin/activate

Opción B (Usando conda - Recomendado para el equipo):
# Crear el entorno (puedes cambiar 'drones_env' por el nombre que prefieras)
conda create --name drones_env python=3.11

# Activar el entorno
conda activate drones_env

3. Instalar Dependencias
Una vez que el entorno virtual esté activado, instala todas las librerías necesarias ejecutando el siguiente comando:
pip install -r requirements.txt

(Asegúrate de tener un archivo requirements.txt en tu repositorio con todas las librerías necesarias).
Cómo Ejecutar la Aplicación
Con el entorno activado y las dependencias instaladas, ejecuta el siguiente comando desde la carpeta raíz del proyecto:
streamlit run app.py

Esto iniciará la aplicación completa, incluyendo tanto la interfaz de Streamlit como el servidor de la API en segundo plano.

La interfaz principal estará disponible en tu navegador en: http://localhost:8501
La documentación de la API estará disponible en: http://localhost:8001/docs

Autores

Hector: HectorLep
Maximiliano: Mxtsi7
Cristian: Insert-name-115
Agustin: sonickiller39
Jose: JJ3972433
