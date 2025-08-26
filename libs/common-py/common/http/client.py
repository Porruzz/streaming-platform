# libs/common-py/common/http/client.py
import httpx
from typing import Callable, Optional

def client(timeout=10.0) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=timeout)
