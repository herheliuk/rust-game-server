#!/usr/bin/env python3

from fastapi import FastAPI, Request, HTTPException, WebSocket, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from authlib.integrations.starlette_client import OAuth

from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

from websockets import connect as websockets_connect

import asyncio
from secrets import token_urlsafe
from json import loads as json_loads, dumps as json_dumps

app = FastAPI(openapi_url=None)

app. add_middleware(SessionMiddleware, secret_key=token_urlsafe(32))

config = Config()

outh = OAuth(config)

outh.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    client_kwargs=({"scope": "openid"})
)

internal_ws_uri = f"ws://{config("RCON_HOST")}:{config("RCON_PORT")}/{config("RCON_PASSWORD")}"

WHITE_LIST = set(config("WHITE_LISTED_GOOGLE_OPEN_IDS").split(","))

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def homepage(request: Request):
    token = request.cookies.get("token")
    if not token or token not in TOKENS:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/")
async def rcon_ws (websocket: WebSocket):
    await websocket.accept()

    token = websocket.cookies.get("token")
    if not token or token not in TOKENS:
        await websocket.close(code=4401)
        return

    async with websockets_connect(internal_ws_uri, ping_timeout=None) as rcon:
        async def web_to_rcon():
            while True:
                raw = await websocket.receive_text()
                message = json_loads(raw).get("Message")
                await rcon.send(json_dumps({
                    "Identifier": -1,
                    "Message": message,
                    "Name": "WebRcon"
                }))
                
        async def rcon_to_web():
            while True:
                raw = await rcon.recv()
                message = json_loads(raw).get("Message")
                await websocket.send_text(message)

        await asyncio.gather(web_to_rcon(), rcon_to_web())

@app.get("/login")
async def login(request: Request) :
    redirect_uri = str(request.url_for('auth')).replace('http:', 'https:')
    return await outh.google.authorize_redirect(request, redirect_uri)

TOKENS = {}

@app.get("/auth/google/callback")
async def auth(request: Request, response: Response):
    token = await outh.google.authorize_access_token(request)
    user_id = token.get("userinfo").get("sub")
    
    if user_id not in WHITE_LIST:
        raise HTTPException(status_code=403, detail=f"{user_id} isn't whitelisted")
    
    token = token_urlsafe(32)
    TOKENS [token] = user_id
    
    response = RedirectResponse(url="/")
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        max_age=60*60*24, # 1 day
        secure=True,
        samesite="lax"
    )
    
    return response

@app.post("/logout")
async def logout(request: Request):
    request.session.pop('authorised', None)
    return RedirectResponse(url="/login")
