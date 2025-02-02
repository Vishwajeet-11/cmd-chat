import rsa
import asyncio 
from server.models import Message
from cryptography.fernet import Fernet
from sanic.response import HTTPResponse
from sanic import Sanic, Request, response, Websocket

app = Sanic("app")
app.config.OAS = False

# Message structure is:
# [username: message, ...]
actual_messages: list[Message] = []
# Users structure is
# {Ip, Username: Public key} 
users: dict[str, str] = {}
key = Fernet.generate_key()


@app.websocket("/talk")
async def talking(request: Request, ws: Websocket) -> HTTPResponse:
    while True:
        data: str = await ws.recv()
        serialized_message: dict = eval(data)
        new_message = Message(
            message=serialized_message.get("text")
        )
        actual_messages.append(new_message)
        await ws.send("{'status': 'ok'}")
        await asyncio.sleep(0.2)


@app.websocket("/update")
async def talking(request: Request, ws: Websocket) -> HTTPResponse:
    while True:
        payload = str({
            "status": [i.message for i in actual_messages], 
            "users_in_chat": list(users.keys())
        })
        await ws.send(payload.encode())
        await asyncio.sleep(0.2)


@app.route('/get_key', methods=['GET', 'POST'])
async def get_key(request: Request) -> HTTPResponse:
    
    pubkey = rsa.PublicKey.load_pkcs1(request.form.get('pubkey'))
    data = rsa.encrypt(key, pubkey)
    
    if request.ip not in users:
        users[f"{request.ip}, {request.form.get('username')}"] = key
    
    return response.raw(data)