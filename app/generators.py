from openai import AsyncOpenAI
from config import AITOKEN
import httpx


client = AsyncOpenAI(api_key=AITOKEN)
http_client=httpx.AsyncClient(proxies="http://fjNUVe:t5BfLK@194.32.251.22:8000",
                                                   transport=httpx.HTTPTransport(local_address="0.0.0.0"))


async def gpt_text(history, model):
    completion = await client.chat.completions.create(
        messages=history,
        model=model
    )
    return {
        'response': completion.choices[0].message.content,
        'usage': {
            'prompt_tokens': completion.usage.prompt_tokens,
            'completion_tokens': completion.usage.completion_tokens,
            'total_tokens': completion.usage.total_tokens
        }
    }


async def gpt_image(req, model):
    response = await client.images.generate(
    model="dall-e-3",
    prompt=req,
    size="1024x1024",
    quality="standard",
    n=1,)
    return {'response':response.data[0].url, 
            'usage':1}

