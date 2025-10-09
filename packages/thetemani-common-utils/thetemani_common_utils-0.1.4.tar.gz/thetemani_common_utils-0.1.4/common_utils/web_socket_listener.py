import websockets
import json
import os
import signal
from typing import Callable
import asyncio


class WebSocketServer:
    def __init__(self, port: int):
        self.port = port
        self.stop_event = asyncio.Event()
        self.on_message_received = None

    def change_message_received_callback(self, on_message_received: Callable):
        self.on_message_received = on_message_received

    def clear_on_message_received(self):
        self.on_message_received = None

    async def start(self):
        await self._start_websocket_listener()

    async def _start_websocket_listener(self):
        async def handler(websocket):
            while True:
                try:
                    data = await websocket.recv()
                    data_obj = json.loads(data)
                    if data_obj.get("Close"):
                        print(f"Closing web socket at port {self.port}")
                        await self.send_close_request()
                        break
                    else:
                        self.on_message_received(data)
                except websockets.ConnectionClosed:
                    print("Connection closed by the server")
                    break

        server = await websockets.serve(handler, "localhost", self.port)
        print(f"WebSocket server started on port {self.port}")
        await self.stop_event.wait()
        server.close()
        await server.wait_closed()
        print(f"WebSocket server stopped on port {self.port}")
        self.free_port()

    async def send_close_request(self):
        uri = f"ws://localhost:{self.port}"
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps({"Close": True}))
            print(f"Sent WebSocket close request to server on port {
                  self.port}")
            await websocket.close()

    def free_port(self):
        while True:
            pids = self.get_pids_using_port(self.port)
            if pids:
                for pid in pids:
                    print(f"Killing process with PID {pid} to free the port.")
                    try:
                        os.kill(pid, signal.SIGTERM)
                    except Exception as e:
                        print(f"Failed to kill process {pid}: {e}")
            else:
                print(f"No processes found using port {self.port}.")
                break

    @staticmethod
    def get_pids_using_port(port):
        try:
            result = os.popen(f"lsof -nP -t -i:{port}").read().strip()
            if result:
                return [int(pid) for pid in result.splitlines()]
            else:
                return []
        except Exception as e:
            print(f"Error getting PIDs for port {port}: {e}")
            return []
