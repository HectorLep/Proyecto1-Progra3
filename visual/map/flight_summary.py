import streamlit as st

def display_route_details(route_details: dict):
    """
    Muestra los detalles de una ruta calculada en un formato limpio.
    """
    if not route_details:
        return

    st.subheader("Detalles de Ruta Calculada:")
    st.markdown(f"**Camino:** `{' -> '.join(route_details['path'])}`")
    st.markdown(f"**Costo Total:** `{route_details['cost']}`")
    if route_details['recharges']:
        st.markdown(f"**Estaciones de Recarga:** `{', '.join(route_details['recharges'])}`")