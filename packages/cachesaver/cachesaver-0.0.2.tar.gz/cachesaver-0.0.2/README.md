# Cachesaver
Cachesaver is a high-efficiency caching library for experiments with large language models (LLMs), designed to minimize costs, improve reproducibility, and streamline debugging. The library enables caching of multiple responses per query, tracks usage for unique sampling across runs, and ensures statistical integrity. Built on Python’s `asyncio`, Cachesaver supports asynchronous execution, request batching, prompt deduplication, and race-condition prevention.

```python
from cachesaver.models.openai import AsyncOpenAI

client = AsyncOpenAI(batch_size=2)

resp = await client.chat.completions.create(
    model="gpt-4.1-nano",
    messages=[
        {"role": "user", "content": "What's the capital of France?"}
    ]
)
```