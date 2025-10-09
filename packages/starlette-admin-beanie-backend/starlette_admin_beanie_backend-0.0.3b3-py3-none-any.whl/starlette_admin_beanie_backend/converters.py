import enum
import inspect
from typing import Any, Sequence, Type, get_args, get_origin
from uuid import UUID

import bson
import pydantic
from beanie import Document, PydanticObjectId, Link, BackLink
from pydantic import Field, SecretStr, AwareDatetime, NaiveDatetime, FutureDatetime, PastDatetime, PastDate, FutureDate, \
    BaseModel
from starlette_admin import BaseField, StringField, IntegerField, DecimalField, EmailField, URLField, HasOne, HasMany, \
    PasswordField, DateTimeField, CollectionField, ListField
from starlette_admin.converters import StandardModelConverter, converts
from starlette_admin.exceptions import NotSupportedAnnotation as BaseNotSupportedAnnotation
from starlette_admin.helpers import slugify_class_name

from .exceptions import NotSupportedAnnotation


class BaseODMModelConverter(StandardModelConverter):
    def get_type(self, model: Document, value: Any) -> Any:
        if isinstance(value, str) and (hasattr(model, value) or value in model.model_fields):
            return model.model_fields[value].annotation
        raise ValueError(f"Can't find attribute with key {value}")

    def convert_fields_list(
            self, *, fields: Sequence[Any], model: Type[Document], **kwargs: Any
    ) -> Sequence[BaseField]:
        fields = [v for v in fields]
        try:
            return super().convert_fields_list(fields=fields, model=model, **kwargs)
        except BaseNotSupportedAnnotation as e:
            raise NotSupportedAnnotation(*e.args) from e


class ModelConverter(BaseODMModelConverter):
    @converts(Field)
    def conv_field(self, *args: Any, **kwargs: Any) -> BaseField:
        _type = kwargs.get("type")
        kwargs.update(
            {
                "type": _type.pydantic_field.annotation,
                "required": _type.is_required_in_doc() and not _type.primary_field,
            }
        )
        return self.convert(*args, **kwargs)

    @converts(list)
    def conv_standard_list(self, *args: Any, **kwargs: Any) -> BaseField:
        self._ensure_get_args_is_not_null(*args, **kwargs)
        _type = kwargs.get("type")
        subtypes = get_args(_type)
        subtype = subtypes[0] if len(subtypes) > 0 else str
        if subtype.__name__ == "Link":
            models = get_args(subtype)
            model = models[0] if len(models) > 0 else str
            return HasMany(
                **self._standard_type_common(*args, **kwargs),
                identity=slugify_class_name(model.__name__)
            )

        if inspect.isclass(subtype) and issubclass(subtype, enum.Enum):
            kwargs.update({"type": subtype, "multiple": True})
            return self.convert(*args, **kwargs)

        kwargs.update({"type": subtype})
        return ListField(required=kwargs.get("required", True), field=self.convert(*args, **kwargs))

    @converts(Link)
    def conv_link(self, *args: Any, **kwargs: Any) -> BaseField:
        _type: Link = kwargs.get("type")
        field_name = kwargs.get("name")
        model: Document = kwargs.get("model")
        # get the model type from the Link field
        link_model_type = get_args(_type)[0]
        # check if this is a list of links
        if get_origin(model.model_fields.get(field_name).annotation) is list:
            return HasMany(
                **self._standard_type_common(*args, **kwargs),
                identity=slugify_class_name(link_model_type.__name__)
            )

        return HasOne(
            **self._standard_type_common(*args, **kwargs),
            identity=slugify_class_name(link_model_type.__name__)
        )

    @converts(BaseModel)
    def conv_model(self, *args: Any, **kwargs: Any) -> BaseField:
        _type: BaseModel = kwargs.get("type")
        standard_type_common = self._standard_type_common(*args, **kwargs)
        sub_fields = []
        for field_name, field in _type.model_fields.items():
            kwargs.update({"name": field_name, "type": field.annotation, "required": field.is_required()})
            sub_fields.append(self.convert(*args, **kwargs))
        return CollectionField(**standard_type_common, fields=sub_fields)

    @converts(bson.ObjectId, bson.Regex, bson.Binary, pydantic.NameEmail, PydanticObjectId, UUID, BackLink)
    def conv_bson_string(self, *args: Any, **kwargs: Any) -> BaseField:
        return StringField(**self._standard_type_common(*args, **kwargs))

    @converts(bson.Int64)
    def conv_bson_int64(self, *args: Any, **kwargs: Any) -> BaseField:
        return IntegerField(**self._standard_type_common(*args, **kwargs))

    @converts(bson.Decimal128)
    def conv_bson_decimal(self, *args: Any, **kwargs: Any) -> BaseField:
        return DecimalField(**self._standard_type_common(*args, **kwargs))

    @converts(pydantic.EmailStr)
    def conv_pydantic_email(self, *args: Any, **kwargs: Any) -> BaseField:
        return EmailField(**self._standard_type_common(*args, **kwargs))

    @converts(pydantic.AnyUrl)
    def conv_pydantic_url(self, *args: Any, **kwargs: Any) -> BaseField:
        return URLField(**self._standard_type_common(*args, **kwargs))

    @converts(SecretStr)
    def conv_secret_str(self, *args: Any, **kwargs: Any) -> BaseField:
        return PasswordField(**self._standard_type_common(*args, **kwargs))

    @converts(AwareDatetime, NaiveDatetime, FutureDatetime, PastDatetime, PastDate, FutureDate)
    def conv_aware_datetime(self, *args: Any, **kwargs: Any) -> BaseField:
        return DateTimeField(**self._standard_type_common(*args, **kwargs))
