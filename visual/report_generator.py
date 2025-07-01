import io
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors

# --- FUNCIONES AUXILIARES PARA GRÁFICOS Y TABLAS ---

def create_styled_table(data, col_widths=None):
    """Crea una tabla de ReportLab con estilos estandarizados."""
    table = Table(data, colWidths=col_widths)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2A5298')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F0F0F0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD')),
    ])
    table.setStyle(style)
    return table

def create_pie_chart(graph):
    """Genera un gráfico de torta de la distribución de nodos."""
    counts = {'warehouse': 0, 'recharge': 0, 'client': 0}
    for vertex in graph.vertices():
        v_type = vertex.type()
        if v_type in counts:
            counts[v_type] += 1
            
    labels = ['Almacén', 'Recarga', 'Cliente']
    sizes = [counts['warehouse'], counts['recharge'], counts['client']]
    
    final_labels = [label for i, label in enumerate(labels) if sizes[i] > 0]
    final_sizes = [size for size in sizes if size > 0]

    if not final_sizes: return None

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(final_sizes, labels=final_labels, autopct='%1.1f%%', startangle=90, colors=['#8B4513', '#FFA500', '#32CD32'])
    ax.axis('equal')
    plt.title("Distribución de Nodos por Tipo")

    return save_chart_to_buffer(fig)

def create_visits_bar_chart(data, title):
    """Genera un gráfico de barras para los nodos más visitados."""
    if not data: return None
    
    df = pd.DataFrame(data, columns=['Nodo', 'Visitas'])
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(df['Nodo'], df['Visitas'], color='#4ecdc4')
    ax.set_ylabel('Número de Visitas')
    ax.set_title(title, fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    return save_chart_to_buffer(fig)

def save_chart_to_buffer(fig):
    """Guarda una figura de Matplotlib en un buffer de memoria y la devuelve como Imagen de ReportLab."""
    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    plt.close(fig)
    return Image(img_buffer, width=6*inch, height=4*inch)


# --- FUNCIÓN PRINCIPAL DEL GENERADOR DE PDF ---

def generate_pdf_report_content(simulation_data: dict) -> bytes:
    """
    Genera un informe PDF con una estructura específica:
    1. Título
    2. Tabla de Clientes
    3. Lista de Órdenes
    4. Gráficos
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=inch, rightMargin=inch, topMargin=inch, bottomMargin=inch)
    story = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ReportTitle', fontSize=22, alignment=1, spaceAfter=0.5*inch, textColor=colors.HexColor('#1E3C72')))
    styles.add(ParagraphStyle(name='SectionTitle', fontSize=16, alignment=0, spaceBefore=0.3*inch, spaceAfter=0.2*inch, textColor=colors.HexColor('#2A5298')))
    styles.add(ParagraphStyle(name='OrderText', leftIndent=12, spaceAfter=6))

    # --- 1. TÍTULO ---
    story.append(Paragraph("Reporte de Simulación de Logística con  Drones", styles['ReportTitle']))


    # --- 2. TABLA DE CLIENTES ---
    story.append(Paragraph("Resumen de Clientes Registrados", styles['SectionTitle']))
    clients = simulation_data.get("clients", [])
    if clients:
        client_data = [["ID Cliente", "Nombre", "Tipo de Cliente", "Órdenes Totales"]] # <-- Cambia el encabezado
        for client in clients:
            client_data.append([
                client.id,
                client.name,
                client.type, # <-- CORREGIDO: ahora usa el tipo real del cliente
                str(client.total_orders)
            ])
        client_table = create_styled_table(client_data, col_widths=[1*inch, 2.5*inch, 1.5*inch, 1*inch])
        story.append(client_table)
    else:
        story.append(Paragraph("No se generaron clientes en esta simulación.", styles['Normal']))
    
    story.append(Spacer(1, 0.3 * inch))

    # --- 3. LISTA DE ÓRDENES ---
    story.append(Paragraph("Bitácora de Órdenes Procesadas", styles['SectionTitle']))
    orders = simulation_data.get("orders", [])
    if orders:
        for order in orders:
            status_color = "green" if order.status == "Entregado" else "red"
            order_text = (
                f"<b>Orden ID:</b> {order.order_id} | "
                f"<b>Cliente:</b> {order.client.id} | "
                f"<b>Ruta:</b> {order.origin} → {order.destination} | "
                f"<b>Estado:</b> <font color='{status_color}'>{order.status}</font>"
            )
            story.append(Paragraph(order_text, styles['OrderText']))
    else:
        story.append(Paragraph("No se procesaron órdenes en esta simulación.", styles['Normal']))

    # Salto de página para los gráficos
    story.append(PageBreak())

    # --- 4. GRÁFICOS ---
    story.append(Paragraph("Análisis Gráfico de la Simulación", styles['SectionTitle']))
    
    # Gráfico 1: Distribución de Nodos
    graph_obj = simulation_data.get("graph")
    if graph_obj:
        node_dist_chart = create_pie_chart(graph_obj)
        if node_dist_chart:
            story.append(node_dist_chart)
            story.append(Spacer(1, 0.2 * inch))

    # Gráficos 2, 3 y 4: Visitas a Nodos
    tracker = simulation_data.get("route_tracker")
    if tracker:
        node_visits = tracker.get_node_visit_stats()
        
        # Gráfico de Clientes más visitados
        client_visits = [d for d in node_visits if "N" in d[0]] # Asumiendo que los clientes tienen 'N' en su ID
        client_chart = create_visits_bar_chart(client_visits, "Nodos de Cliente Más Visitados")
        if client_chart:
            story.append(client_chart)
            story.append(Spacer(1, 0.2 * inch))

        # Gráfico de Estaciones de recarga más visitadas (Ejemplo, ajustar lógica de filtrado si es necesario)
        recharge_visits = [d for d in node_visits if "R" in d[0] or d[1] < 5] # Placeholder filter
        recharge_chart = create_visits_bar_chart(recharge_visits, "Nodos de Recarga Más Visitados")
        if recharge_chart:
            story.append(recharge_chart)
            story.append(Spacer(1, 0.2 * inch))
        
        # Gráfico de Almacenes más visitados (Ejemplo, ajustar lógica de filtrado si es necesario)
        storage_visits = [d for d in node_visits if "W" in d[0] or d[1] < 3] # Placeholder filter
        storage_chart = create_visits_bar_chart(storage_visits, "Nodos de Almacenamiento Más Visitados")
        if storage_chart:
            story.append(storage_chart)
    
    # --- Construir el PDF ---
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def get_report_filename():
    """Genera un nombre de archivo único para el reporte."""
    now = datetime.now()
    return f"Reporte_Drones_{now.strftime('%Y%m%d_%H%M%S')}.pdf"