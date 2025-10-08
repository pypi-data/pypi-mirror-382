"""
BuzuAI Python Client Library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A Python client library for interacting with BuzuAI chat system via Socket.IO.

Basic usage:

    >>> from buzuai import get_buzuai_client, send_message_to_buzuai
    >>> 
    >>> # Cách 1: Sử dụng helper function
    >>> response = send_message_to_buzuai("user_123", "Xin chào")
    >>> print(response)
    >>> 
    >>> # Cách 2: Sử dụng client trực tiếp
    >>> client = get_buzuai_client()
    >>> client.connect()
    >>> client.join_room("user_123")
    >>> response = client.send_message("user_123", "Xin chào")

"""

from .client import BuzuAIClient, get_buzuai_client, send_message_to_buzuai

__version__ = "0.1.0"
__all__ = ["BuzuAIClient", "get_buzuai_client", "send_message_to_buzuai"]
