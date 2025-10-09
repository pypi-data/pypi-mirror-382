import typing as t

from beanie import Document
from beanie.odm.operators.find import comparison as c, evaluation as e, logical as l
from pydantic import Field


def normalize_list(
        arr: t.Optional[t.Sequence[t.Any]], is_default_sort_list: bool = False
) -> t.Optional[t.Sequence[str]]:
    if arr is None:
        return None
    _new_list = []
    for v in arr:
        if isinstance(v, str):
            _new_list.append(v)
        elif (
                isinstance(v, tuple) and is_default_sort_list
        ):  # Support for fields_default_sort:
            if len(v) == 2 and isinstance(v[0], str) and isinstance(v[1], bool):
                _new_list.append((v[0], v[1]))
            else:
                raise ValueError(
                    "Invalid argument, Expected Tuple[str, bool]"
                )
        else:
            raise ValueError(f"Expected str, got {type(v).__name__}")
    return _new_list


def resolve_deep_query(
        where: t.Dict[str, t.Any],
        model: t.Type[Document],
        logic=None
) -> t.Any:
    queries = []
    if isinstance(where, list):
        for item in where:
            queries.append(resolve_deep_query(item, model))
    else:
        for k, v in where.items():
            if k == "and":
                queries = resolve_deep_query(v, model, k)
            elif k == "or":
                queries = resolve_deep_query(v, model, k)
            else:
                for op, val in v.items():
                    match op:
                        case "eq":
                            return c.Eq(k, val)
                        case "neq":
                            return c.NE(k, val)
                        case "lt":
                            return c.LT(k, val)
                        case "gt":
                            return c.GT(k, val)
                        case "le":
                            return c.LTE(k, val)
                        case "ge":
                            return c.GTE(k, val)
                        case "in":
                            return c.In(k, val)
                        case "not_in":
                            return c.NotIn(k, val)
                        case "startswith":
                            return e.RegEx(k, f"^{val}", "i")
                        case "not_startswith":
                            return l.Not(e.RegEx(k, f"^{val}", "i"))
                        case "endswith":
                            return e.RegEx(k, f"{val}$", "i")
                        case "not_endswith":
                            return l.Not(e.RegEx(k, f"{val}$", "i"))
                        case "contains":
                            return e.RegEx(k, f"{val}", "i")
                        case "not_contains":
                            return l.Not(e.RegEx(k, f"{val}", "i"))
                        case "is_false":
                            return c.Eq(k, False)
                        case "is_true":
                            return c.Eq(k, True)
                        case "is_null":
                            return c.Eq(k, None)
                        case "is_not_null":
                            return c.NE(k, None)
                        case "between":
                            return l.And(k >= val[0], k <= val[1])
                        case "not_between":
                            return l.Or(k < val[0], k > val[1])
    if logic:
        if logic == "or":
            return {"$or": queries}
        else:
            return {"$and": queries}
    return queries


def resolve_proxy(model: t.Type[Document], proxy_name: str) -> t.Optional[Field]:
    _list = proxy_name.split(".")
    m = model
    for v in _list:
        if m is not None:
            m = getattr(m, v, None)  # type: ignore
    return m  # type: ignore[return-value]


# Dynamically create Pydantic model for projection
# def generate_projection_schema(base_model: t.Type[Document], exclude_fields: t.Sequence[str]):
#     fields = {}
#
#     for name, model_field in base_model.model_fields.items():
#         if name in exclude_fields or name == "revision_id":
#             continue
#
#         # Handle default values or required marker
#         default = model_field.default if model_field.default is not None else ...
#         annotation = model_field.annotation
#
#         alias = model_field.alias
#
#         # Keep alias if used
#         if alias != name:
#             field_info = FieldInfo(default=default, validation_alias=alias)
#         else:
#             field_info = FieldInfo(default=default)
#
#         fields[name] = (annotation, field_info)
#
#     projection_model = create_model(f"{base_model.__name__}ProjectionSchema", **fields)
#
#     # Add __admin_select2_repr__ attribute if present in the Original Model
#     try:
#         html_repr_method = getattr(
#             base_model,
#             "__admin_select2_repr__",
#         )
#         setattr(projection_model, "__admin_select2_repr__", html_repr_method)
#     except Exception:  # noqa
#         pass
#     return projection_model
