import asyncio
import logging
import os
import uvicorn
from contextlib import asynccontextmanager

from app.api.routers.chat import chat_router
from app.api.routers.chart import chart_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm the chat agent in a background thread on startup."""
    import threading

    def _prewarm_thread():
        """Jalankan ingest di thread terpisah dengan event loop sendiri."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            logger.info("Memulai pre-warming agent (ingest + vector index)...")
            from app.utils.index import get_agent
            loop.run_until_complete(get_agent())
            logger.info("Agent siap! Backend sudah bisa menerima pertanyaan.")
        except Exception as e:
            logger.error(f"Pre-warm gagal: {e}", exc_info=True)
        finally:
            loop.close()

    # Jalankan pre-warming di OS thread terpisah — tidak memblokir event loop utama
    t = threading.Thread(target=_prewarm_thread, daemon=True)
    t.start()

    yield  # Server berjalan normal, terima request


app = FastAPI(lifespan=lifespan)

environment = os.getenv("ENVIRONMENT", "dev")

if environment == "dev":
    logger.warning("Running in development mode - allowing CORS for all origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(chat_router,  prefix="/api/chat")
app.include_router(chart_router, prefix="/api/chart")


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8001, reload=False)
