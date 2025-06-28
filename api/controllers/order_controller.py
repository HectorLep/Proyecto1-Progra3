from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from domain.orden import Order as DomainOrder
from domain.cliente import Client as DomainClient # Needed for Client basic info in Order
from api.shared_simulation_state import get_simulation_data, current_orders_list # current_orders_list for modification

router = APIRouter()

# Pydantic model for Client summary within Order
class OrderClientSummary(BaseModel):
    id: str
    name: str
    node_id: str

    class Config:
        orm_mode = True

# Pydantic model for Order response
class OrderResponse(BaseModel):
    order_id: str
    client: OrderClientSummary # Embed client summary
    origin: str
    destination: str
    weight: float
    priority: str
    status: str
    creation_date: datetime
    delivery_date: Optional[datetime] = None
    total_cost: float

    class Config:
        orm_mode = True

def map_domain_order_to_response(order_do: DomainOrder) -> OrderResponse:
    """Maps a DomainOrder object to an OrderResponse Pydantic model."""
    client_summary = OrderClientSummary.from_orm(order_do.client) if isinstance(order_do.client, DomainClient) else \
                     OrderClientSummary(id=str(order_do.client_id), name="N/A", node_id="N/A") # Fallback

    return OrderResponse(
        order_id=order_do.order_id,
        client=client_summary,
        origin=order_do.origin,
        destination=order_do.destination,
        weight=order_do.weight,
        priority=order_do.priority,
        status=order_do.status,
        creation_date=order_do.creation_date,
        delivery_date=order_do.delivery_date,
        total_cost=order_do.total_cost
    )

@router.get("/orders/", response_model=List[OrderResponse])
async def list_orders():
    """
    Retrieve a list of all orders from the current simulation.
    """
    sim_data = get_simulation_data()
    orders_domain_list = sim_data.get("orders", [])

    if not orders_domain_list:
        return []

    return [map_domain_order_to_response(order_do) for order_do in orders_domain_list if isinstance(order_do, DomainOrder)]

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order_details(order_id: str):
    """
    Retrieve the details of a specific order by its ID.
    """
    sim_data = get_simulation_data()
    orders_domain_list = sim_data.get("orders", [])

    found_order = None
    for order_do in orders_domain_list:
        if isinstance(order_do, DomainOrder) and order_do.order_id == order_id:
            found_order = order_do
            break

    if not found_order:
        raise HTTPException(status_code=404, detail=f"Order with ID '{order_id}' not found.")

    return map_domain_order_to_response(found_order)

@router.post("/orders/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(order_id: str):
    """
    Cancel a specific order. Sets its status to 'cancelled'.
    """
    # Note: current_orders_list is directly imported for modification.
    # This direct modification of shared state is simple but has concurrency implications
    # if the API and Streamlit app were truly concurrent multi-threaded/processed.
    # For this project's scope, it's assumed to be managed.

    found_order = None
    for order_do in current_orders_list: # Iterate through the modifiable list
        if isinstance(order_do, DomainOrder) and order_do.order_id == order_id:
            found_order = order_do
            break

    if not found_order:
        raise HTTPException(status_code=404, detail=f"Order with ID '{order_id}' not found.")

    if found_order.status not in ["pending", "processing"]: # Example: only cancel if not already delivered/failed
        raise HTTPException(status_code=400, detail=f"Order '{order_id}' cannot be cancelled. Status: {found_order.status}")

    found_order.status = "cancelled"
    # Potentially update other fields, e.g., log cancellation time
    # found_order.delivery_date = datetime.now() # Or a specific cancellation_date field

    # No need to call update_simulation_data explicitly if we are modifying the list in-place
    # and other parts of the system re-read this list.

    return map_domain_order_to_response(found_order)

@router.post("/orders/{order_id}/complete", response_model=OrderResponse)
async def complete_order(order_id: str):
    """
    Mark a specific order as completed. Sets its status to 'delivered'.
    (Simulates an external system marking completion, cost might be fixed or recalculated).
    """
    found_order = None
    for order_do in current_orders_list: # Iterate through the modifiable list
        if isinstance(order_do, DomainOrder) and order_do.order_id == order_id:
            found_order = order_do
            break

    if not found_order:
        raise HTTPException(status_code=404, detail=f"Order with ID '{order_id}' not found.")

    if found_order.status == "delivered":
        raise HTTPException(status_code=400, detail=f"Order '{order_id}' is already delivered.")
    if found_order.status == "cancelled":
        raise HTTPException(status_code=400, detail=f"Order '{order_id}' was cancelled.")

    # Use the existing mark_delivered method if it suits, or set status directly
    # found_order.mark_delivered(cost=found_order.total_cost if found_order.total_cost > 0 else 0) # Example
    found_order.status = "delivered"
    if not found_order.delivery_date:
        found_order.delivery_date = datetime.now()
    # If total_cost was not set by simulation, it might be 0.
    # The mark_delivered method in DomainOrder handles client order increment.

    return map_domain_order_to_response(found_order)
