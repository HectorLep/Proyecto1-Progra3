from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

# Assuming domain.cliente.Client can be imported after sys.path modification in main.py
from domain.cliente import Client as DomainClient
from api.shared_simulation_state import get_simulation_data

router = APIRouter()

# Pydantic model for Client response
class ClientResponse(BaseModel):
    id: str
    name: str
    node_id: str
    type: str
    total_orders: int

    class Config:
        orm_mode = True # Allows mapping from ORM objects (like our DomainClient)

@router.get("/clients/", response_model=List[ClientResponse])
async def list_clients():
    """
    Retrieve a list of all clients from the current simulation.
    """
    sim_data = get_simulation_data()
    clients_domain_list = sim_data.get("clients", [])

    if not clients_domain_list:
        # Return empty list if no clients or no simulation data
        return []

    # Convert domain client objects to ClientResponse objects
    # FastAPI can often do this automatically if domain object attributes match Pydantic model
    # and orm_mode=True is set. Let's ensure it works or do manual conversion.
    response_clients = []
    for client_do in clients_domain_list:
        if isinstance(client_do, DomainClient): # Check if it's the expected type
             response_clients.append(ClientResponse.from_orm(client_do))
        # else: handle unexpected type or skip

    return response_clients

@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client_details(client_id: str):
    """
    Retrieve the details of a specific client by their ID.
    """
    sim_data = get_simulation_data()
    clients_domain_list = sim_data.get("clients", [])

    found_client = None
    for client_do in clients_domain_list:
        if isinstance(client_do, DomainClient) and client_do.id == client_id:
            found_client = client_do
            break

    if not found_client:
        raise HTTPException(status_code=404, detail=f"Client with ID '{client_id}' not found in current simulation.")

    return ClientResponse.from_orm(found_client)
