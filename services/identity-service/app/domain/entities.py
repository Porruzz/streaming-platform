# app/domain/entities.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Entity:
    id: str
