from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import io
from api.shared_simulation_state import state_instance 
from visual.report_generator import generate_pdf_report_content, get_report_filename

router = APIRouter()

@router.get("/reports/pdf")
async def get_pdf_report():
    """
    Genera y retorna un reporte completo de la simulación en formato PDF.
    """
    sim_data = state_instance.get_data() 
    # Verificar si se ha ejecutado una simulación
    if not sim_data.get("graph"):
        raise HTTPException(status_code=404, detail="No hay datos de simulación activos para generar un reporte.")

    try:
        pdf_content_bytes = generate_pdf_report_content(sim_data)

        # Crear un objeto tipo archivo en memoria para la respuesta
        pdf_file_obj = io.BytesIO(pdf_content_bytes)

        report_filename = get_report_filename()

        return StreamingResponse(
            pdf_file_obj,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={report_filename}"}
        )
    except Exception as e:
        # Imprimir el error en la consola del servidor para depuración
        print(f"Error al generar el reporte PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Falló la generación del reporte PDF: {str(e)}")