import asyncio
import json
import logging
import websockets
from typing import List, Dict, Callable

class Dendrite:
    """
    Simulates the Neural Link (WebSocket Listener).
    Acts as the 'Receptor' in the Scientific E2E loop.
    """
    def __init__(self, uri="ws://localhost:8001/mcp/events"):
        self.uri = uri
        self.events = []
        self.logger = logging.getLogger("Dendrite")
        self.connected = False
        self._stop_event = asyncio.Event()

    async def listen(self, duration=5.0, parser: Callable = None):
        """
        Listen for events for a fixed duration.
        """
        self.events = []
        try:
            async with websockets.connect(self.uri) as websocket:
                self.connected = True
                self.logger.info("Dendrite connected to Neural Mesh.")
                
                # Subscribe to everything
                await websocket.send(json.dumps({"type": "subscribe", "channel": "*"}))
                
                try:
                    while True:
                        try:
                            # Wait for message with timeout
                            message = await asyncio.wait_for(websocket.recv(), timeout=duration)
                            data = json.loads(message)
                            if parser:
                                data = parser(data)
                            self.events.append(data)
                        except asyncio.TimeoutError:
                            # Expected timeout when listening is done
                            break
                except Exception as e:
                    self.logger.error(f"Dendrite stream error: {e}")
                    
        except Exception as e:
            self.logger.error(f"Dendrite connection failed: {e}")
            self.connected = False
            
        return self.events

    async def capture_until(self, condition: Callable[[Dict], bool], timeout=10.0) -> List[Dict]:
        """
        Capture events until a condition is met or timeout.
        Returns all captured events.
        """
        captured = []
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with websockets.connect(self.uri) as websocket:
                await websocket.send(json.dumps({"type": "subscribe", "channel": "*"}))
                
                while (asyncio.get_event_loop().time() - start_time) < timeout:
                    try:
                        msg = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                        data = json.loads(msg)
                        captured.append(data)
                        if condition(data):
                            return captured
                    except asyncio.TimeoutError:
                        continue
        except Exception as e:
            self.logger.error(f"Capture failed: {e}")
            
        return captured
