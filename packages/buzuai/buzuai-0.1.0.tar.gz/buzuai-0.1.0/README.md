# BuzuAI Python Client

[![Python Version](https://img.shields.io/pypi/pyversions/buzuai)](https://pypi.org/project/buzuai/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Thư viện Python client để giao tiếp với hệ thống AI của BuzuAI qua Socket.IO.

## 🚀 Tính năng

- ✅ Kết nối real-time qua Socket.IO
- 🔄 Singleton pattern - tái sử dụng kết nối
- 📝 Logging tự động với emoji
- ⏱️ Chờ response từ AI (timeout 300s)
- 🎯 API đơn giản, dễ sử dụng
- 🐍 Hỗ trợ Python 3.7+
- 📦 Chuẩn PyPI, dễ dàng cài đặt

## 📦 Cài đặt

```bash
pip install buzuai
```

Hoặc cài đặt từ source:

```bash
git clone https://github.com/Luisnguyen1/buzuai.git
cd buzuai
pip install -e .
```

## 🎯 Sử dụng cơ bản

### Cách 1: Helper function (Đơn giản nhất)

```python
from buzuai import send_message_to_buzuai

# Gửi tin nhắn và nhận response
response = send_message_to_buzuai(
    user_id="user_123",
    message_text="Xin chào, bạn khỏe không?",
    language_code="vi"
)

if response:
    print("AI trả lời:", response)
else:
    print("Không nhận được response")
```

### Cách 2: Sử dụng client singleton

```python
from buzuai import get_buzuai_client

# Lấy client instance (singleton)
client = get_buzuai_client()

# Kết nối
if client.connect():
    print("✅ Đã kết nối")
    
    # Join room
    client.join_room("user_123")
    
    # Gửi tin nhắn và chờ response
    response = client.send_message(
        visitor_id="user_123",
        text="Hôm nay thời tiết thế nào?",
        language_code="vi"
    )
    
    if response:
        print("💬 AI:", response)
    
    # Ngắt kết nối
    client.disconnect()
```

### Cách 3: Tạo instance mới

```python
from buzuai import BuzuAIClient

# Tạo client instance mới
client = BuzuAIClient()

# Kết nối và sử dụng
if client.connect():
    response = client.send_message(
        visitor_id="user_123",
        text="Xin chào",
        language_code="vi"
    )
    print(response)
    client.disconnect()
```

### Ví dụ đầy đủ với logging

```python
from buzuai import get_buzuai_client
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Lấy client
client = get_buzuai_client()

# Kết nối
if not client.connect():
    print("❌ Không thể kết nối")
    exit(1)

print("✅ Đã kết nối thành công!")

# Gửi nhiều tin nhắn
questions = [
    "Xin chào!",
    "Bạn có thể giúp gì cho tôi?",
    "Hôm nay thời tiết thế nào?",
]

for question in questions:
    print(f"\n📤 Hỏi: {question}")
    response = client.send_message(
        visitor_id="user_123",
        text=question,
        language_code="vi"
    )
    
    if response:
        # Response có thể chứa: text, type, content, etc.
        text = response.get("text", response.get("content", ""))
        print(f"💬 AI: {text}")
    else:
        print("⚠️ Không nhận được response")

# Ngắt kết nối
client.disconnect()
print("👋 Đã ngắt kết nối")
```

## 📖 API Reference

### Helper Functions

#### `send_message_to_buzuai(user_id, message_text, language_code="vi")`

Helper function đơn giản nhất để gửi tin nhắn.

**Tham số:**
- `user_id` (str): ID của user
- `message_text` (str): Nội dung tin nhắn
- `language_code` (str): Mã ngôn ngữ (mặc định: "vi")

**Returns:** `Dict[str, Any]` hoặc `None`

**Ví dụ:**
```python
response = send_message_to_buzuai("user_123", "Xin chào")
```

#### `get_buzuai_client()`

Lấy singleton instance của BuzuAI client.

**Returns:** `BuzuAIClient`

**Ví dụ:**
```python
client = get_buzuai_client()
```

### `BuzuAIClient` Class

#### Constructor

```python
BuzuAIClient()
```

Không cần tham số. Sử dụng singleton pattern.

#### Methods

##### `connect() -> bool`

Kết nối đến BuzuAI server.

**Returns:** `True` nếu kết nối thành công

**Ví dụ:**
```python
if client.connect():
    print("Đã kết nối")
```

##### `join_room(visitor_id, bot_id=None) -> bool`

Join vào room chat với bot.

**Tham số:**
- `visitor_id` (str): ID của user
- `bot_id` (str, optional): ID của bot (mặc định: DEFAULT_BOT_ID)

**Returns:** `True` nếu join thành công

**Ví dụ:**
```python
client.join_room("user_123")
```

##### `send_message(visitor_id, text, language_code="vi") -> Optional[Dict[str, Any]]`

Gửi tin nhắn đến AI và chờ phản hồi.

**Tham số:**
- `visitor_id` (str): ID của user
- `text` (str): Nội dung tin nhắn
- `language_code` (str): Mã ngôn ngữ (mặc định: "vi")

**Returns:** Dict chứa response từ AI hoặc None nếu timeout/lỗi

**Ví dụ:**
```python
response = client.send_message("user_123", "Xin chào")
```

##### `disconnect()`

Ngắt kết nối khỏi server.

**Ví dụ:**
```python
client.disconnect()
```

#### Properties

##### `is_connected`

Kiểm tra trạng thái kết nối.

**Returns:** `bool`

**Ví dụ:**
```python
if client.is_connected:
    print("Đang kết nối")
```

#### Constants

- `DEFAULT_BOT_ID`: "4489b201-a08a-4d87-81e1-632bcbdb44a8"
- `BUZUAI_URL`: "https://api.buzuai.com/app-chat"
- `NAMESPACE`: "/app-chat"
- `RESPONSE_TIMEOUT`: 300 (seconds)

## 🔧 Cấu hình Logging

```python
import logging

# Bật logging với level INFO
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Sử dụng client - logging sẽ tự động hoạt động
from buzuai import get_buzuai_client
client = get_buzuai_client()
```

## 🔍 Các sự kiện Socket.IO

Thư viện tự động xử lý các sự kiện sau:

**Outgoing (Gửi đi):**
- `joinRoom` - Join vào room chat
- `sendMessageToAI` - Gửi tin nhắn đến AI

**Incoming (Nhận về):**
- `connect` - Khi kết nối thành công
- `disconnect` - Khi bị ngắt kết nối
- `receiveMessage` - Nhận response từ AI
- `receiveNotification` - Nhận thông báo từ hệ thống

## 🐛 Troubleshooting

### Không nhận được response

**Nguyên nhân:**
- Timeout (mặc định 300 giây)
- Bot đang bận
- Lỗi kết nối

**Giải pháp:**
```python
response = client.send_message(user_id, "test")
if response is None:
    print("Không nhận được response - thử lại")
```

### Không kết nối được

**Kiểm tra:**
```python
client = get_buzuai_client()
if not client.connect():
    print("Lỗi kết nối - kiểm tra internet")
```

### Bật debug logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## � Ví dụ (Examples)

Thư viện đi kèm 3 file ví dụ:

### 1. `example_simple.py` - Đơn giản nhất
Sử dụng helper function để gửi 1 tin nhắn:
```bash
python example_simple.py
```

### 2. `example_multiple.py` - Gửi nhiều tin nhắn
Sử dụng client để gửi nhiều câu hỏi:
```bash
python example_multiple.py
```

### 3. `example_interactive.py` - Chế độ chat
Chat tương tác với AI như terminal chat:
```bash
python example_interactive.py
```

## 📋 Requirements

- Python >= 3.7
- python-socketio[client] >= 5.0.0

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **GitHub**: https://github.com/Luisnguyen1/buzuai
- **Issues**: https://github.com/Luisnguyen1/buzuai/issues
- **Homepage**: https://buzuai.com

## 📞 Support

Nếu bạn gặp vấn đề hoặc có câu hỏi:
- Mở issue trên GitHub: https://github.com/Luisnguyen1/buzuai/issues
- Email: support@buzuai.com

---

**Version:** 0.1.0  
**Python:** 3.7+  
Made with ❤️ by BuzuAI Team