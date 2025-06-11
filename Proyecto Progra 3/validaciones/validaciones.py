def validar_entradas_simulacion(num_nodos, num_aristas, num_ordenes, porc_almacenes, porc_recargas):
    """
    Valida las entradas para la simulación de logística de drones.
    Retorna tupla (es_valido, mensaje_error).
    """
    # Validar número de nodos
    if not isinstance(num_nodos, int) or num_nodos < 10 or num_nodos > 150:
        return False, "El número de nodos debe ser un entero entre 10 y 150."
    
    # Validar número de aristas
    max_aristas = num_nodos * (num_nodos - 1)  # Máximo de aristas en grafo dirigido
    if not isinstance(num_aristas, int) or num_aristas < 10 or num_aristas > max_aristas:
        return False, f"El número de aristas debe ser un entero entre 10 y {max_aristas}."
    
    # Validar número de órdenes
    if not isinstance(num_ordenes, int) or num_ordenes < 1 or num_ordenes > 500:
        return False, "El número de órdenes debe ser un entero entre 1 y 500."
    
    # Validar porcentajes
    if not (10 <= porc_almacenes <= 40 and 10 <= porc_recargas <= 40):
        return False, "Los porcentajes de almacenes y recargas deben estar entre 10% y 40%."
    
    if porc_almacenes + porc_recargas > 90:
        return False, "La suma de porcentajes de almacenes y recargas debe dejar al menos 10% para clientes."
    
    return True, ""

def validar_calculo_ruta(grafo, nodo_origen, nodo_destino):
    """
    Valida las entradas para el cálculo de rutas.
    Retorna tupla (es_valido, mensaje_error).
    """
    if not grafo:
        return False, "El grafo no está inicializado."
    
    todos_nodos = [v.element() for v in grafo.vertices()]
    if nodo_origen not in todos_nodos or nodo_destino not in todos_nodos:
        return False, "El nodo de origen o destino no existe en el grafo."
    
    # Verificar tipos de nodos
    nodo_origen_vertice = next(v for v in grafo.vertices() if v.element() == nodo_origen)
    nodo_destino_vertice = next(v for v in grafo.vertices() if v.element() == nodo_destino)
    if nodo_origen_vertice.type() != 'warehouse' or nodo_destino_vertice.type() != 'client':
        return False, "El origen debe ser un almacén y el destino un cliente."
    
    return True, ""