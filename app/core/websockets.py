# app/core/websockets.py - Fixed database connection handling
import json
import asyncio
from typing import Dict, List, Optional
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.models import User
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Store user info for connections
        self.user_sessions: Dict[WebSocket, int] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        self.user_sessions[websocket] = user_id
        
        logger.info(f"User {user_id} connected via WebSocket")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "message": "Connected to ReWear notifications",
            "timestamp": asyncio.get_event_loop().time()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.user_sessions:
            user_id = self.user_sessions[websocket]
            
            if user_id in self.active_connections:
                self.active_connections[user_id].remove(websocket)
                
                # Clean up empty connection lists
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            del self.user_sessions[websocket]
            logger.info(f"User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")
            self.disconnect(websocket)
    
    async def send_to_user(self, message: dict, user_id: int):
        """Send message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected_sockets = []
            
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected_sockets.append(websocket)
            
            # Clean up disconnected sockets
            for socket in disconnected_sockets:
                self.disconnect(socket)
    
    async def broadcast_to_all(self, message: dict):
        """Send message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(message, user_id)
    
    def get_connected_users(self) -> List[int]:
        """Get list of currently connected user IDs"""
        return list(self.active_connections.keys())
    
    def is_user_online(self, user_id: int) -> bool:
        """Check if user is currently connected"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0


# Global connection manager instance
manager = ConnectionManager()


class NotificationService:
    """Enhanced service for sending WebSocket + Email notifications with proper DB handling"""
    
    def __init__(self):
        # Import email service here to avoid circular imports
        try:
            from app.services.email import email_service
            self.email_service = email_service
            self.email_enabled = True
        except ImportError:
            logger.warning("Email service not available - only WebSocket notifications will be sent")
            self.email_service = None
            self.email_enabled = False
    
    def _get_fresh_db_session(self):
        """Get a fresh database session to avoid connection issues"""
        from app.database import SessionLocal
        return SessionLocal()
    
    async def _get_user_safely(self, user_id: int) -> Optional[User]:
        """Get user with proper error handling"""
        db = None
        try:
            db = self._get_fresh_db_session()
            user = db.query(User).filter(User.id == user_id).first()
            return user
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None
        finally:
            if db:
                db.close()
    
    async def notify_swap_request(self, requester_id: int, owner_id: int, swap_data: dict):
        """Notify item owner of new swap request (WebSocket + Email)"""
        
        # WebSocket notification (instant)
        ws_notification = {
            "type": "swap_request",
            "title": "New Swap Request",
            "message": f"Someone wants to swap for your item: {swap_data.get('item_title', 'Unknown item')}",
            "data": {
                "swap_id": swap_data.get("swap_id"),
                "requester_id": requester_id,
                "item_id": swap_data.get("item_id"),
                "swap_type": swap_data.get("swap_type")
            },
            "timestamp": asyncio.get_event_loop().time(),
            "action_required": True
        }
        
        await manager.send_to_user(ws_notification, owner_id)
        
        # Email notification (for offline users or always if configured)
        if self.email_enabled:
            try:
                # Get users with fresh DB session
                owner = await self._get_user_safely(owner_id)
                requester = await self._get_user_safely(requester_id)
                
                if owner and requester and owner.email:
                    # Only send email if user is offline (or always if configured)
                    should_send_email = (
                        not manager.is_user_online(owner_id) or 
                        not getattr(self, 'email_for_offline_only', True)
                    )
                    
                    if should_send_email:
                        await self.email_service.send_swap_request_email(
                            owner=owner,
                            requester=requester,
                            swap_data=swap_data
                        )
                        logger.info(f"Swap request email sent to {owner.email}")
                
            except Exception as e:
                logger.error(f"Failed to send swap request email: {e}")
    
    async def notify_swap_response(self, requester_id: int, owner_id: int, swap_data: dict, accepted: bool):
        """Notify requester of swap response (WebSocket + Email)"""
        status = "accepted" if accepted else "rejected"
        
        # WebSocket notification
        ws_notification = {
            "type": "swap_response",
            "title": f"Swap Request {status.title()}",
            "message": f"Your swap request for '{swap_data.get('item_title', 'item')}' was {status}",
            "data": {
                "swap_id": swap_data.get("swap_id"),
                "owner_id": owner_id,
                "item_id": swap_data.get("item_id"),
                "status": status
            },
            "timestamp": asyncio.get_event_loop().time(),
            "action_required": accepted
        }
        
        await manager.send_to_user(ws_notification, requester_id)
        
        # Email notification for acceptance (important event)
        if self.email_enabled and accepted:
            try:
                owner = await self._get_user_safely(owner_id)
                requester = await self._get_user_safely(requester_id)
                
                if owner and requester and requester.email:
                    await self.email_service.send_swap_accepted_email(
                        requester=requester,
                        owner=owner,
                        swap_data=swap_data
                    )
                    logger.info(f"Swap acceptance email sent to {requester.email}")
                
            except Exception as e:
                logger.error(f"Failed to send acceptance email: {e}")
    
    async def notify_swap_completed(self, user_ids: List[int], swap_data: dict):
        """Notify all parties when swap is completed (WebSocket + Email)"""
        
        # WebSocket notification
        ws_notification = {
            "type": "swap_completed",
            "title": "Swap Completed!",
            "message": f"Your swap for '{swap_data.get('item_title', 'item')}' has been completed",
            "data": {
                "swap_id": swap_data.get("swap_id"),
                "item_id": swap_data.get("item_id"),
                "points_earned": swap_data.get("points_earned", 0)
            },
            "timestamp": asyncio.get_event_loop().time(),
            "action_required": False
        }
        
        for user_id in user_ids:
            await manager.send_to_user(ws_notification, user_id)
        
        # Email notifications (important milestone)
        if self.email_enabled:
            try:
                for user_id in user_ids:
                    user = await self._get_user_safely(user_id)
                    if user and user.email:
                        await self.email_service.send_swap_completed_email(
                            user=user,
                            swap_data=swap_data
                        )
                        logger.info(f"Swap completion email sent to {user.email}")
                
            except Exception as e:
                logger.error(f"Failed to send completion emails: {e}")
    
    async def notify_points_earned(self, user_id: int, points: int, reason: str):
        """Notify user when they earn points (WebSocket only)"""
        notification = {
            "type": "points_earned",
            "title": "Points Earned!",
            "message": f"You earned {points} points: {reason}",
            "data": {
                "points": points,
                "reason": reason
            },
            "timestamp": asyncio.get_event_loop().time(),
            "action_required": False
        }
        
        await manager.send_to_user(notification, user_id)
    
    async def notify_item_approved(self, user_id: int, item_data: dict):
        """Notify user when their item is approved (WebSocket only)"""
        notification = {
            "type": "item_approved",
            "title": "Item Approved",
            "message": f"Your item '{item_data.get('title', 'item')}' is now live on ReWear!",
            "data": {
                "item_id": item_data.get("item_id"),
                "title": item_data.get("title")
            },
            "timestamp": asyncio.get_event_loop().time(),
            "action_required": False
        }
        
        await manager.send_to_user(notification, user_id)
    
    async def send_welcome_notification(self, user_id: int, user_email: str = None, user_name: str = None):
        """Send welcome notification to new users (WebSocket + Email) with user data"""
        
        # WebSocket welcome
        ws_notification = {
            "type": "welcome",
            "title": "Welcome to ReWear! 🌱",
            "message": "Start your sustainable fashion journey today!",
            "data": {
                "signup_bonus": 100,
                "next_steps": ["Upload your first item", "Browse available swaps", "Earn more points"]
            },
            "timestamp": asyncio.get_event_loop().time(),
            "action_required": False
        }
        
        await manager.send_to_user(ws_notification, user_id)
        
        # Welcome email with user data passed directly
        if self.email_enabled:
            try:
                if user_email and user_name:
                    # Use provided user data to avoid DB connection issues
                    from app.models import User
                    temp_user = User(
                        id=user_id,
                        email=user_email,
                        first_name=user_name.split()[0] if user_name else "User",
                        username=user_name or f"user_{user_id}"
                    )
                    
                    await self.email_service.send_welcome_email(temp_user)
                    logger.info(f"Welcome email sent to {user_email}")
                else:
                    # Fallback: get user from DB
                    user = await self._get_user_safely(user_id)
                    if user and user.email:
                        await self.email_service.send_welcome_email(user)
                        logger.info(f"Welcome email sent to {user.email}")
                
            except Exception as e:
                logger.error(f"Failed to send welcome email: {e}")
    
    async def notify_system_announcement(self, message: str, user_ids: Optional[List[int]] = None):
        """Send system-wide announcements (WebSocket only)"""
        notification = {
            "type": "system_announcement",
            "title": "ReWear Announcement",
            "message": message,
            "timestamp": asyncio.get_event_loop().time(),
            "action_required": False
        }
        
        if user_ids:
            for user_id in user_ids:
                await manager.send_to_user(notification, user_id)
        else:
            await manager.broadcast_to_all(notification)


# Notification service instance
notification_service = NotificationService()