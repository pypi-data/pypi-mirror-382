from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection
from pymongo.database import Database

from cores.config import database_config, service_config

# Thông số kết nối MongoDB
MONGO_URI = (
    f"mongodb://{database_config.MONGODB_USERNAME}:{database_config.MONGODB_PASSWORD}@"
    f"{database_config.MONGODB_HOST}:{database_config.MONGODB_PORT}/"
    f"{database_config.MONGODB_DATABASE}?authSource="
    f"{database_config.MONGODB_AUTHENTICATION_DATABASE}"
)

DATABASE_NAME = database_config.MONGODB_DATABASE

def get_mongo_uri() -> str:
    return MONGO_URI  # hoặc lấy từ config


def get_mongo_database_name() -> str:
    return DATABASE_NAME


# # Khởi tạo client và database
# client: Optional[AsyncIOMotorClient] = None
# db: Optional[Database] = None


def get_mongodb():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]
    return db


def get_test_mongodb():
    if service_config.APP_ENV == "local":
        uri = (
            f"mongodb://{database_config.MONGODB_USERNAME}:"
            f"{database_config.MONGODB_PASSWORD}@"
            f"{database_config.MONGODB_HOST}:{database_config.MONGODB_PORT}/"
            f"test_{database_config.MONGODB_DATABASE}?authSource="
            f"{database_config.MONGODB_AUTHENTICATION_DATABASE}"
        )
    else:
        uri = (
            f"mongodb://{database_config.MONGODB_HOST}:"
            f"{database_config.MONGODB_PORT}/"
            f"test_{database_config.MONGODB_DATABASE}"
        )
    client = AsyncIOMotorClient(uri)
    db = client[f"test_{database_config.MONGODB_DATABASE}"]
    return db


def get_collection(
    db: Database,
    collection_name: str,
) -> Collection:
    """Lấy một collection từ database."""
    return db[collection_name]
