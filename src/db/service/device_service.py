from src.db.data.device import Device
from src.db.db_connector import DatabaseConnector


class DeviceService:
    def __init__(self):
        self.__connection = DatabaseConnector()
        self.__connection.connect()

    def create(self, entity: Device) -> None:
        entity_dict = entity.to_dict()
        cols = ", ".join(entity_dict.keys())
        vals = [":" + k for k in entity_dict.keys()]
        sql = f"INSERT INTO devices ({cols}) VALUES ({vals});"
        self.__connection.find_all(sql)

    def read(self, _id: int) -> Device | None:
        device = self.__connection.find_one("SELECT * FROM devices WHERE id = ?;", (_id,))
        return Device(**dict(device)) if device is not None else None

    def read_all(self) -> list[Device]:
        devices_rows = self.__connection.find_all("SELECT * FROM devices;")
        return [Device(**dict(row)) for row in devices_rows]

    def update(self, entity: Device) -> Device | None:
        if not self.exists(entity.id):
            return None
        update_sql = "UPDATE devices "
        set_strs = []
        entity_as_dict = entity.to_dict()
        for k in entity_as_dict.keys():
            if k == 'id':
                continue
            set_strs.append(f"SET {k} = :{k}")
        update_sql += ", ".join(set_strs)
        update_sql += " WHERE id = :id"
        self.__connection.find_one(update_sql, entity_as_dict)
        return entity

    def delete(self, _id: int) -> None:
        if not self.exists(_id):
            return
        self.__connection.find_one("DELETE FROM devices WHERE id = ?;", _id)

    def exists(self, _id: int) -> bool:
        return self.__connection.find_one("SELECT * FROM devices WHERE id = ?;", (_id,)) is not None