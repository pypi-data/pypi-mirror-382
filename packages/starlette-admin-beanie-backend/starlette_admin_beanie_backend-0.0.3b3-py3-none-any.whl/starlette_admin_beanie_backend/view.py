from typing import List, Any, Optional, Dict, Sequence, Union, Type

from beanie import Document, PydanticObjectId
from beanie.odm.operators.find.comparison import In
from pydantic import ValidationError
from starlette.requests import Request
from starlette_admin import BaseField, CollectionField, ListField, HasOne, HasMany

from starlette_admin.helpers import prettify_class_name, slugify_class_name, pydantic_error_to_form_validation_errors
from starlette_admin.views import BaseModelView

from .converters import ModelConverter
from .helpers import normalize_list, resolve_deep_query, resolve_proxy


class ModelView(BaseModelView):
    def __init__(
            self,
            model: Type[Document],
            icon: Optional[str] = None,
            name: Optional[str] = None,
            label: Optional[str] = None,
            identity: Optional[str] = None,
            converter: Optional[ModelConverter] = None
    ):
        self.model = model

        self.icon = icon
        self.name = name or self.name or prettify_class_name(self.model.__name__)
        self.label = label or self.label or prettify_class_name(self.model.__name__) + "s"
        self.identity = identity or self.identity or slugify_class_name(self.model.__name__)

        self.pk_attr = "id"

        # Define Fields
        if self.fields is None or len(self.fields) == 0:
            _all_list = list(model.model_fields.keys())
            self.fields = [f for f in _all_list if f != "revision_id"]
        # Convert Fields
        self.fields = (converter or ModelConverter()).convert_fields_list(
            fields=self.fields, model=self.model
        )

        self.exclude_fields_from_list = normalize_list(self.exclude_fields_from_list)
        self.exclude_fields_from_detail = normalize_list(self.exclude_fields_from_detail)
        self.exclude_fields_from_create = normalize_list(self.exclude_fields_from_create)
        self.exclude_fields_from_edit = normalize_list(self.exclude_fields_from_edit)
        self.searchable_fields = normalize_list(self.searchable_fields)
        self.sortable_fields = normalize_list(self.sortable_fields)
        self.export_fields = normalize_list(self.export_fields)
        self.fields_default_sort = normalize_list(
            self.fields_default_sort, is_default_sort_list=True
        )

        super().__init__()

    async def find_all(
            self,
            request: Request,
            skip: int = 0,
            limit: int = 100,
            where: Union[Dict[str, Any], str, None] = None,
            order_by: Optional[List[str]] = None
    ) -> Sequence[Any]:
        q = await self._build_query(request, where)
        o = await self._build_order_clauses([] if order_by is None else order_by)
        return await (
            self
            .model
            .find(q, fetch_links=True, nesting_depth=1, sort=o, skip=skip, limit=limit)
            .to_list()
        )

    async def count(self, request: Request, where: Union[Dict[str, Any], str, None] = None) -> int:
        if where is None:
            return await self.model.get_pymongo_collection().estimated_document_count()

        q = await self._build_query(request, where)
        return await self.model.get_pymongo_collection().count_documents(q)

    async def find_by_pk(self, request: Request, pk: Any) -> Any:
        return await self.model.get(pk, fetch_links=True)

    async def find_by_pks(self, request: Request, pks: List[Any]) -> Sequence[Any]:
        pks = list(map(PydanticObjectId, pks))
        return await self.model.find(In(self.model.id, pks)).to_list()

    async def create(self, request: Request, data: Dict) -> Any:
        arranged_data = await self._arrange_data(request, data)
        for k, v in arranged_data.items():
            data[k] = v
        try:
            obj = self.model(**data)
            await self.before_create(request, data, obj)
            # Create a new document
            await obj.create()
            await self.after_create(request, obj)
            return obj
        except Exception as e:
            self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: Dict[str, Any]) -> Any:
        arranged_data = await self._arrange_data(request, data, is_edit=True)
        for k, v in arranged_data.items():
            data[k] = v
        try:
            obj = await self.find_by_pk(request, pk)
            await obj.set(data)
            await self.before_edit(request, data, obj)
            # Save the changes
            await self.model.save(obj)
            await self.after_edit(request, obj)
            return obj
        except Exception as e:
            self.handle_exception(e)

    async def delete(self, request: Request, pks: List[Any]) -> Optional[int]:
        objs = self.model.find(In(self.model.id, [PydanticObjectId(pk) for pk in pks]))
        objs_list = await objs.to_list()
        for obj in objs_list:
            await self.before_delete(request, obj)
        # Delete documents
        deleted = await objs.delete()
        for obj in objs_list:
            await self.after_delete(request, obj)
        return deleted.deleted_count

    @staticmethod
    def handle_exception(exc: Exception) -> None:
        print(exc)
        if isinstance(exc, ValidationError):
            raise pydantic_error_to_form_validation_errors(exc)
        raise exc

    async def _arrange_data(
            self,
            request: Request,
            data: Dict[str, Any],
            is_edit: bool = False,
            fields: Optional[Sequence[BaseField]] = None,
    ) -> Dict[str, Any]:
        arranged_data: Dict[str, Any] = {}
        if fields is None:
            fields = self.get_fields_list(request, request.state.action)
        for field in fields:
            name, value = field.name, data.get(field.name, {})
            if isinstance(field, CollectionField) and value is not None:
                arranged_data[name] = await self._arrange_data(
                    request,
                    value,
                    is_edit,
                    field.get_fields_list(request, request.state.action),
                )
            elif (
                    isinstance(field, ListField)
                    and isinstance(field.field, CollectionField)
                    and value is not None
            ):
                arranged_data[name] = [
                    await self._arrange_data(
                        request,
                        v,
                        is_edit,
                        field.field.get_fields_list(request, request.state.action),
                    )
                    for v in value
                ]
            elif isinstance(field, HasOne) and value is not None:
                foreign_model = self._find_foreign_model(field.identity)
                arranged_data[name] = await foreign_model.find_by_pk(request, value)
            elif isinstance(field, HasMany) and value is not None:
                foreign_model = self._find_foreign_model(field.identity)
                arranged_data[name] = [await foreign_model.find_by_pk(request, v) for v in value]
            else:
                arranged_data[name] = value
        return arranged_data

    async def _build_query(self, _: Request, where: Union[Dict[str, Any], str, None] = None) -> Any:
        if where is None:
            return {}
        if isinstance(where, dict):
            return resolve_deep_query(where, self.model)
        return {}

    async def _build_order_clauses(self, order_list: List[str]) -> Any:
        clauses = []
        for value in order_list:
            key, order = value.strip().split(maxsplit=1)
            clause = resolve_proxy(self.model, key)
            if clause is not None:
                clauses.append(f"{'+' if order.lower() == 'asc' else '-'}{clause}")
        return clauses
