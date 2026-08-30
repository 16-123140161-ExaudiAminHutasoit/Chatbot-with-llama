"""
chart.py — FastAPI Router untuk generate diagram on-demand.
Endpoint: GET /api/chart/{chart_name}?style=bar|line|pie
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.utils.chart_generator import generate_chart, CHART_MAP

chart_router = APIRouter()


@chart_router.get("/{chart_name}")
def get_chart(chart_name: str, style: str = Query("bar", description="Style diagram: bar, line, pie")):
    """
    Generate dan kembalikan diagram statistik sebagai gambar PNG.

    Contoh:
        GET /api/chart/chart_kemiskinan?style=line
        GET /api/chart/chart_kemiskinan?style=bar
    """
    buf = generate_chart(chart_name, style=style)

    if buf is None:
        tersedia = list(CHART_MAP.keys())
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Diagram '{chart_name}' tidak ditemukan.",
                "diagram_tersedia": tersedia,
            },
        )

    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename={chart_name}_{style}.png"},
    )


@chart_router.get("/")
def list_charts():
    return {
        "total": len(CHART_MAP),
        "diagram_tersedia": list(CHART_MAP.keys()),
        "contoh_url": "/api/chart/chart_kemiskinan?style=line",
    }
