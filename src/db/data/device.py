from dataclasses import dataclass

from src.db.data.entity import Entity
from src.db.service.user_service import UserService
from src.db.data.user import User


@dataclass
class Device(Entity):
    device_name: str
    owned_by: int | None

    def get_owned_by_user(self) -> User | None:
        return UserService().read(self.owned_by) if self.owned_by is not None else None
