import streamlit as st

st.set_page_config(page_title="🚁 Drone Logistics Simulator - Correos Chile", layout="wide")

# Sidebar setup
with st.sidebar:
    st.header("⚙️ Simulation Parameters")
    st.slider("Number of Nodes", 10, 150, 15)
    st.slider("Number of Edges", 10, 300, 28)
    st.slider("Number of Orders", 10, 500, 10)
    st.button("Start Simulation")

# Tabs setup
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Run Simulation", "Explore Network", "Clients & Orders", "Route Analytics", "General Statistics"])

with tab1:
    st.header("Run Simulation")
    st.text("Start the simulation by selecting parameters from the sidebar.")

with tab2:
    st.header("Explore Network")
    st.text("Visualize the drone network here.")

with tab3:
    st.header("Clients & Orders")
    st.text("Manage and view clients and their orders.")

with tab4:
    st.header("Route Analytics")
    st.text("Analyze and visualize route usage.")

with tab5:
    st.header("General Statistics")
    st.text("View global system statistics.")
