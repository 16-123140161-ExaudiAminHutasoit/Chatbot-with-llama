import asyncio
import logging
import os
import shutil
import threading
from queue import Queue
from typing import Optional, Dict, Any, List

from pydantic import BaseModel

from llama_index.core import VectorStoreIndex
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.readers.file import FlatReader
from llama_index.core.callbacks import CallbackManager
from llama_index.core.callbacks.base_handler import BaseCallbackHandler
from llama_index.core.callbacks.schema import CBEventType, EventPayload
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.schema import TextNode, NodeWithScore
from llama_index.core.settings import Settings
from llama_index.core.indices import load_index_from_storage
from llama_index.core.storage import StorageContext
from llama_index.core.storage.docstore.types import BaseDocumentStore

from app.utils.node_parsers.markdown import CustomMarkdownNodeParser
from app.utils.transformations import URLExtractor, Deduplicator, Upserter
from app.utils.transformations import HyperlinksRemover, DocsSummarizer
from app.utils.misc import get_max_h_value


# ─── Konstanta direktori ────────────────────────────────────────────────────
PIPELINE_STORAGE_DIR = "./pipeline_storage"
STORAGE_DIR = "./storage"
DATA_DIR = "./data"

# ─── Semaphore: batasi 1 LLM call sekaligus (mencegah crash saat stress test) ─
_LLM_SEMAPHORE = asyncio.Semaphore(1)

# ─── Lock untuk proteksi set_queue saat multi-thread ────────────────────────
_QUEUE_LOCK = threading.Lock()


class EventObject(BaseModel):
    """
    Represents an event from the LlamaIndex callback handler.

    Attributes:
        type (str): The type of the event, e.g. "function_call".
        payload (dict): The payload associated with the event.
    """
    type: str
    payload: dict


class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler untuk stream token ke queue per-request."""

    def __init__(self, queue: Queue) -> None:
        super().__init__([], [])
        self._queue = queue

    def set_queue(self, queue: Queue) -> None:
        with _QUEUE_LOCK:
            self._queue = queue

    @property
    def queue(self) -> Queue:
        return self._queue

    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        parent_id: str = "",
        **kwargs: Any,
    ) -> str:
        """Run when an event starts and return id of event."""
        if event_type == CBEventType.FUNCTION_CALL:
            if payload is not None:
                func_call = payload.get("function_call", "")
                tool_obj = payload.get("tool")
                tool_name = getattr(tool_obj, "name", str(tool_obj)) if tool_obj else "tool"
                self._queue.put(
                    EventObject(
                        type="function_call",
                        payload={
                            "arguments_str": str(func_call),
                            "tool_str": tool_name,
                        },
                    )
                )

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        """Run when an event ends."""
        if event_type == CBEventType.AGENT_STEP:
            if payload is not None and "response" in payload:
                self._queue.put(payload["response"])
        elif event_type == CBEventType.RETRIEVE:
            if payload is None or EventPayload.NODES not in payload:
                return
            nodes_with_scores: list[NodeWithScore] = payload[EventPayload.NODES]
            nodes_to_return = []
            for node_with_score in nodes_with_scores:
                node = node_with_score.node
                node_meta = node.metadata
                if "section_link" in node_meta:
                    nodes_to_return.append({
                        "id": node.id_,
                        "title": get_max_h_value(node_meta) or node_meta.get("file_path", ""),
                        "url": node_meta.get("file_path", ""),
                        "section": node_meta.get("section_link", ""),
                        "summary": node_meta.get("summary", node.get_content()[:150] + "..."),
                    })
            self._queue.put(
                EventObject(
                    type="nodes_retrieved",
                    payload={"nodes": nodes_to_return},
                )
            )

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        pass

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        pass


# ─── Fungsi utilitas ─────────────────────────────────────────────────────────

def clean_old_persisted_indices(doc_id: str) -> None:
    """Hapus direktori storage lama saat dokumen diperbarui."""
    if os.path.exists(STORAGE_DIR):
        print(f"[CLEAN] Menghapus vector index lama: {STORAGE_DIR}")
        shutil.rmtree(STORAGE_DIR, ignore_errors=True)


async def ingest(directory: str, docstore: BaseDocumentStore) -> list:
    """Baca, deduplikasi, dan simpan dokumen ke docstore."""
    reader = SimpleDirectoryReader(
        input_dir=directory,
        recursive=True,
        required_exts=[".md", ".mdx"],
        file_extractor={
            ".md": FlatReader(),
            ".mdx": FlatReader(),
        },
    )
    docs = reader.load_data()

    deduplicator = Deduplicator(
        cleanup_fn=clean_old_persisted_indices,
        docstore=docstore,
    )
    url_extractor = URLExtractor(data_path=DATA_DIR)
    hyperlinks_remover = HyperlinksRemover()
    upserter = Upserter(
        docstore=docstore,
        persist_dir=PIPELINE_STORAGE_DIR,
    )

    pipeline = IngestionPipeline(
        transformations=[
            deduplicator,
            hyperlinks_remover,
            url_extractor,
            upserter,
        ],
    )

    try:
        if os.path.exists(PIPELINE_STORAGE_DIR):
            pipeline.load(PIPELINE_STORAGE_DIR)
        nodes = await pipeline.arun(documents=docs)
    except Exception as e:
        print(f"[INGEST] Cache pipeline perlu diperbarui ({e}). Menghapus cache lama...")
        for d in [PIPELINE_STORAGE_DIR, STORAGE_DIR]:
            if os.path.exists(d):
                shutil.rmtree(d, ignore_errors=True)
        pipeline = IngestionPipeline(
            transformations=[
                deduplicator,
                hyperlinks_remover,
                url_extractor,
                upserter,
            ],
        )
        nodes = await pipeline.arun(documents=docs)

    pipeline.persist(PIPELINE_STORAGE_DIR)
    print(f"[INGEST] New/updated nodes: {len(nodes)}")

    if len(nodes) > 0:
        docstore.add_documents(nodes)
        docstore.persist(
            persist_path=os.path.join(PIPELINE_STORAGE_DIR, "docstore.json")
        )

    # Kembalikan semua dokumen dari docstore
    result_docs = []
    for doc_id in docstore.get_all_document_hashes().values():
        try:
            doc = docstore.get_document(doc_id=doc_id)
            if doc:
                result_docs.append(doc)
        except Exception:
            continue
    return result_docs if result_docs else docs


def _build_bps_query_engine(
    storage_dir: str,
    docs: list,
    callback_manager: CallbackManager,
):
    """Build query engine stateless untuk BPS FAQ.
    
    Menggunakan query_engine alih-alih chat_engine agar setiap pertanyaan
    diproses secara independen tanpa kontaminasi riwayat percakapan,
    sehingga retrieval selalu akurat sesuai pertanyaan yang diajukan.
    """
    node_parser = CustomMarkdownNodeParser()

    llm = Ollama(
        model="qwen2.5:1.5b",
        temperature=0.1,
        request_timeout=300.0,
        context_window=4096,
    )
    # FastEmbedEmbedding: ONNX lokal, jauh lebih cepat dari Ollama embedding
    embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")

    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.callback_manager = callback_manager

    from llama_index.core.prompts import PromptTemplate

    # ── QA Prompt: instruksi langsung tanpa condense (stateless) ─────────
    qa_prompt_tmpl = (
        "Informasi resmi BPS Kabupaten Lampung Selatan:\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Berdasarkan data di atas, jawab pertanyaan berikut secara akurat dan lengkap dalam Bahasa Indonesia.\n\n"
        "ATURAN WAJIB:\n"
        "1. DILARANG KERAS menjawab dalam Bahasa Inggris. Seluruh jawaban WAJIB 100% Bahasa Indonesia.\n"
        "2. Jangan pernah gunakan frasa bahasa Inggris seperti 'I'm sorry', 'I can't', 'misunderstanding'.\n"
        "3. Jika data tersedia di konteks di atas, WAJIB tampilkan data tersebut secara lengkap dan presisi.\n"
        "4. DILARANG KERAS menghalusinasikan angka 0% atau menebak angka jika angka persen untuk tahun yang diminta tidak tertulis di konteks.\n"
        "5. Jika data TIDAK tersedia di konteks, jawab: 'Mohon maaf, data untuk tahun tersebut belum tersedia. "
        "Silakan hubungi kantor BPS Lampung Selatan di (0727) 322241 atau bps1803@bps.go.id.'\n"
        "6. PEMBEDAAN INDIKATOR:\n"
        "   - 'Laju Pertumbuhan Ekonomi / PDRB': tampilkan angka PERSEN (%) pertumbuhan (contoh: 2018 = 5,23%). Jangan jawab 0%!\n"
        "   - 'Jumlah Penduduk Miskin': tampilkan angka RIBU JIWA saja (contoh: 2024 = 132,38 Ribu Jiwa).\n"
        "   - 'Persentase / Tingkat Kemiskinan': tampilkan PERSEN % saja (contoh: 2024 = 12,57%).\n"
        "   - 'Garis Kemiskinan': tampilkan angka RUPIAH per kapita per bulan.\n"
        "   - 'Indeks Kedalaman Kemiskinan P1': tampilkan nilai P1 saja.\n"
        "   - 'Indeks Keparahan Kemiskinan P2': tampilkan nilai P2 saja.\n"
        "7. Tampilkan SEMUA data tahun yang tersedia jika diminta rincian lengkap.\n"
        "8. Kontak BPS: Jl. Mustafa Kemal No. 24 Kalianda | Telp (0727) 322241 | bps1803@bps.go.id | WA +62 858-1911-1803\n"
        "9. Mulai jawaban LANGSUNG dengan data/informasi. Jangan diawali 'Halo', 'Tentu', 'Baik', atau basa-basi.\n"
        "10. JANGAN gunakan simbol bintang (*). Gunakan tanda hubung (-) untuk daftar poin.\n"
        "11. JANGAN PERNAH mencocokkan atau menggunakan angka dari tahun lain jika tahun yang diminta tidak tercantum di teks. Katakan data tahun tersebut belum tersedia di publikasi ini.\n"
        "12. DILARANG KERAS menyebutkan atau mencantumkan 'Penanggung Jawab Data' atau nama petugas BPS dalam jawaban. Hanya tampilkan datanya saja.\n"
        "13. DILARANG KERAS menambahkan kalimat 'Mohon maaf...' jika data statistik sudah berhasil ditampilkan di atas.\n"
        "14. Jika terdapat URL/Tautan Akses Resmi BPS pada teks konteks di atas, WAJIB sertakan link URL tersebut di akhir jawaban sebagai referensi resmi.\n"
        "15. Akhiri jawaban dengan satu kalimat penutup singkat yang ramah.\n\n"
        "Pertanyaan: {query_str}\n"
        "Jawaban:"
    )
    qa_prompt = PromptTemplate(qa_prompt_tmpl)

    # ── Load dari cache atau buat index baru ──────────────────────────────
    index_cached = (
        os.path.exists(storage_dir)
        and os.path.exists(os.path.join(storage_dir, "docstore.json"))
    )

    if index_cached:
        print(f"[INDEX] Memuat vector index dari cache: {storage_dir}")
        storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
        vector_index = load_index_from_storage(
            storage_context, callback_manager=callback_manager
        )
    else:
        print(f"[INDEX] Membuat vector index baru (embedding {len(docs)} dokumen)...")
        all_nodes = []
        for doc in docs:
            nodes = node_parser.get_nodes_from_documents([doc])
            all_nodes.extend(nodes)
        print(f"[INDEX] Total nodes: {len(all_nodes)}")
        vector_index = VectorStoreIndex(
            all_nodes,
            callback_manager=callback_manager,
            show_progress=True,
        )
        vector_index.storage_context.persist(persist_dir=storage_dir)
        print(f"[INDEX] Vector index berhasil disimpan ke {storage_dir}")

    # ── Query Engine: stateless, setiap pertanyaan retrieval independen ───
    query_engine = vector_index.as_query_engine(
        similarity_top_k=8,          # ambil 8 node paling relevan
        text_qa_template=qa_prompt,
        streaming=False,             # streaming=False agar query() langsung mengembalikan teks jawaban (3-5 detik)
        verbose=True,
    )

    return query_engine


# ─── Global state ─────────────────────────────────────────────────────────────
_GLOBAL_AGENT = None
_GLOBAL_HANDLER: Optional[StreamingCallbackHandler] = None


async def get_agent():
    """Inisialisasi atau kembalikan agent dari cache memori."""
    global _GLOBAL_AGENT, _GLOBAL_HANDLER
    logger = logging.getLogger("uvicorn")

    # Sudah di-cache — langsung kembalikan
    if _GLOBAL_AGENT is not None and _GLOBAL_HANDLER is not None:
        return _GLOBAL_AGENT

    queue = Queue()
    handler = StreamingCallbackHandler(queue)
    callback_manager = CallbackManager([handler])

    # Cek apakah vector index sudah ada di disk
    index_ready = (
        os.path.exists(STORAGE_DIR)
        and os.path.exists(os.path.join(STORAGE_DIR, "docstore.json"))
    )

    if index_ready:
        logger.info("⚡ Vector index ditemukan di cache, memuat langsung...")
        docs = []
    else:
        logger.info("📂 Vector index belum ada. Memulai ingest dokumen...")
        if os.path.exists(PIPELINE_STORAGE_DIR):
            docstore = SimpleDocumentStore.from_persist_dir(PIPELINE_STORAGE_DIR)
        else:
            docstore = SimpleDocumentStore()

        docs = await ingest(
            directory=f"{DATA_DIR}/sensus",
            docstore=docstore,
        )
        logger.info(f"✅ Ingest selesai: {len(docs)} dokumen siap untuk diindex.")

    bps_query_engine = _build_bps_query_engine(
        STORAGE_DIR, docs, callback_manager=callback_manager
    )

    _GLOBAL_AGENT = bps_query_engine
    _GLOBAL_HANDLER = handler

    logger.info("✅ Query engine siap! Backend siap menerima pertanyaan.")
    return bps_query_engine


def get_request_queue() -> Queue:
    """Buat Queue baru dan pasang ke handler global untuk satu request.
    Menggunakan lock untuk thread-safety."""
    q = Queue()
    if _GLOBAL_HANDLER is not None:
        _GLOBAL_HANDLER.set_queue(q)
    return q
