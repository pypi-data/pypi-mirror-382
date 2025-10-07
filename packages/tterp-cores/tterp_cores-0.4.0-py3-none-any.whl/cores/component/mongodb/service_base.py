from abc import abstractmethod
from datetime import datetime

# from cores.component.mongodb.database import database, client
import motor.motor_asyncio
from bson.objectid import ObjectId
from fastapi.encoders import jsonable_encoder
from settings import (
    MONGODB_AUTHENTICATION_DATABASE,
    MONGODB_DATABASE,
    MONGODB_HOST,
    MONGODB_PASSWORD,
    MONGODB_PORT,
    MONGODB_USERNAME,
)

from cores.schemas.sche_base import MetadataSchema

from .service_base_contract import ServiceBaseContract

mongouri = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DATABASE}?authSource={MONGODB_AUTHENTICATION_DATABASE}"

# client = motor.motor_asyncio.AsyncIOMotorClient(mongouri)
# database = getattr(client, MONGODB_DATABASE)


class ServiceBase(ServiceBaseContract):
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongouri)
        self.database = getattr(self.client, MONGODB_DATABASE)

    def convert_data(self, data):
        if data:
            data["id"] = str(data["_id"])
            del data["_id"]
        return data

    async def paginate(
        self,
        pagination_params,
        query: dict = {},
        with_trash: bool = False,
        sort_by: dict = None,
        direction=None,
    ):
        page = pagination_params.page
        size = pagination_params.page_size
        objs = []
        data = (
            self.collection.find(query).skip(size * (page - 1)).limit(size)
        )
        if sort_by and direction:
            data.sort(sort_by, direction)
        total = await self.collection.count_documents(query)
        async for obj in data:
            objs.append(self.convert_data(obj))
        metadata = MetadataSchema(
            current_page=page, page_size=size, total_items=total
        )
        return {
            "code": 200,
            "data": objs,
            "metadata": jsonable_encoder(metadata),
        }

    async def get_all(self):
        objs = []
        async for obj in self.collection.find():
            objs.append(self.convert_data(obj))
        return objs

    async def create(self, data: object, with_timestamp=True) -> dict:
        data = jsonable_encoder(data)
        if with_timestamp:
            data["created_at"] = data["updated_at"] = datetime.now()
        obj = await self.collection.insert_one(data)
        new_obj = await self.collection.find_one({"_id": obj.inserted_id})
        new_obj = self.convert_data(new_obj)
        return new_obj

    async def find(self, id: str) -> dict:
        obj = await self.collection.find_one(
            {"_id": ObjectId(id), "deleted_at": None}
        )
        return self.convert_data(obj)

    async def search(
        self, name: str, is_absolute: bool = True, is_get_first: bool = True
    ):
        q_collection = self.collection
        if is_get_first:
            if is_absolute:
                return self.convert_data(
                    await q_collection.find_one(
                        {"name": name, "deleted_at": None}
                    )
                )
            else:
                async for obj in q_collection.find(
                    {
                        "name": {"$regex": name, "$options": "i"},
                        "deleted_at": None,
                    }
                ):
                    return self.convert_data(obj)
        else:
            if is_absolute:
                objs = []
                async for obj in q_collection.find(
                    {"name": name, "deleted_at": None}
                ):
                    objs.append(self.convert_data(obj))
                return objs
            else:
                objs = []
                async for obj in q_collection.find(
                    {
                        "name": {"$regex": name, "$options": "i"},
                        "deleted_at": None,
                    }
                ):
                    objs.append(self.convert_data(obj))
                return objs

    async def update(self, id: str, data: object) -> dict:
        data = jsonable_encoder(data)
        q_obj = self.collection
        if q_obj.find_one({"_id": ObjectId(id), "deleted_at": None}):
            updated_obj = await q_obj.update_one(
                {"_id": ObjectId(id)}, {"$set": data}
            )
            if updated_obj:
                return self.convert_data(
                    await q_obj.find_one({"_id": ObjectId(id)})
                )
        return False

    async def delete(self, id: str, is_hard_delete=False) -> dict:
        q_obj = self.collection
        if await q_obj.find_one({"_id": ObjectId(id), "deleted_at": None}):
            if is_hard_delete:
                deleted_obj = q_obj.delete_one({"_id": ObjectId(id)})
            else:
                deleted_obj = await q_obj.update_one(
                    {"_id": ObjectId(id)},
                    {"$set": {"deleted_at": datetime.now()}},
                )
            if deleted_obj:
                return True
                # return self.convert_data(await q_obj.find_one({'_id':
                # ObjectId(id)})
        return False

    @abstractmethod
    def set_collection(self, collection):
        self.collection = collection

    @abstractmethod
    def set_collection_helper(self, data):
        self.collection_helper = data
