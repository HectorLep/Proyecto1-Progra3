from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

from api.shared_simulation_state import get_simulation_data
# Assuming sim.rutas.RouteTracker and model.graph.Graph are available
# from sim.rutas import RouteTracker
# from model.graph import Graph

router = APIRouter()

class VisitedNodeRank(BaseModel):
    node_id: str
    type: str
    visits: int

class SimulationSummaryResponse(BaseModel):
    summary_text: str
    total_nodes: int = 0
    total_edges: int = 0
    node_type_distribution: Dict[str, int] = {}
    # Add more fields as needed

def get_node_type(graph, node_id_str):
    if not graph: return "unknown"
    node_obj = graph.get_vertex_by_element(node_id_str)
    return node_obj.type() if node_obj else "unknown"

@router.get("/info/reports/visits/clients", response_model=List[VisitedNodeRank])
async def get_client_visit_ranking():
    """
    Retrieves a ranking of the most visited client nodes.
    """
    sim_data = get_simulation_data()
    tracker = sim_data.get("route_tracker")
    graph = sim_data.get("graph")

    if not tracker or not graph:
        raise HTTPException(status_code=404, detail="Simulation data or route tracker not available.")

    node_visits = tracker.get_node_visit_stats(limit=None) # Get all node visits

    client_visits = []
    for node_id, visits_count in node_visits:
        node_type = get_node_type(graph, node_id)
        if node_type == 'client':
            client_visits.append(VisitedNodeRank(node_id=node_id, type=node_type, visits=visits_count))

    return sorted(client_visits, key=lambda x: x.visits, reverse=True)


@router.get("/info/reports/visits/recharges", response_model=List[VisitedNodeRank])
async def get_recharge_visit_ranking():
    """
    Retrieves a ranking of the most visited recharge station nodes.
    """
    sim_data = get_simulation_data()
    tracker = sim_data.get("route_tracker")
    graph = sim_data.get("graph")

    if not tracker or not graph:
        raise HTTPException(status_code=404, detail="Simulation data or route tracker not available.")

    node_visits = tracker.get_node_visit_stats(limit=None)

    recharge_visits = []
    for node_id, visits_count in node_visits:
        node_type = get_node_type(graph, node_id)
        if node_type == 'recharge':
            recharge_visits.append(VisitedNodeRank(node_id=node_id, type=node_type, visits=visits_count))

    return sorted(recharge_visits, key=lambda x: x.visits, reverse=True)

@router.get("/info/reports/visits/storages", response_model=List[VisitedNodeRank])
async def get_storage_visit_ranking():
    """
    Retrieves a ranking of the most visited storage (warehouse) nodes.
    """
    sim_data = get_simulation_data()
    tracker = sim_data.get("route_tracker")
    graph = sim_data.get("graph")

    if not tracker or not graph:
        raise HTTPException(status_code=404, detail="Simulation data or route tracker not available.")

    node_visits = tracker.get_node_visit_stats(limit=None)

    storage_visits = []
    for node_id, visits_count in node_visits:
        node_type = get_node_type(graph, node_id)
        if node_type == 'warehouse': # Note: Vertex type is 'warehouse'
            storage_visits.append(VisitedNodeRank(node_id=node_id, type=node_type, visits=visits_count))

    return sorted(storage_visits, key=lambda x: x.visits, reverse=True)


@router.get("/info/reports/summary", response_model=SimulationSummaryResponse)
async def get_general_summary():
    """
    Retrieves a general summary of the active simulation.
    """
    sim_data = get_simulation_data()
    summary_text = sim_data.get("summary", "No summary available.")
    graph = sim_data.get("graph")

    response_data = {"summary_text": summary_text}

    if graph:
        response_data["total_nodes"] = len(list(graph.vertices()))
        response_data["total_edges"] = len(list(graph.edges())) # This might be double for undirected if not careful

        type_dist = {}
        for v_obj in graph.vertices():
            v_type = v_obj.type()
            type_dist[v_type] = type_dist.get(v_type, 0) + 1
        response_data["node_type_distribution"] = type_dist

    return SimulationSummaryResponse(**response_data)
