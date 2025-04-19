from dataclasses import dataclass

from src.db.data.entity import Entity


@dataclass
class User(Entity):
    name: str | None
