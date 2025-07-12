# app/api/routes/websockets.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.core.websockets import manager, notification_service
from app.core.security import verify_token
from app.config import settings
from app.database import get_db
from app.models import User
from app.config import settings

router = APIRouter()


async def get_user_from_token(token: str, db: Session) -> Optional[User]:
    """Extract user from JWT token for WebSocket authentication"""
    try:
        payload = verify_token(token)
        if not payload:
            return None
            
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        return user
        
    except (ValueError, TypeError):
        return None


@router.websocket("/notifications/{token}")
async def websocket_notifications(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time notifications
    URL: /ws/notifications/{jwt_token}
    """
    
    # Authenticate user
    user = await get_user_from_token(token, db)
    if not user:
        await websocket.close(code=4001, reason="Invalid authentication token")
        return
    
    # Connect user
    await manager.connect(websocket, user.id)
    
    try:
        while True:
            # Listen for client messages (heartbeat, preferences, etc.)
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_client_message(websocket, user.id, message, db)
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error for user {user.id}: {e}")
        manager.disconnect(websocket)


async def handle_client_message(websocket: WebSocket, user_id: int, message: dict, db: Session):
    """Handle messages sent from client to server"""
    
    message_type = message.get("type")
    
    if message_type == "heartbeat":
        # Respond to heartbeat to keep connection alive
        await manager.send_personal_message({
            "type": "heartbeat_response",
            "timestamp": message.get("timestamp")
        }, websocket)
    
    elif message_type == "mark_notification_read":
        # Mark specific notification as read
        notification_id = message.get("notification_id")
        # Here you could update database to mark notification as read
        await manager.send_personal_message({
            "type": "notification_marked_read",
            "notification_id": notification_id
        }, websocket)
    
    elif message_type == "get_online_users":
        # Send list of online users (for chat features later)
        online_users = manager.get_connected_users()
        await manager.send_personal_message({
            "type": "online_users",
            "users": online_users
        }, websocket)
    
    elif message_type == "typing_indicator":
        # Handle typing indicators for chat (future feature)
        target_user_id = message.get("target_user_id")
        if target_user_id:
            await manager.send_to_user({
                "type": "user_typing",
                "user_id": user_id,
                "typing": message.get("typing", False)
            }, target_user_id)


@router.get("/test-notifications")
async def test_notification_page():
    """Test page for WebSocket notifications (development only)"""
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ReWear WebSocket Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .notification { 
                background: #f0f0f0; 
                padding: 10px; 
                margin: 10px 0; 
                border-radius: 5px; 
                border-left: 4px solid #007bff;
            }
            .error { border-left-color: #dc3545; background: #fff5f5; }
            .success { border-left-color: #28a745; background: #f5fff5; }
            input, button { padding: 8px; margin: 5px; }
            #messages { max-height: 400px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <h1>ReWear WebSocket Notifications Test</h1>
        
        <div>
            <input type="text" id="tokenInput" placeholder="JWT Token" style="width: 400px;">
            <button onclick="connect()">Connect</button>
            <button onclick="disconnect()">Disconnect</button>
        </div>
        
        <div>
            <button onclick="sendHeartbeat()">Send Heartbeat</button>
            <button onclick="getOnlineUsers()">Get Online Users</button>
        </div>
        
        <div id="status">Status: Disconnected</div>
        
        <h3>Messages:</h3>
        <div id="messages"></div>

        <script>
            let ws = null;
            let isConnected = false;

            function updateStatus(status, isError = false) {
                const statusDiv = document.getElementById('status');
                statusDiv.textContent = 'Status: ' + status;
                statusDiv.style.color = isError ? 'red' : 'green';
            }

            function addMessage(message, type = 'info') {
                const messagesDiv = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `notification ${type}`;
                messageDiv.innerHTML = `
                    <strong>${new Date().toLocaleTimeString()}</strong><br>
                    <pre>${JSON.stringify(message, null, 2)}</pre>
                `;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }

            function connect() {
                const token = document.getElementById('tokenInput').value;
                if (!token) {
                    alert('Please enter a JWT token');
                    return;
                }

                const wsUrl = `ws://localhost:8000/api/v1/ws/notifications/${token}`;
                ws = new WebSocket(wsUrl);

                ws.onopen = function() {
                    isConnected = true;
                    updateStatus('Connected');
                    addMessage({type: 'connection', message: 'WebSocket connected'}, 'success');
                };

                ws.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        addMessage(data, 'info');
                    } catch (e) {
                        addMessage({raw: event.data}, 'error');
                    }
                };

                ws.onclose = function() {
                    isConnected = false;
                    updateStatus('Disconnected');
                    addMessage({type: 'connection', message: 'WebSocket disconnected'}, 'error');
                };

                ws.onerror = function(error) {
                    updateStatus('Error', true);
                    addMessage({type: 'error', message: 'WebSocket error', error: error}, 'error');
                };
            }

            function disconnect() {
                if (ws && isConnected) {
                    ws.close();
                }
            }

            function sendHeartbeat() {
                if (ws && isConnected) {
                    ws.send(JSON.stringify({
                        type: 'heartbeat',
                        timestamp: Date.now()
                    }));
                } else {
                    alert('Not connected');
                }
            }

            function getOnlineUsers() {
                if (ws && isConnected) {
                    ws.send(JSON.stringify({
                        type: 'get_online_users'
                    }));
                } else {
                    alert('Not connected');
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# Admin endpoints for testing notifications
@router.post("/admin/send-test-notification")
async def send_test_notification(
    user_id: int,
    message: str,
    notification_type: str = "system_announcement"
):
    """Send test notification to specific user (admin only)"""
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    
    test_notification = {
        "type": notification_type,
        "title": "Test Notification",
        "message": message,
        "timestamp": 12345678,
        "action_required": False
    }
    
    await manager.send_to_user(test_notification, user_id)
    
    return {
        "message": f"Test notification sent to user {user_id}",
        "online_users": manager.get_connected_users(),
        "is_user_online": manager.is_user_online(user_id)
    }


@router.get("/admin/websocket-stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics (admin only)"""
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    
    return {
        "total_connections": len(manager.user_sessions),
        "unique_users": len(manager.active_connections),
        "connected_users": manager.get_connected_users(),
        "connections_per_user": {
            user_id: len(connections) 
            for user_id, connections in manager.active_connections.items()
        }
    }