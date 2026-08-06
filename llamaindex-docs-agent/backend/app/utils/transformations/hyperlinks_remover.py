"""Transformation: Hapus hyperlink dan gambar dari teks node."""
import re

from llama_index.core.schema import TransformComponent


class HyperlinksRemover(TransformComponent):
    """Hapus hyperlinks dan gambar dari konten Markdown node."""

    def __call__(self, nodes, **kwargs):
        for node in nodes:
            text = node.get_content()
            if not text:
                continue
            # Hapus gambar (beserta spasi di sekitarnya): ![alt](url)
            text = re.sub(r"\s*!\[.*?\]\(.*?\)\s*", " ", text)
            # Pertahankan teks link, buang URL: [teks](url) → teks
            text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
            # Bersihkan spasi berlebih dan baris kosong berlebih
            text = re.sub(r" {2,}", " ", text)
            text = re.sub(r"\n{3,}", "\n\n", text)
            node.set_content(text.strip())
        return nodes