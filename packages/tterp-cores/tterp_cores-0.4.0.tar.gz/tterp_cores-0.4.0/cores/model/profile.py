from typing import Any

from pydantic import BaseModel


class Profile(BaseModel):
    id: int
    gender: int | None
    user_id: int
    full_name: str
    state: str
    user_dep_pos: list[Any] = []
    user_dep_pos: list[Any] = []


# Example usage
data = [
    {
        "id": 49,
        "gender": 1,
        "user_id": 266,
        "full_name": "LÊ CÔNG TIẾN",
        "state": "ACTIVE",
        "pro_dep_pos": [
            {
                "updated_at": "2024-10-12T06:06:39",
                "deleted_at": None,
                "id": 86,
                "dep_id": 29,
                "expertise_id": None,
                "label": "",
                "is_primary": True,
                "created_at": "2024-10-12T06:06:39",
                "pro_id": 49,
                "pos_id": 31,
                "appointment_date": None,
                "expire_date": None,
                "active": True,
                "department": {
                    "updated_at": "2023-12-06T08:40:21",
                    "note": None,
                    "created_at": "2023-12-06T08:40:21",
                    "parent_id": None,
                    "deleted_at": None,
                    "id": 29,
                    "name": "Phòng Công nghệ Thông tin",
                    "manager_id": None,
                    "address": None,
                    "phone": None,
                    "parent": None,
                },
                "position": {"id": 31, "name": "Phó phòng"},
                "expertise": None,
            },
            {
                "updated_at": "2024-10-15T11:22:29",
                "deleted_at": None,
                "id": 1819,
                "dep_id": 1,
                "expertise_id": None,
                "label": None,
                "is_primary": False,
                "created_at": "2024-10-15T11:22:29",
                "pro_id": 49,
                "pos_id": 1,
                "appointment_date": None,
                "expire_date": None,
                "active": True,
                "department": {
                    "updated_at": "2023-12-06T08:38:33",
                    "note": None,
                    "created_at": "2023-12-06T08:38:33",
                    "parent_id": None,
                    "deleted_at": None,
                    "id": 1,
                    "name": "default",
                    "manager_id": None,
                    "address": None,
                    "phone": None,
                    "parent": None,
                },
                "position": {"id": 1, "name": "default"},
                "expertise": None,
            },
        ],
    }
]

# parsed_data = [User(**user) for user in data]
# print(parsed_data)
