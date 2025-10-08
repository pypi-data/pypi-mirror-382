"""
BuzuAI Service - Service để tích hợp với BuzuAI chatbot
Sử dụng SocketIO để gửi tin nhắn và nhận phản hồi từ AI
"""

import socketio
import logging
import time
from typing import Optional, Dict, Any
from threading import Event

logger = logging.getLogger(__name__)


class BuzuAIClient:
    """
    Client để kết nối và giao tiếp với BuzuAI chatbot
    Sử dụng singleton pattern để tái sử dụng kết nối
    """
    
    # Bot ID mặc định từ hệ thống BuzuAI
    DEFAULT_BOT_ID = "4489b201-a08a-4d87-81e1-632bcbdb44a8"
    BUZUAI_URL = "https://api.buzuai.com/app-chat"
    NAMESPACE = "/app-chat"
    
    # Timeout cho việc chờ phản hồi từ AI (seconds)
    RESPONSE_TIMEOUT = 300
    
    def __init__(self):
        self.sio = None
        self.response_data = None
        self.response_event = None
        self.is_connected = False
        self.session_id = None
        self.join_room_event = None
        
    def _create_client(self):
        """Tạo mới socket client với handlers"""
        sio = socketio.Client(logger=False, engineio_logger=False)
        
        @sio.event(namespace=self.NAMESPACE)
        def connect():
            self.is_connected = True
            logger.info(f"✅ Connected to BuzuAI: {sio.sid}")
        
        @sio.on("receiveMessage", namespace=self.NAMESPACE)
        def receive_message(data):
            """Nhận phản hồi từ AI"""
            logger.info(f"💬 Received AI response: {data}")
            self.response_data = data
            if self.response_event:
                self.response_event.set()
        
        @sio.on("receiveNotification", namespace=self.NAMESPACE)
        def receive_notification(data):
            """Nhận thông báo từ AI - bao gồm sessionId khi join room"""
            logger.info(f"🔔 Notification from AI: {data}")
            
            # Kiểm tra nếu có sessionId trong notification (khi join room)
            if "sessionId" in data and not self.session_id:
                self.session_id = data.get("sessionId")
                logger.info(f"✅ Received sessionId from notification: {self.session_id}")
                if self.join_room_event:
                    self.join_room_event.set()
        
        @sio.on("joinedRoom", namespace=self.NAMESPACE)
        def joined_room(data):
            """Nhận sessionId sau khi join room thành công (backup handler)"""
            logger.info(f"✅ Joined room successfully: {data}")
            if "sessionId" in data:
                self.session_id = data.get("sessionId")
                if self.join_room_event:
                    self.join_room_event.set()
        
        @sio.event(namespace=self.NAMESPACE)
        def disconnect():
            self.is_connected = False
            logger.info("❌ Disconnected from BuzuAI")
        
        return sio
    
    def connect(self) -> bool:
        """
        Kết nối đến BuzuAI server
        Returns: True nếu kết nối thành công
        """
        try:
            if self.sio and self.is_connected:
                return True
            
            self.sio = self._create_client()
            self.sio.connect(
                self.BUZUAI_URL,
                namespaces=[self.NAMESPACE],
                transports=["websocket"]
            )
            
            # Đợi kết nối được thiết lập
            timeout = 5
            start_time = time.time()
            while not self.is_connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            return self.is_connected
            
        except Exception as e:
            logger.error(f"Error connecting to BuzuAI: {str(e)}")
            return False
    
    def disconnect(self):
        """Ngắt kết nối"""
        try:
            if self.sio and self.is_connected:
                self.sio.disconnect()
                self.is_connected = False
                self.session_id = None
        except Exception as e:
            logger.error(f"Error disconnecting from BuzuAI: {str(e)}")
    
    def join_room(self, visitor_id: str, bot_id: Optional[str] = None) -> bool:
        """
        Join vào room chat với bot và chờ nhận sessionId
        
        Args:
            visitor_id: ID của user trong hệ thống (userId)
            bot_id: ID của bot, mặc định sử dụng DEFAULT_BOT_ID
        
        Returns: True nếu join thành công và nhận được sessionId
        """
        try:
            if not self.is_connected:
                if not self.connect():
                    return False
            
            # Nếu đã có sessionId, không cần join lại
            if self.session_id:
                logger.info(f"✅ Already in room with sessionId={self.session_id}")
                return True
            
            bot_id = bot_id or self.DEFAULT_BOT_ID
            
            # Reset session_id và tạo event để chờ
            self.session_id = None
            self.join_room_event = Event()
            
            # Emit joinRoom
            self.sio.emit("joinRoom", {
                "visitorId": visitor_id,
                "botId": bot_id
            }, namespace=self.NAMESPACE)
            
            logger.info(f"📤 Joining room with visitorId={visitor_id}, botId={bot_id}")
            
            # Chờ nhận sessionId (timeout 10s)
            joined = self.join_room_event.wait(timeout=10)
            
            if joined and self.session_id:
                logger.info(f"✅ Joined room successfully with sessionId={self.session_id}")
                return True
            else:
                logger.warning(f"⏰ Timeout waiting for joinRoom confirmation")
                return False
            
        except Exception as e:
            logger.error(f"Error joining room: {str(e)}")
            return False
        finally:
            self.join_room_event = None
    
    def send_message(self, visitor_id: str, text: str, language_code: str = "vi") -> Optional[Dict[str, Any]]:
        """
        Gửi tin nhắn đến AI và chờ phản hồi
        
        Args:
            visitor_id: ID của user trong hệ thống
            text: Nội dung tin nhắn
            language_code: Mã ngôn ngữ (vi/en)
        
        Returns: Dict chứa response từ AI hoặc None nếu có lỗi
        """
        try:
            # Đảm bảo đã kết nối và join room
            if not self.is_connected:
                if not self.connect():
                    return None
            
            # Join room và đợi nhận sessionId trước khi gửi tin nhắn
            if not self.join_room(visitor_id):
                logger.error("Cannot send message: Failed to join room or get sessionId")
                return None
            
            # Kiểm tra sessionId trước khi gửi
            if not self.session_id:
                logger.error("Cannot send message: No sessionId available")
                return None
            
            # Reset response data và event
            self.response_data = None
            self.response_event = Event()
            
            # Gửi tin nhắn với sessionId
            self.sio.emit("sendMessageToAI", {
                "visitorId": visitor_id,
                "text": text,
                "languageCode": language_code,
                "sessionId": self.session_id
            }, namespace=self.NAMESPACE)
            
            logger.info(f"📤 Sent message to AI: visitorId={visitor_id}, text={text}")
            
            # Chờ response từ AI
            received = self.response_event.wait(timeout=self.RESPONSE_TIMEOUT)
            
            if received and self.response_data:
                logger.info(f"✅ Received AI response successfully")
                return self.response_data
            else:
                logger.warning(f"⏰ Timeout waiting for AI response")
                return None
                
        except Exception as e:
            logger.error(f"Error sending message to AI: {str(e)}")
            return None
        finally:
            self.response_event = None


# Singleton instance
_buzuai_client = None


def get_buzuai_client() -> BuzuAIClient:
    """
    Lấy singleton instance của BuzuAI client
    """
    global _buzuai_client
    if _buzuai_client is None:
        _buzuai_client = BuzuAIClient()
    return _buzuai_client


def send_message_to_buzuai(user_id: str, message_text: str, language_code: str = "vi") -> Optional[Dict[str, Any]]:
    """
    Helper function để gửi tin nhắn đến BuzuAI
    
    Args:
        user_id: ID của user trong hệ thống
        message_text: Nội dung tin nhắn
        language_code: Mã ngôn ngữ (vi/en)
    
    Returns: Dict chứa response từ AI hoặc None nếu có lỗi
    """
    try:
        client = get_buzuai_client()
        response = client.send_message(user_id, message_text, language_code)
        return response
    except Exception as e:
        logger.error(f"Error in send_message_to_buzuai: {str(e)}")
        return None
