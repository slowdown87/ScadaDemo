"""
WebSocket Handler
WebSocket处理器
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List, Set
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """连接管理器"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.zone_subscriptions: Dict[int, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, zone_id: int = None):
        """接受WebSocket连接"""
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)

            if zone_id:
                if zone_id not in self.zone_subscriptions:
                    self.zone_subscriptions[zone_id] = set()
                self.zone_subscriptions[zone_id].add(websocket)

        logger.info(f"WebSocket connected, zone_id={zone_id}, total={len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket, zone_id: int = None):
        """断开WebSocket连接"""
        async with self._lock:
            self.active_connections.discard(websocket)

            if zone_id and zone_id in self.zone_subscriptions:
                self.zone_subscriptions[zone_id].discard(websocket)

        logger.info(f"WebSocket disconnected, zone_id={zone_id}, total={len(self.active_connections)}")

    async def broadcast(self, message: dict, zone_id: int = None):
        """广播消息"""
        if zone_id and zone_id in self.zone_subscriptions:
            connections = self.zone_subscriptions[zone_id]
        else:
            connections = self.active_connections

        disconnected = set()
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message: {e}")
                disconnected.add(connection)

        for conn in disconnected:
            await self.disconnect(conn)

    def get_stats(self) -> dict:
        """获取连接统计"""
        return {
            "total_connections": len(self.active_connections),
            "zone_subscriptions": {
                zone_id: len(connections)
                for zone_id, connections in self.zone_subscriptions.items()
            }
        }


manager = ConnectionManager()


@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket, zone_id: int = None):
    """
    WebSocket连接端点

    Args:
        websocket: WebSocket连接
        zone_id: 订阅的区域ID (可选)
    """
    await manager.connect(websocket, zone_id)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_websocket_message(websocket, message, zone_id)

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                })

    except WebSocketDisconnect:
        await manager.disconnect(websocket, zone_id)
        logger.info(f"Client disconnected from zone {zone_id}")


async def handle_websocket_message(websocket: WebSocket, message: dict, zone_id: int):
    """处理WebSocket消息"""
    msg_type = message.get("type")

    if msg_type == "ping":
        await websocket.send_json({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        })

    elif msg_type == "subscribe":
        new_zone = message.get("zone_id", zone_id)
        async with manager._lock:
            if new_zone not in manager.zone_subscriptions:
                manager.zone_subscriptions[new_zone] = set()
            manager.zone_subscriptions[new_zone].add(websocket)

        await websocket.send_json({
            "type": "subscribed",
            "zone_id": new_zone,
            "timestamp": datetime.now().isoformat()
        })

    elif msg_type == "unsubscribe":
        old_zone = message.get("zone_id")
        if old_zone and old_zone in manager.zone_subscriptions:
            async with manager._lock:
                manager.zone_subscriptions[old_zone].discard(websocket)

        await websocket.send_json({
            "type": "unsubscribed",
            "zone_id": old_zone,
            "timestamp": datetime.now().isoformat()
        })

    elif msg_type == "get_anomaly":
        anomaly_data = await fetch_anomaly_data(zone_id)
        await websocket.send_json({
            "type": "anomaly_data",
            "data": anomaly_data,
            "timestamp": datetime.now().isoformat()
        })

    elif msg_type == "get_stats":
        await websocket.send_json({
            "type": "stats",
            "data": manager.get_stats(),
            "timestamp": datetime.now().isoformat()
        })

    else:
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {msg_type}",
            "timestamp": datetime.now().isoformat()
        })


async def fetch_anomaly_data(zone_id: int) -> dict:
    """获取异常数据"""
    return {
        "zone_id": zone_id,
        "is_anomaly": False,
        "overall_score": 0.15,
        "alarm_level": "normal",
        "detector_results": {}
    }


async def broadcast_anomaly_alert(zone_id: int, alert_data: dict):
    """
    广播异常告警

    Args:
        zone_id: 区域ID
        alert_data: 告警数据
    """
    message = {
        "type": "anomaly_alert",
        "zone_id": zone_id,
        "data": alert_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message, zone_id)


async def broadcast_maintenance_reminder(zone_id: int, reminder_data: dict):
    """
    广播维护提醒

    Args:
        zone_id: 区域ID
        reminder_data: 提醒数据
    """
    message = {
        "type": "maintenance_reminder",
        "zone_id": zone_id,
        "data": reminder_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message, zone_id)


@router.get("/stats")
async def get_connection_stats():
    """获取连接统计"""
    return manager.get_stats()
