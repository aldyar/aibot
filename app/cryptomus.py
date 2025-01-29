import json
import hashlib
import base64
from datetime import datetime
from typing import Any
from aiohttp import ClientSession
from config import API_KEY, MERCHANT_UUID
from pprint import pprint

def generate_headers(data: str) -> dict[str: Any]:
    print("Data used for headers (generate_headers):", data)  # Печать данных перед подписью
    sign = hashlib.md5(
        base64.b64encode(data.encode("ascii")) + API_KEY.encode("ascii")
    ).hexdigest()
    print("Generated sign:", sign)

    return{"merchant": MERCHANT_UUID, "sign": sign, "content-type": "application/json"}


async def create_invoice(user_id: int, amount)-> Any:
    async with ClientSession() as session:
        json_dumps =json.dumps( {
            "amount": amount,
            "order_id": f"MY-TEST-ORDER-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "currency": "USD",
            #"network": "BSC",
            #"lifetime": 900
        })
        response = await session.post(
            "https://api.cryptomus.com/v1/payment",
            data = json_dumps,
            headers=generate_headers(json_dumps)
        )
        result = await response.json()
        return result
    

async def get_invoice(uuid: str) -> Any:
    async with ClientSession() as session:
        json_dumps =json.dumps( {"uuid": uuid})
        print (json_dumps)
        response = await session.post(
            "https://api.cryptomus.com/v1/payment/info",
            data=json_dumps,
            headers=generate_headers(json_dumps)
        )
        result = await response.json()
        pprint(result)

        return result