import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from queue import Queue, Empty
from threading import Thread
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse, JSONResponse
from llama_index.core.base.llms.types import MessageRole, ChatMessage
from pydantic import BaseModel

from app.utils.index import EventObject, get_agent, get_request_queue, _LLM_SEMAPHORE
from app.utils.json import json_to_model

chat_router = r = APIRouter()

logger = logging.getLogger("uvicorn")

# ThreadPoolExecutor untuk LLM query dengan timeout
_LLM_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="llm_worker")

# Timeout LLM dalam detik (sesuaikan dengan kecepatan hardware)
LLM_QUERY_TIMEOUT_SECS = 180   # 3 menit untuk model kecil di hardware terbatas


class _Message(BaseModel):
    role: MessageRole
    content: str


class _ChatData(BaseModel):
    messages: List[_Message]


def convert_sse(obj: str | dict) -> str:
    """Convert the given object (or string) to a Server-Sent Event (SSE) event."""
    return "data: {}\n\n".format(json.dumps(obj, ensure_ascii=False))


async def _wait_for_agent(timeout_secs: int = 300):
    """Tunggu sampai pre-warming agent selesai (maks timeout_secs detik)."""
    import app.utils.index as idx_module

    waited = 0
    while idx_module._GLOBAL_AGENT is None:
        if waited >= timeout_secs:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Server masih memuat data, silakan coba lagi dalam 1-2 menit.",
            )
        await asyncio.sleep(2)
        waited += 2
    return idx_module._GLOBAL_AGENT


@r.get("/health")
async def health_check():
    """Health check endpoint — memastikan backend siap menerima pertanyaan."""
    import app.utils.index as idx_module
    ready = idx_module._GLOBAL_AGENT is not None
    return JSONResponse(
        content={
            "status": "ready" if ready else "loading",
            "message": "Backend siap." if ready else "Backend sedang memuat data.",
        },
        status_code=200,
    )


@r.post("")
async def chat(
    request: Request,
    data: _ChatData = Depends(json_to_model(_ChatData)),
):
    # Tunggu agent siap (pre-warm mungkin masih berjalan)
    agent = await _wait_for_agent(timeout_secs=300)

    # Validasi input
    if len(data.messages) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )
    last_message = data.messages.pop()
    if last_message.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last message must be from user",
        )

    query_text = last_message.content
    logger.info(f"[CHAT] Menerima pertanyaan: '{query_text[:80]}'")

    # Buat queue baru yang di-attach ke handler global (thread-safe)
    queue = get_request_queue()

    # ── Jalankan LLM di thread terpisah ──────────────────────────────────────
    def run_agent():
        try:
            logger.info(f"[LLM] Mulai query: '{query_text[:60]}'")
            response = agent.query(query_text)
            answer = str(response).strip()
            if answer:
                # Bersihkan bintang dan emoji dari jawaban LLM
                answer = answer.replace("*", "")
                queue.put(answer)
            else:
                queue.put(
                    "Mohon maaf, data untuk pertanyaan tersebut belum tersedia. "
                    "Silakan hubungi BPS Lampung Selatan di (0727) 322241."
                )
            logger.info("[LLM] Query selesai.")
            queue.put(None)  # Sentinel: selesai
        except Exception as e:
            logger.error(f"[AGENT] Error saat query: {e}", exc_info=True)
            queue.put(
                "Mohon maaf, terjadi kendala saat memproses jawaban. "
                "Silakan coba lagi atau hubungi BPS Lampung Selatan di (0727) 322241."
            )
            queue.put(None)

    # ── Generator SSE ─────────────────────────────────────────────────────────
    async def event_generator():
        # Gunakan semaphore agar hanya 1 LLM call berjalan sekaligus
        async with _LLM_SEMAPHORE:
            thread = Thread(target=run_agent, daemon=True)
            thread.start()
            logger.info(f"[CHAT] Thread LLM dimulai untuk: '{query_text[:60]}'")

            loop = asyncio.get_event_loop()
            total_waited = 0
            max_wait = LLM_QUERY_TIMEOUT_SECS

            while total_waited < max_wait:
                try:
                    # Poll queue setiap 2 detik (tidak blocking event loop)
                    next_item = await loop.run_in_executor(
                        None, lambda: queue.get(timeout=2)
                    )
                except Empty:
                    total_waited += 2
                    # Kirim heartbeat agar koneksi tidak timeout di sisi client
                    yield ": heartbeat\n\n"
                    continue
                except Exception as e:
                    logger.error(f"[CHAT] Queue error: {e}")
                    yield convert_sse(
                        "Mohon maaf, terjadi gangguan. Silakan coba lagi."
                    )
                    break

                if next_item is None:
                    # Sentinel: LLM selesai
                    logger.info("[CHAT] Stream selesai.")
                    break
                elif isinstance(next_item, str):
                    yield convert_sse(next_item)
                    break  # Jawaban sudah lengkap, selesai
                elif isinstance(next_item, EventObject):
                    yield convert_sse(next_item.model_dump())
            else:
                # Timeout habis
                logger.warning(f"[CHAT] Timeout ({max_wait}s) untuk: '{query_text[:60]}'")
                yield convert_sse(
                    "Mohon maaf, sistem membutuhkan waktu lebih lama. "
                    "Silakan coba pertanyaan yang lebih spesifik, atau hubungi "
                    "BPS Lampung Selatan di (0727) 322241."
                )

            thread.join(timeout=5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")