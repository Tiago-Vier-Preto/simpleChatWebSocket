import asyncio
import websockets

from asyncio import run
from asyncio import Future

from websockets import serve


async def http_handler(path, headers):
    """Route HTTP requests to their handlers"""
    from http import HTTPStatus
    from websockets.http import Headers

    if path == '/ui-chat':
        # Entregar para o navegador o conteúdo do arquivo chat.html,
        # que corresponde ao cliente chat implementado pelo webservice
        with open("chat.html") as f:
            headers = Headers(**{'Content-Type': 'text/html'})
            body = bytes(f.read(), 'utf-8')

            return HTTPStatus.OK, headers, body

    elif path == '/ui-echo':
        # Entregar para o navegador o conteúdo do arquivo echo.html,
        # que corresponde ao cliente echo implementado pelo webservice
        with open("echo.html") as f:
            headers = Headers(**{'Content-Type': 'text/html'})
            body = bytes(f.read(), 'utf-8')

            return HTTPStatus.OK, headers, body
        
    else:
        return None


async def echo(websocket):
    """Echo WebSocket handler"""
    async for message in websocket:
        await websocket.send(message)


async def chat(websocket, sessions={}):
    remote = websocket.remote_address
    sessions[remote] = websocket

    """Chat WebSocket handler"""
    try:
        async for message in websocket:
            for socket in sessions.values():
                await socket.send(message)
                print(f"Sent message to {socket.remote_address}: {message}") # informa que a mensagem foi enviada para o cliente
    finally:
        del sessions[remote]
        print(f"Session closed: {remote}") # informa que a sessão foi fechada


async def web_socket_router(websocket, path):
    """Route WebSocket requests to their handlers"""
    if path == '/':
        await websocket.close(reason=f'needs a path')
    elif path == '/echo':
        await echo(websocket)
    elif path == '/chat':
        print(f"Chat session started: {websocket.remote_address}") # informa que a sessão de chat foi iniciada
        await chat(websocket)
    else:
        await websocket.close(reason=f'path not found: {path}')


async def main():
    async with serve(web_socket_router, "localhost", 8080, process_request=http_handler):
        await Future()


run(main())
