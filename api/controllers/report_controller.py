from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import io

from api.shared_simulation_state import get_simulation_data
# Assuming visual.report_generator can be imported after sys.path modification
from visual.report_generator import generate_pdf_report_content, get_report_filename

router = APIRouter()

@router.get("/reports/pdf")
async def get_pdf_report():
    """
    Generates and returns a complete simulation report in PDF format.
    """
    sim_data = get_simulation_data()

    if not sim_data.get("graph"): # Check if a simulation has been run
        raise HTTPException(status_code=404, detail="No active simulation data found to generate a report.")

    try:
        pdf_content_bytes = generate_pdf_report_content(sim_data)

        # Create a file-like object from bytes for StreamingResponse
        pdf_file_obj = io.BytesIO(pdf_content_bytes)

        report_filename = get_report_filename()

        return StreamingResponse(
            pdf_file_obj,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={report_filename}"}
        )
    except Exception as e:
        # Log the exception e
        print(f"Error generating PDF report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")
