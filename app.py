import streamlit as st
import sys
import os
import threading
import uvicorn

st.set_page_config(
    page_title="🚁 Drone Logistics Simulator - Correos Chile",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from visual.dashboard import main as main_dashboard
from api.main import app as fastapi_app

def run_fastapi():
    """Ejecuta la aplicación FastAPI usando uvicorn en el puerto 8001."""
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8001, log_level="info")

if __name__ == "__main__":
    
    if 'fastapi_thread_started' not in st.session_state:
        print("INFO: Iniciando el hilo de la API de FastAPI en segundo plano...")
        fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
        fastapi_thread.start()
        st.session_state['fastapi_thread_started'] = True
        print("INFO: Hilo de la API iniciado.")

    print("INFO: Iniciando el dashboard de Streamlit...")
    main_dashboard()