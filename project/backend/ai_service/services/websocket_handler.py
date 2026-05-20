"""
WebSocket Handler
实时WebSocket推送服务
"""

from fastapi import WebSocket
from typing import Dict, Set, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: Dict[int, Set[WebSocket]] = {
            1: set(), 2: set(), 3: set(), 4: set(), 5: set()
        }

    async def start(self):
        """启动WebSocket服务"""
        logger.info("WebSocket manager started")

    async def stop(self):
        """停止WebSocket服务"""
        # Close all connections
        for connection in self.active_connections.copy():
            await connection.close()
        self.active_connections.clear()
        for zone_id in self.subscriptions:
            self.subscriptions[zone_id].clear()
        logger.info("WebSocket manager stopped")

    async def connect(self, websocket: WebSocket, zone_id: Optional[int] = None):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections.add(websocket)

        if zone_id and 1 <= zone_id <= 5:
            self.subscriptions[zone_id].add(websocket)

        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, zone_id: Optional[int] = None):
        """断开WebSocket连接"""
        self.active_connections.discard(websocket)

        if zone_id and 1 <= zone_id <= 5:
            self.subscriptions[zone_id].discard(websocket)

        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast_anomaly(self, zone_id: int, anomaly_data: Dict):
        """广播异常告警到订阅者"""
        message = {
            "type": "anomaly_alert",
            "zone_id": zone_id,
            "data": anomaly_data,
            "timestamp": datetime.now().isoformat()
        }

        # 发送给所有订阅该区域的用户
        if 1 <= zone_id <= 5:
            disconnected = set()
            for connection in self.subscriptions[zone_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send to client: {e}")
                    disconnected.add(connection)

            # 清理断开的连接
            for conn in disconnected:
                self.subscriptions[zone_id].discard(conn)

        # 同时发送给所有连接的用户（重要告警）
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to client: {e}")
                disconnected.add(connection)

        for conn in disconnected:
            self.active_connections.discard(conn)

    async def broadcast_maintenance_alert(self, maintenance_data: Dict):
        """广播维护告警"""
        message = {
            "type": "maintenance_alert",
            "data": maintenance_data,
            "timestamp": datetime.now().isoformat()
        }

        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send maintenance alert: {e}")
                disconnected.add(connection)

        for conn in disconnected:
            self.active_connections.discard(conn)

    async def broadcast_heartbeat(self):
        """发送心跳包"""
        message = {
            "type": "heartbeat",
            "timestamp": datetime.now().isoformat(),
            "active_connections": len(self.active_connections)
        }

        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                disconnected.add(connection)

        for conn in disconnected:
            self.active_connections.discard(conn)
