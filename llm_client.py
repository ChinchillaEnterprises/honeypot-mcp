import os
import asyncio
from google import genai
from google.genai import types

_client = None

def _get_client():
    global _client
    if _client is None:
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        _client = genai.Client(api_key=key)
    return _client

async def generate(prompt: str, timeout: float = 60.0) -> str:
    client = _get_client()

    def _sync():
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text

    return await asyncio.wait_for(
        asyncio.get_event_loop().run_in_executor(None, _sync),
        timeout=timeout,
    )

async def generate_parallel(prompts: list[str], timeout: float = 60.0) -> list[str]:
    tasks = [generate(p, timeout=timeout) for p in prompts]
    return await asyncio.gather(*tasks, return_exceptions=True)

async def research_with_grounding(query: str, timeout: float = 60.0) -> str:
    client = _get_client()

    def _sync():
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=query,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )
        return response.text

    return await asyncio.wait_for(
        asyncio.get_event_loop().run_in_executor(None, _sync),
        timeout=timeout,
    )
