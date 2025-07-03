from fastapi import APIRouter, HTTPException
from typing import List, Dict
from pydantic import BaseModel
from api.shared_simulation_state import state_instance 

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

def get_node_type(graph, node_id_str):
    if not graph: return "unknown"
    node_obj = graph.get_vertex_by_element(node_id_str)
    return node_obj.type() if node_obj else "unknown"

@router.get("/info/reports/visits/clients", response_model=List[VisitedNodeRank])
async def get_client_visit_ranking():
    """Recupera un ranking de los nodos de clientes más visitados."""
    sim_data = state_instance.get_data() # <-- USO CORREGIDO
    tracker = sim_data.get("route_tracker")
    graph = sim_data.get("graph")

    if not tracker or not graph:
        raise HTTPException(status_code=404, detail="Datos de simulación o rastreador de rutas no disponible.")

    node_visits = tracker.get_node_visit_stats(limit=None)
    client_visits = [
        VisitedNodeRank(node_id=node_id, type=get_node_type(graph, node_id), visits=count)
        for node_id, count in node_visits if get_node_type(graph, node_id) == 'client'
    ]
    return sorted(client_visits, key=lambda x: x.visits, reverse=True)

@router.get("/info/reports/visits/recharges", response_model=List[VisitedNodeRank])
async def get_recharge_visit_ranking():
    """Recupera un ranking de las estaciones de recarga más visitadas."""
    sim_data = state_instance.get_data() 
    tracker = sim_data.get("route_tracker")
    graph = sim_data.get("graph")

    if not tracker or not graph:
        raise HTTPException(status_code=404, detail="Datos de simulación o rastreador de rutas no disponible.")

    node_visits = tracker.get_node_visit_stats(limit=None)
    recharge_visits = [
        VisitedNodeRank(node_id=node_id, type=get_node_type(graph, node_id), visits=count)
        for node_id, count in node_visits if get_node_type(graph, node_id) == 'recharge'
    ]
    return sorted(recharge_visits, key=lambda x: x.visits, reverse=True)

@router.get("/info/reports/visits/storages", response_model=List[VisitedNodeRank])
async def get_storage_visit_ranking():
    """Recupera un ranking de los nodos de almacenamiento más visitados."""
    sim_data = state_instance.get_data() 
    tracker = sim_data.get("route_tracker")
    graph = sim_data.get("graph")

    if not tracker or not graph:
        raise HTTPException(status_code=404, detail="Datos de simulación o rastreador de rutas no disponible.")

    node_visits = tracker.get_node_visit_stats(limit=None)
    storage_visits = [
        VisitedNodeRank(node_id=node_id, type=get_node_type(graph, node_id), visits=count)
        for node_id, count in node_visits if get_node_type(graph, node_id) == 'warehouse'
    ]
    return sorted(storage_visits, key=lambda x: x.visits, reverse=True)

@router.get("/info/reports/summary", response_model=SimulationSummaryResponse)
async def get_general_summary():
    """Recupera un resumen general de la simulación activa."""
    sim_data = state_instance.get_data() 
    summary_text = sim_data.get("summary", "No hay resumen disponible.")
    graph = sim_data.get("graph")

    if not graph:
        raise HTTPException(status_code=409, detail="No active simulation found. Please run a simulation first.")

    type_dist = {v.type(): 0 for v in graph.vertices()}
    for v_obj in graph.vertices():
        type_dist[v_obj.type()] += 1
        
    return SimulationSummaryResponse(
        summary_text=summary_text,
        total_nodes=len(list(graph.vertices())),
        total_edges=len(list(graph.edges())),
        node_type_distribution=type_dist
    )