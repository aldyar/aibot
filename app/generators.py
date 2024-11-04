import asyncio
from openai import AsyncOpenAI
import base64
import aiohttp
import aiofiles
from config import AITOKEN
import json


client = AsyncOpenAI(api_key='AITOKEN')


async def gpt_text(req, model):
    completion = await client.chat.completions.create(
        messages=[{"role": "user", "content": req}],
        model= model
    )
    return {'response':completion.choices[0].message.content, 
            'usage':completion.usage.total_tokens}


async def gpt_image(req, model):
    response = await client.images.generate(
    model="dall-e-3",
    prompt=req,
    size="1024x1024",
    quality="standard",
    n=1,)
    return {'response':response.data[0].url, 
            'usage':1}


async def encode_image(image_path):
    async with aiofiles.open(image_path, "rb") as image_file:
        return base64.b64encode(await image_file.read()).decode('utf-8')


async def gpt_vision(caption: str, model: str, image_path: str):
    base64_image = await encode_image(image_path)
    caption = caption if caption else "What is in this image?"

    try:
        # Создание сообщения для OpenAI
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": caption},
                {
                    "role": "user",
                    "content": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        )

        # Проверьте структуру ответа
        if response and response.choices:
            return response.choices[0].message.content
        else:
            return "No valid response from GPT Vision."
    except Exception as e:
        print(f"Error in GPT Vision: {str(e)}")
        return "Error in processing the image."




""" на 15 минуте остановился писать код
async def gpt_vision(req, model, file):
    #доп код
    if req is None or not isinstance(req, str):
        raise ValueError("Текст запроса должен быть строкой.")
    
    base64_image = await encode_image(file)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AITOKEN}"
    }
    payload = { 
    "model":model,
    "messages":[
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": req,
            },
            {
            "type": "image_url",
            "image_url": {
                "url":  f"data:image/jpeg;base64,{base64_image}"
            },
            },
        ],
        }
    ],
    "max_tokens": 300
    }
    #доп код
    print("Payload:", json.dumps(payload, ensure_ascii=False, indent=2))
   
    
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
            completion = await response.json()
    return {'response':completion['choices'][0]['message']['content'], 
            'usage': completion['usage']['total_tokens']}
    """

