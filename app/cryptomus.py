import json
import hashlib
import base64
from datetime import datetime
from typing import Any

from aiohttp import ClientSession
from config import API_KEY, MERCHANT_UUID

def generate_headers(data: str) -> dict[str: Any]:
    json_dumps  = json.dumps(data)
    print("Data used for headers (generate_headers):", json_dumps)  # Печать данных перед подписью
    sign = hashlib.md5(
        base64.b64encode(json_dumps.encode("ascii")) + API_KEY.encode("ascii")
    ).hexdigest()
    print("Generated sign:", sign)

    return{"merchant": MERCHANT_UUID, "sign": sign, "content-type": "application/json"}

async def create_invoice(user_id: int)-> Any:
    async with ClientSession() as session:
        data = {
            "amount": "10",
            "order_id": f"MY-TEST-ORDER-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "currency": "USDT",
            "network": "tron",
            "lifetime": 900

        }
        print("Data to send (create_invoice):", data)
        json_dumps  = json.dumps(data)
        response = await session.post(
            "https://api.cryptomus.com/v1/payment",
            data = json_dumps,
            headers=generate_headers(data)
        )
        print("Response status (create_invoice):", response.status)
        #return await response.json()
        result = await response.json()
        print("Response JSON (create_invoice):", result)

        return result
async def get_invoice(uuid: str) -> Any:
    async with ClientSession() as session:
        data = {"uuid": uuid}
        # Печатаем данные, которые отправляем
        print("Data to send (get_invoice):", data)
        #json_dumps  = json.dumps({"uuid":uuid})
        json_dumps = json.dumps(data)
        print("JSON to send (get_invoice):", json_dumps)
        response = await session.post(
            "https://api.cryptomus.com/v1/payment/info",
            data=json_dumps,
            headers=generate_headers(json_dumps)
        )
        # Печатаем статус ответа
        print("Response status (get_invoice):", response.status)

        # Получаем и печатаем JSON-ответ
        result = await response.json()
        print("Response JSON (get_invoice):", result)

        return result