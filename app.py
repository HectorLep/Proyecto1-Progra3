# Contenido FINAL y COMPLETO para el archivo app.py (en la carpeta raíz)

import streamlit as st
import sys
import os
import threading
import uvicorn

# --- Configuración de la página (esto debe estar al principio) ---
st.set_page_config(
    page_title="🚁 Drone Logistics Simulator - Correos Chile",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Añadir la raíz del proyecto al path de Python ---
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# --- Importar los componentes de la app DESPUÉS de configurar el path ---
from visual.dashboard import main as main_dashboard
from api.main import app as fastapi_app

# --- Función para ejecutar la API de FastAPI en un hilo separado ---
def run_fastapi():
    """Ejecuta la aplicación FastAPI usando uvicorn en el puerto 8001."""
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8001, log_level="info")

# --- Lógica principal ---
if __name__ == "__main__":
    
    # Verificar si el hilo de la API ya está corriendo para evitar duplicados
    if 'fastapi_thread_started' not in st.session_state:
        # Iniciar la API en un hilo de fondo (background thread)
        # daemon=True asegura que el hilo se cierre cuando la app de Streamlit se detenga
        print("INFO: Iniciando el hilo de la API de FastAPI en segundo plano...")
        fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
        fastapi_thread.start()
        st.session_state['fastapi_thread_started'] = True
        print("INFO: Hilo de la API iniciado.")

    # Ejecutar la función principal del dashboard de Streamlit
    print("INFO: Iniciando el dashboard de Streamlit...")
    main_dashboard()