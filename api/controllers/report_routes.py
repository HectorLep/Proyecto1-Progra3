from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import io
from api.shared_simulation_state import state_instance 
from visual.report_generator import generate_pdf_report_content, get_report_filename

router = APIRouter()

@router.get("/reports/pdf")
async def get_pdf_report():
    """
    Genera y retorna un reporte completo de la simulacion en formato PDF.
    """
    sim_data = state_instance.get_data() 
    if not sim_data.get("graph"):
        raise HTTPException(status_code=404, detail="No hay datos de simulacion activos para generar un reporte.")

    try:
        pdf_content_bytes = generate_pdf_report_content(sim_data)
        pdf_file_obj = io.BytesIO(pdf_content_bytes)
        report_filename = get_report_filename()

        return StreamingResponse(
            pdf_file_obj,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={report_filename}"}
        )
    except Exception as e:
        print(f"Error al generar el reporte PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Fallo la generacion del reporte PDF: {str(e)}")