
# 🚁 Simulador de Logística con Drones - Fase 2

### Universidad Católica de Temuco

**Facultad de Ingeniería - Departamento de Ingeniería Informática**\<br\>
**INFO 1126 - Programación 3**

-----

## Descripción del Proyecto

Sistema de simulación para una red logística de drones autónomos. La aplicación cuenta con una interfaz interactiva (Streamlit) para visualizar la red en un mapa, calcular rutas óptimas con restricciones de autonomía (Dijkstra, Kruskal) y analizar datos. Incluye una API RESTful (FastAPI) para la integración con servicios externos y la generación de reportes en PDF.

## Características Principales

  * **Visualización Geoespacial Interactiva:** Mapa dinámico con Folium que muestra nodos, aristas y rutas calculadas en tiempo real.
  * **Simulación de Rutas con Autonomía:** Implementación del algoritmo de Dijkstra para encontrar la ruta más corta, con una lógica avanzada que fuerza paradas en estaciones de recarga.
  * **Análisis de Red:** Visualización del Árbol de Expansión Mínima (MST) sobre el mapa usando el algoritmo de Kruskal.
  * **API RESTful Completa:** Backend robusto con FastAPI que expone endpoints para gestionar y consultar los datos de la simulación.
  * **Reportes en PDF:** Generación de informes detallados y profesionales bajo demanda desde la interfaz y la API.
  * **Analítica de Datos Avanzada:** Uso de un Árbol AVL para registrar la frecuencia de las rutas y ofrecer estadísticas detalladas.

-----

## Guía de Instalación

Sigue estos pasos para configurar y ejecutar el proyecto en un entorno local.

### 1\. Clonar el Repositorio

```bash
git clone https://github.com/HectorLep/Proyecto1-Progra3.git
cd Proyecto1-Progra3
```

### 2\. Crear y Activar un Entorno Virtual

Es fundamental usar un entorno virtual para aislar las dependencias del proyecto.

**Opción A (Usando `venv` - Estándar de Python):**

```bash
# Crear el entorno
python3 -m venv venv

# Activar el entorno (en Linux/macOS)
source venv/bin/activate
```

**Opción B (Usando `conda` - Recomendado para el equipo):**

```bash
# Crear el entorno
conda create --name drones_env python=3.11

# Activar el entorno
conda activate drones_env
```

### 3\. Instalar Dependencias

Una vez que el entorno virtual esté activado, instala todas las librerías necesarias:

```bash
pip install -r requirements.txt
```

*(Asegúrate de tener un archivo `requirements.txt` en tu repositorio).*

-----

## Cómo Ejecutar la Aplicación

Con el entorno activado y las dependencias instaladas, ejecuta el siguiente comando desde la carpeta raíz del proyecto:

```bash
streamlit run app.py
```

Esto iniciará la aplicación completa, incluyendo tanto la interfaz de Streamlit como el servidor de la API en segundo plano.

  * **Interfaz Principal:** `http://localhost:8501`
  * **Documentación de la API:** `http://localhost:8001/docs`

-----

## Autores

  * **Hector:** [@HectorLep](https://github.com/HectorLep)
  * **Maximiliano:** [@Mxtsi7](https://github.com/Mxtsi7)
  * **Cristian:** [@Insert-name-115](https://github.com/Insert-name-115)
  * **Agustin:** [@sonickiller39](https://github.com/sonickiller39)
  * **Jose:** [@JJ3972433](https://github.com/JJ3972433)
