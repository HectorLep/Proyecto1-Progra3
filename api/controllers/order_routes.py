from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from domain.orden import Order as DomainOrder
from domain.cliente import Client as DomainClient
from api.shared_simulation_state import state_instance 

router = APIRouter()

class OrderClientSummary(BaseModel):
    id: str
    name: str
    node_id: str

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    order_id: str
    client: OrderClientSummary
    origin: str
    destination: str
    weight: float
    priority: str
    status: str
    creation_date: datetime
    delivery_date: Optional[datetime] = None
    total_cost: float

    class Config:
        from_attributes = True 

def map_domain_order_to_response(order_do: DomainOrder) -> OrderResponse:
    """Mapea un objeto de dominio Order a un modelo de respuesta Pydantic."""
    return OrderResponse.model_validate(order_do)

@router.get("/orders/", response_model=List[OrderResponse])
async def list_orders():
    """Recupera una lista de todas las órdenes de la simulación actual."""
    sim_data = state_instance.get_data()
    if not sim_data.get("graph"):
        raise HTTPException(status_code=409, detail="No active simulation found. Please run a simulation first.")
    
    orders_domain_list = sim_data.get("orders", [])
    return [map_domain_order_to_response(order) for order in orders_domain_list]

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order_details(order_id: str):
    """Recupera los detalles de una orden específica por su ID."""
    sim_data = state_instance.get_data()
    if not sim_data.get("graph"):
        raise HTTPException(status_code=409, detail="No active simulation found. Please run a simulation first.")

    orders_domain_list = sim_data.get("orders", [])
    found_order = next((order for order in orders_domain_list if order.order_id == order_id), None)
    if not found_order:
        raise HTTPException(status_code=404, detail=f"Order with ID '{order_id}' not found.")
    return map_domain_order_to_response(found_order)

@router.post("/orders/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(order_id: str):
    """Cancela una orden específica."""
    sim_data = state_instance.get_data()
    if not sim_data.get("graph"):
        raise HTTPException(status_code=409, detail="No active simulation found. Please run a simulation first.")
        
    orders_domain_list = sim_data.get("orders", [])
    found_order = next((order for order in orders_domain_list if order.order_id == order_id), None)

    if not found_order:
        raise HTTPException(status_code=404, detail=f"Order with ID '{order_id}' not found.")

    if found_order.status not in ["pending", "processing", "Normal"]:
        raise HTTPException(status_code=400, detail=f"Order '{order_id}' cannot be cancelled. Status: {found_order.status}")

    found_order.status = "cancelled"

    return map_domain_order_to_response(found_order)

@router.post("/orders/{order_id}/complete", response_model=OrderResponse)
async def complete_order(order_id: str):
    """Marca una orden específica como completada."""
    sim_data = state_instance.get_data()
    if not sim_data.get("graph"):
        raise HTTPException(status_code=409, detail="No active simulation found. Please run a simulation first.")
        
    orders_domain_list = sim_data.get("orders", [])
    found_order = next((order for order in orders_domain_list if order.order_id == order_id), None)

    if not found_order:
        raise HTTPException(status_code=404, detail=f"Order with ID '{order_id}' not found.")

    if found_order.status == "Entregado":
        raise HTTPException(status_code=400, detail=f"Order '{order_id}' is already delivered.")
    
    if found_order.status == "cancelled":
        raise HTTPException(status_code=400, detail=f"Cannot complete an order that was cancelled.")

    found_order.status = "Entregado"
    if not found_order.delivery_date:
        found_order.delivery_date = datetime.now()

    return map_domain_order_to_response(found_order)