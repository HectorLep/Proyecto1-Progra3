from fastapi import FastAPI
import uvicorn
import sys
import os

# Add project root to sys.path to allow imports from domain, model, etc.
# This is a common pattern for running FastAPI apps when the app is not at the project root.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Import routers after sys.path is configured
from api.controllers import client_controller, order_controller, report_controller, info_controller

app = FastAPI(
    title="Drone Logistics API",
    description="API for interacting with the Drone Logistics Simulation data.",
    version="1.0.0"
)

# Include routers from controller modules
app.include_router(client_controller.router, prefix="/api", tags=["Clients"])
app.include_router(order_controller.router, prefix="/api", tags=["Orders"])
app.include_router(report_controller.router, prefix="/api", tags=["Reports"]) # For PDF report
app.include_router(info_controller.router, prefix="/api", tags=["Info & Analytics"]) # For other info endpoints

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Drone Logistics API. See /docs for details."}

# Note: To run this FastAPI app, you would typically use:
# uvicorn api.main:app --reload --port 8000
# The main streamlit app (app.py) will run the simulation and update shared state.
# This FastAPI app will run as a separate process if uvicorn is used directly.
# For them to share memory using globals like in shared_simulation_state.py,
# FastAPI would ideally be run in the same process/thread as Streamlit,
# or a more robust IPC/shared database mechanism would be needed.

# For the purpose of this project, if Streamlit calls FastAPI endpoints hosted by itself (same process),
# then shared_simulation_state can work. If they are separate processes, it won't.
# The prompt implies the API exposes data of the "active simulation", suggesting a link.
# Let's assume for now that Streamlit will somehow make this data available,
# or we adjust how data is shared later. The controllers will use shared_simulation_state.

if __name__ == "__main__":
    # This is for running the FastAPI app directly for testing, not for combined run.
    # When running with Streamlit, Streamlit will be the main entry point.
    # The `app.py` in the root will need to be modified to also run this FastAPI app,
    # possibly using threading or by having Streamlit make HTTP requests to this app if run separately.
    # For now, let's make it runnable for API testing.
    print(f"PROJECT_ROOT for FastAPI: {PROJECT_ROOT}")
    print(f"sys.path for FastAPI: {sys.path}")
    uvicorn.run(app, host="0.0.0.0", port=8001) # Use a different port, e.g. 8001
                                                # if Streamlit uses 8501 (default)
                                                # and if we run them separately.
                                                # If integrated, port management is different.

# To integrate with Streamlit app.py, one approach is to run FastAPI in a separate thread
# from within the Streamlit application. Or, Streamlit calls these endpoints if run separately.
# Given the structure, the controllers will try to access shared_simulation_state.
# The `update_simulation_data` function in `shared_simulation_state` needs to be called by `visual/dashboard.py`
# after `ejecutar_simulacion`.
# And `app.py` (root) needs to be the main entry point that can serve both.
# This means `app.py` might need to launch FastAPI app using uvicorn programmatically or similar.
# For now, the API files are structured. The integration with Streamlit's execution flow is key.
# The controllers will assume `shared_simulation_state` is populated.

# A simple way to make FastAPI part of Streamlit app is to mount it.
# However, Streamlit usually runs its own server.
# The simplest path for this task is to have Streamlit update shared_simulation_state,
# and FastAPI (if run in the same process, e.g. using custom threading in app.py) reads it.
# Or, if API is separate, Streamlit would need to POST data to a special API endpoint to update state.
# Let's stick to shared_simulation_state for now and address integration in app.py later.
