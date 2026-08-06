import asyncio

from llama_index.core.schema import TransformComponent
from llama_index.core.bridge.pydantic import Field
from llama_index.core.response_synthesizers import TreeSummarize
from llama_index.llms.ollama import Ollama

class DocsSummarizer(TransformComponent):
  """Summarize current documentation page."""

  llm: str = Field(
    default='qwen2.5:1.5b',
    description='LLM to summarize'
  )

  async def generate_summary(self, node, summarizer, prompt):
      print(f"getting summary for {node.id_}")
      summary = await summarizer.aget_response(prompt, [node.text])
      node.metadata['summary'] = summary
  
  async def process_nodes(self, nodes, summarizer, prompt):
    tasks = []
    for node in nodes:
      task = asyncio.create_task(
         self.generate_summary(node, summarizer, prompt)
      )
      tasks.append(task)
    await asyncio.gather(*tasks)
  
  
  def __call__(self, nodes, **kwargs):
    # Summarizer hanya dijalankan secara async (acall).
    # Kembalikan nodes apa adanya agar pipeline tidak kehilangan data.
    return nodes

  async def acall(self, nodes, **kwargs):
    summarizer = TreeSummarize(
      verbose=True,
      llm=Ollama(
        model=self.llm,
        temperature=0,
        request_timeout=60.0,
      )
    )


    SUMMARY_PROMPT = "Berikan ringkasan singkat di bawah 50 kata dari dokumen FAQ sensus BPS berikut. Ada banyak dokumen, ini hanya salah satunya. Ringkasan 50 kata ini harus mencakup semua topik yang dibahas dalam dokumen ini secara singkat, sehingga orang yang membaca ringkasan ini mendapat gambaran lengkap tentang apa yang akan mereka pelajari jika membaca seluruh dokumen."

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(
    #   self.process_nodes(nodes, summarizer, SUMMARY_PROMPT)
    # )
    await self.process_nodes(nodes, summarizer, SUMMARY_PROMPT)
    return nodes