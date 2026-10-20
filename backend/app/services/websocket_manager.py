import json
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger("flying_cabs.websocket")

class ConnectionManager:
    def __init__(self):
        # rider_id -> list of active WebSockets
        self.rider_connections: Dict[int, List[WebSocket]] = {}
        # driver_id -> list of active WebSockets
        self.driver_connections: Dict[int, List[WebSocket]] = {}
        # fleet map spectators
        self.map_connections: List[WebSocket] = []

    async def connect_rider(self, rider_id: int, websocket: WebSocket):
        await websocket.accept()
        if rider_id not in self.rider_connections:
            self.rider_connections[rider_id] = []
        self.rider_connections[rider_id].append(websocket)
        logger.info(f"Rider {rider_id} connected via WebSocket")

    def disconnect_rider(self, rider_id: int, websocket: WebSocket):
        if rider_id in self.rider_connections:
            if websocket in self.rider_connections[rider_id]:
                self.rider_connections[rider_id].remove(websocket)
            if not self.rider_connections[rider_id]:
                del self.rider_connections[rider_id]
        logger.info(f"Rider {rider_id} disconnected")

    async def connect_driver(self, driver_id: int, websocket: WebSocket):
        await websocket.accept()
        if driver_id not in self.driver_connections:
            self.driver_connections[driver_id] = []
        self.driver_connections[driver_id].append(websocket)
        logger.info(f"Driver {driver_id} connected via WebSocket")

    def disconnect_driver(self, driver_id: int, websocket: WebSocket):
        if driver_id in self.driver_connections:
            if websocket in self.driver_connections[driver_id]:
                self.driver_connections[driver_id].remove(websocket)
            if not self.driver_connections[driver_id]:
                del self.driver_connections[driver_id]
        logger.info(f"Driver {driver_id} disconnected")

    async def connect_map(self, websocket: WebSocket):
        await websocket.accept()
        self.map_connections.append(websocket)
        logger.info("Map spectator connected via WebSocket")

    def disconnect_map(self, websocket: WebSocket):
        if websocket in self.map_connections:
            self.map_connections.remove(websocket)
        logger.info("Map spectator disconnected")

    async def send_to_rider(self, rider_id: int, message_type: str, data: dict):
        payload = json.dumps({"type": message_type, "data": data})
        if rider_id in self.rider_connections:
            dead_sockets = []
            for ws in self.rider_connections[rider_id]:
                try:
                    await ws.send_text(payload)
                except Exception:
                    dead_sockets.append(ws)
            for ws in dead_sockets:
                self.disconnect_rider(rider_id, ws)

    async def send_to_driver(self, driver_id: int, message_type: str, data: dict):
        payload = json.dumps({"type": message_type, "data": data})
        if driver_id in self.driver_connections:
            dead_sockets = []
            for ws in self.driver_connections[driver_id]:
                try:
                    await ws.send_text(payload)
                except Exception:
                    dead_sockets.append(ws)
            for ws in dead_sockets:
                self.disconnect_driver(driver_id, ws)

    async def broadcast_to_drivers(self, message_type: str, data: dict):
        payload = json.dumps({"type": message_type, "data": data})
        for driver_id, sockets in list(self.driver_connections.items()):
            dead_sockets = []
            for ws in sockets:
                try:
                    await ws.send_text(payload)
                except Exception:
                    dead_sockets.append(ws)
            for ws in dead_sockets:
                self.disconnect_driver(driver_id, ws)

    async def broadcast_to_map(self, message_type: str, data: dict):
        payload = json.dumps({"type": message_type, "data": data})
        dead_sockets = []
        for ws in self.map_connections:
            try:
                await ws.send_text(payload)
            except Exception:
                dead_sockets.append(ws)
        for ws in dead_sockets:
            self.disconnect_map(ws)

    async def broadcast_fleet_location(self, driver_id: int, lat: float, lng: float, altitude_m: float, status: str):
        msg = {
            "driver_id": driver_id,
            "lat": lat,
            "lng": lng,
            "altitude_m": altitude_m,
            "status": status
        }
        await self.broadcast_to_map("DRIVER_LOCATION_UPDATE", msg)


    async def broadcast_ride_update(self, ride_id: int, data: dict):
        event_type = data.get("event", "RIDE_UPDATE")
        await self.broadcast_to_map(event_type, data)
        if "rider_id" in data:
            await self.send_to_rider(data["rider_id"], event_type, data)
        if "driver_id" in data:
            await self.send_to_driver(data["driver_id"], event_type, data)

ws_manager = ConnectionManager()
