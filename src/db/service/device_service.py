from src.db.service.user_service import UserService
from src.db.service.entity_service import EntityService
from src.db.data.device import Device


class DeviceService(EntityService):
    def __init__(self):
        super().__init__("devices", Device)

    def create(self, entity: Device) -> None:
        self.validate(entity)
        super().create(entity)

    def read(self, _id: int) -> Device | None:
        return super().read(_id)

    def read_all(self) -> list[Device]:
        return super().read_all()

    def update(self, entity: Device) -> Device | None:
        return super().update(entity)

    @staticmethod
    def validate(device: Device) -> bool:
        return device.owned_by is None or UserService().exists(device.owned_by)
