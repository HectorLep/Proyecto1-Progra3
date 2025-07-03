from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from api.shared_simulation_state import state_instance

router = APIRouter()

class ClientResponse(BaseModel):
    id: str; name: str; node_id: str; type: str; total_orders: int
    class Config: from_attributes = True

@router.get("/clients/", response_model=List[ClientResponse])
async def list_clients():
    """Recupera una lista de todos los clientes de la simulación actual."""
    sim_data = state_instance.get_data()
    if not sim_data.get("graph"):
        raise HTTPException(status_code=409, detail="No active simulation found. Please run a simulation first.")
        
    clients_list = sim_data.get("clients", [])
    return clients_list

@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client_details(client_id: str):
    """Recupera los detalles de un cliente específico por su ID."""
    sim_data = state_instance.get_data()
    if not sim_data.get("graph"):
        raise HTTPException(status_code=409, detail="No active simulation found. Please run a simulation first.")
        
    clients_list = sim_data.get("clients", [])
    found_client = next((client for client in clients_list if client.id == client_id), None)
    if not found_client:
        raise HTTPException(status_code=404, detail=f"Client with ID '{client_id}' not found.")
    return found_client