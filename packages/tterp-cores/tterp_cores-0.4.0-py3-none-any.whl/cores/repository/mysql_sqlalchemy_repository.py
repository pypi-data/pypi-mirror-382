import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import and_, asc, case, delete, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from cores.model.paging import PagingDTO


# Define a protocol for entities with soft-delete attributes
class _BaseProtocol:
    id: Any
    deleted_at: Any
    active: Any


Entity = TypeVar("Entity", bound=_BaseProtocol)
Schema = TypeVar("Schema", bound=BaseModel)


class BaseSQLAlchemyRepository(Generic[Entity]):
    """
    A base repository class for SQLAlchemy with flexible soft-delete handling.
    """

    def __init__(self, session: AsyncSession, model: type[Entity]):
        self.session = session
        self.model = model

    def _apply_soft_delete_filter(self, query, with_trash: bool = False) -> Any:
        """Applies soft-delete filters to a query if applicable."""
        if not with_trash:
            if hasattr(self.model, "deleted_at"):
                query = query.where(self.model.deleted_at.is_(None))
            elif hasattr(self.model, "active"):
                query = query.where(self.model.active.is_(True))
        return query

    # --------------------------------------------------------------------------
    # QUERY METHODS (GET/FIND)
    # --------------------------------------------------------------------------

    async def get(
        self,
        id: str | int,
        *,
        options: list[Any] | None = None,
        columns: list[str] | None = None,
        with_trash: bool = False,
    ) -> Entity | None:
        """Gets a single object by its ID."""
        query = select(self.model).where(self.model.id == id)

        if options:
            query = query.options(*options)
        if columns:
            query = query.options(load_only(*[getattr(self.model, col) for col in columns]))

        query = self._apply_soft_delete_filter(query, with_trash)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ids(
        self,
        ids: list[int | str],
        *,
        options: list[Any] | None = None,
        columns: list[str] | None = None,
        with_trash: bool = False,
    ) -> list[Entity]:
        """Gets a list of objects by a list of IDs."""
        query = select(self.model).where(self.model.id.in_(ids))

        if options:
            query = query.options(*options)
        if columns:
            query = query.options(load_only(*[getattr(self.model, col) for col in columns]))

        query = self._apply_soft_delete_filter(query, with_trash)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def find_one_by(
        self,
        *,
        with_trash: bool = False,
        options: list[Any] | None = None,
        **conditions: Any,
    ) -> Entity | None:
        """Finds the first record matching the conditions."""
        query = select(self.model).filter_by(**conditions)

        if options:
            query = query.options(*options)

        query = self._apply_soft_delete_filter(query, with_trash)

        # Debug: Log the query and conditions
        from cores.logger.logging import ApiLogger
        ApiLogger.debug(f"find_one_by query: {query}")
        ApiLogger.debug(f"find_one_by conditions: {conditions}")
        ApiLogger.debug(f"find_one_by model: {self.model}")

        result = await self.session.execute(query.limit(1))
        found_entity = result.scalar_one_or_none()
        ApiLogger.debug(f"find_one_by result: {found_entity}")
        return found_entity

    async def find_all_by(
        self, *, with_trash: bool = False, **conditions: Any
    ) -> list[Entity]:
        """Finds all records matching the conditions."""
        query = select(self.model).filter_by(**conditions)
        query = self._apply_soft_delete_filter(query, with_trash)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_paging_list(
        self,
        paging: PagingDTO,
        options: list[Any] | None = None,
        with_trash: bool = False,
        **conditions: Any,
    ) -> list[Entity]:
        """
        Gets a paginated list of records with sorting and filtering.
        """
        base_query = select(self.model)

        if options:
            base_query = base_query.options(*options)

        base_query = self.apply_filter(base_query, **conditions)
        base_query = self._apply_soft_delete_filter(base_query, with_trash)

        query = self.apply_pagination(paging, base_query)
        query = self.apply_sorting(paging, query)

        return await self.execute_pagination_query(paging, base_query, query)

    def apply_filter(self, base_query, **conditions: Any) -> Any:
        """Applies key-value condition filters to the query."""
        for key, value in conditions.items():
            if value is not None:
                column = getattr(self.model, key, None)
                if column:
                    if isinstance(value, str):
                        base_query = base_query.where(column.ilike(f"%{value}%"))
                    else:
                        base_query = base_query.where(column == value)
        return base_query

    async def execute_pagination_query(
        self, paging: PagingDTO, base_query, query
    ) -> list[Entity]:
        """Executes the query and the count query for pagination."""
        result = await self.session.execute(query)
        entities = list(result.unique().scalars())

        total_query = base_query.with_only_columns(func.count(self.model.id)).order_by(None)
        total_result = await self.session.execute(total_query)
        paging.total = total_result.scalar()
        return entities

    def apply_sorting(self, paging: PagingDTO, query) -> Any:
        """Applies sorting to the query."""
        if hasattr(paging, "order") and hasattr(paging, "sort_by"):
            direction = desc if paging.order == "desc" else asc
            query = query.order_by(direction(getattr(self.model, paging.sort_by)))
        return query

    def apply_pagination(self, paging: PagingDTO, base_query) -> Any:
        """Applies pagination to the query."""
        query = base_query.limit(paging.page_size).offset(
            (paging.page - 1) * paging.page_size
        )
        return query

    # --------------------------------------------------------------------------
    # WRITE METHODS (CREATE/UPDATE/DELETE)
    # --------------------------------------------------------------------------

    async def insert(
        self, data: Entity | BaseModel, with_commit=True, model_validate=True
    ) -> Entity:
        """Inserts a new record."""
        if isinstance(data, BaseModel):
            data = self.model(**data.model_dump())
        self.session.add(data)
        await self.session.flush()
        return data

    def bulk_insert(self, entities: list[Entity]) -> None:
        """Inserts multiple records in bulk."""
        self.session.add_all(entities)

    async def update(self, id: str | int, data_in: Schema | dict[str, Any]) -> bool:
        """Updates a record by its ID."""
        if isinstance(data_in, BaseModel):
            data_dict = data_in.model_dump(exclude_unset=True)
        else:
            data_dict = data_in

        if not data_dict:
            return False

        query = update(self.model).where(self.model.id == id).values(**data_dict)
        result = await self.session.execute(query, execution_options={"synchronize_session": False})
        return result.rowcount > 0

    async def delete(self, id: str | int, is_hard: bool = False) -> bool:
        """Deletes a record by its ID (supports hard and soft delete)."""
        if is_hard:
            query = delete(self.model).where(self.model.id == id)
        elif hasattr(self.model, "deleted_at"):
            query = (
                update(self.model)
                .where(self.model.id == id)
                .values(deleted_at=datetime.datetime.now())
            )
        elif hasattr(self.model, "active"):
            query = (
                update(self.model)
                .where(self.model.id == id)
                .values(active=False)
            )
        else:
            raise ValueError(
                "Model does not support soft delete, and hard delete was not requested."
            )

        result = await self.session.execute(query)
        return result.rowcount > 0

    async def get_or_create(
        self, defaults: dict[str, Any] | None = None, **conditions: Any
    ) -> tuple[Entity, bool]:
        """Finds a record or creates it if it does not exist."""
        defaults = defaults or {}
        instance = await self.find_one_by(**conditions)
        if instance:
            return instance, False
        else:
            instance = self.model(**conditions, **defaults)
            await self.insert(instance, with_commit=False)
            return instance, True

    async def update_or_create(
        self, defaults: dict[str, Any] | None = None, **conditions: Any
    ) -> Entity:
        """Finds a record and updates it, or creates it if it does not exist."""
        defaults = defaults or {}
        instance = await self.find_one_by(**conditions)
        if instance:
            if defaults:
                for key, value in defaults.items():
                    setattr(instance, key, value)
            return instance
        else:
            instance = self.model(**conditions, **defaults)
            return await self.insert(instance)

    # --------------------------------------------------------------------------
    # SPECIALIZED LOGIC
    # --------------------------------------------------------------------------

    async def soft_update(
        self, old_entity: Entity, data_in: Schema | dict[str, Any]
    ) -> Entity:
        """
        "Versioning" logic: Deactivates the old record and creates a new one.
        """
        if hasattr(old_entity, "deleted_at"):
            old_entity.deleted_at = datetime.datetime.now()
        elif hasattr(old_entity, "active"):
            old_entity.active = False
        else:
            raise ValueError("Model does not support soft deactivation for soft_update.")

        if not isinstance(data_in, dict):
            data_in = data_in.model_dump(exclude_none=True)

        update_data = {
            **{
                k: v
                for k, v in old_entity.__dict__.items()
                if k != "_sa_instance_state"
            },
            **data_in,
            "id": None,
            "deleted_at": None,
            "active": True,
        }

        # Clean up keys that might not exist in the new model
        if not hasattr(self.model, "active"):
            update_data.pop("active", None)
        if not hasattr(self.model, "deleted_at"):
            update_data.pop("deleted_at", None)


        new_entity = type(old_entity)(**update_data)
        self.session.add(new_entity)
        await self.session.flush()
        return new_entity

    async def bulk_update(
        self,
        ids: list[int],
        updates: dict[int | str, dict[str, Any]],
        with_commit: bool = True,
    ) -> bool:
        """
        Performs a bulk update using a CASE statement for high efficiency.
        """
        if not updates:
            return False

        if all(not isinstance(v, dict) for v in updates.values()):
            query = (
                update(self.model)
                .where(self.model.id.in_(ids))
                .values(**updates)
            )
            result = await self.session.execute(query)
            return result.rowcount > 0

        all_columns_to_update: set[str] = set()
        for changes in updates.values():
            all_columns_to_update.update(changes.keys())

        values_to_set = {}
        for col_name in all_columns_to_update:
            case_statement = case(
                *(
                    (self.model.id == id_, new_values[col_name])
                    for id_, new_values in updates.items()
                    if col_name in new_values
                ),
                else_=getattr(self.model, col_name),
            )
            values_to_set[col_name] = case_statement

        query = (
            update(self.model)
            .where(self.model.id.in_(ids))
            .values(**values_to_set)
        )
        result = await self.session.execute(query)
        return result.rowcount > 0

    async def delete_by_condition(self, condition: dict, is_hard: bool = False) -> bool:
        """Deletes records based on a condition."""
        query = None
        filters = []

        for key, value in condition.items():
            if isinstance(value, dict):
                for op, val in value.items():
                    if op == "in":
                        filters.append(getattr(self.model, key).in_(val))
            else:
                filters.append(getattr(self.model, key) == value)

        if is_hard:
            query = (
                delete(self.model)
                .where(and_(*filters))
                .execution_options(synchronize_session="fetch")
            )
        elif hasattr(self.model, "deleted_at"):
            query = (
                update(self.model)
                .where(and_(*filters))
                .values(deleted_at=datetime.datetime.now())
                .execution_options(synchronize_session="fetch")
            )
        elif hasattr(self.model, "active"):
            query = (
                update(self.model)
                .where(and_(*filters))
                .values(active=False)
                .execution_options(synchronize_session="fetch")
            )


        if query is None:
            raise ValueError("Cannot delete: Model does not support soft delete.")

        await self.session.execute(query)

        return True
