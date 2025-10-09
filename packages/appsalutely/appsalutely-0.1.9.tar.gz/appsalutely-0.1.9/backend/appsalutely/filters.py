from enum import StrEnum
from typing import Annotated, Callable, Self, TypeVar, Any, Generic

from fastapi import HTTPException, status, Query, Depends
from pydantic import BaseModel, ValidationError, Json
import pydantic
from tortoise import Model
from tortoise.fields import Field
from tortoise.fields.data import IntEnumFieldInstance
from tortoise.fields.relational import ForeignKeyFieldInstance, ManyToManyFieldInstance
from tortoise.queryset import QuerySet

T = TypeVar("T", bound=Model)


class Operation(StrEnum):
    """
    Enum representing the operations that can be used in filters.
    """

    # https://tortoise.github.io/query.html#filtering
    EQ = "eq"
    NE = "ne"
    IN = "in"
    NOT_IN = "not_in"
    GTE = "gte"
    GT = "gt"
    LTE = "lte"
    LT = "lt"
    RANGE = "range"
    ISNULL = "isnull"
    NOT_ISNULL = "not_isnull"
    CONTAINS = "contains"
    STARTSWITH = "startswith"
    ENDSWITH = "endswith"
    SEARCH = "search"


class FilterItem(BaseModel, Generic[T]):
    """
    Represents a single filter item consisting of a field, an operation name, and a value.
    """

    field: str
    op: Operation
    value: int | str | list | None

    def validate_field(self, model: type[T]):
        """
        Validate the field against the model's fields and ensure it is indexable.
        :param model: The Tortoise model to validate the field against.
        :raises HTTPException: If the field is not valid or not indexable.
        """
        if self.field not in getattr(model.Meta, "filter_by_fields", []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Field cannot be filtered: " + self.field,
            )
        parts = self.field.split("__")
        while True:
            part = parts.pop(0)
            try:
                field = model._meta.fields_map[part]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unknown field: " + self.field,
                )
            if not len(parts):
                break
            if isinstance(field, ForeignKeyFieldInstance):
                model = field.related_model
            elif isinstance(field, ManyToManyFieldInstance):
                model = field.related_model
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Field is not a relation: " + self.field,
                )
        if not field.indexable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Field cannot be filtered: " + self.field,
            )
        to_value = self._to_value_any
        if isinstance(field, IntEnumFieldInstance):
            to_value = self._to_value_intenum
        if self.op in (Operation.IN, Operation.NOT_IN):
            if not isinstance(self.value, list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Value must be a list for operation: " + self.op,
                )
            self.value = [to_value(field, v) for v in self.value]
        else:
            self.value = to_value(field, self.value)

    @staticmethod
    def _to_value_any(field: Field, v):
        return field.to_python_value(v)

    @staticmethod
    def _to_value_intenum(field: Field, v):
        assert isinstance(field, IntEnumFieldInstance)
        if isinstance(v, str):
            try:
                return field.enum_type(int(v))
            except ValueError:
                pass
            try:
                return field.enum_type[v]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid enum value {v!r} for field {field.model_field_name}",
                )
        if isinstance(v, int):
            return field.enum_type(v)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid enum value {v!r} for field {field.model_field_name}",
        )

    def apply(self, query: QuerySet[T]) -> QuerySet[T]:
        """
        Apply the filter to the given Tortoise QuerySet.
        :param query: The Tortoise QuerySet to apply the filter to.
        :return: The filtered QuerySet.
        """
        f = self.field
        match self.op:
            case Operation.EQ:
                pass
            case Operation.NE:
                f += "__not"
            case _:
                f += "__" + self.op
        query = query.filter(**{f: self.value})
        return query


class FilterSet(BaseModel, Generic[T]):
    """
    Represents a collection of filters to be applied to a query.
    """

    filters: list[FilterItem]

    def __init__(
        self,
        model: type[T],
        filters: list[FilterItem] = [],
        before_validate: Callable[[Self], None] | None = None,
    ) -> None:
        """
        Initialize the Filters object with a model and a filter parameter.
        :param model: The Tortoise model to validate the filters against.
        :param param: A JSON string representing the filters.
        :param before_validate: An optional callback to run before validating the filters.
        :raises HTTPException: If the filter string is invalid or if validation fails.
        """
        try:
            super().__init__(filters=filters)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.errors(include_url=False),
            )
        if before_validate:
            before_validate(self)
        for filter in self.filters:
            filter.validate_field(model)

    def apply(self, query: QuerySet[T]) -> QuerySet[T]:
        """
        Apply all filters to the given Tortoise QuerySet.
        :param query: The Tortoise QuerySet to apply filters to.
        :return: The filtered QuerySet.
        """
        for filter in self.filters:
            query = filter.apply(query)
        return query

    @classmethod
    def __class_getitem__(cls, model: type[T]) -> "FilterSet":  # type: ignore
        """
        Magic function to create a dependency for filtering Tortoise QuerySets using the type hint.
        This allows the use of `FilterSet[Model]` as an endpoint parameter type hint.
        :param model: The Tortoise model to validate the filters against.
        :return: A callable that takes a filter string and returns a FilterSet.
        """

        def _filters(filter: Annotated[str, Query()] = "[]") -> FilterSet:
            try:
                params = pydantic.TypeAdapter(
                    Json[list[tuple[str, str, Any]]]
                ).validate_python(filter)
            except pydantic.ValidationError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=e.errors(include_url=False, include_context=False),
                )
            items: list[FilterItem[T]] = [
                FilterItem(field=f[0], op=Operation(f[1]), value=f[2]) for f in params
            ]
            return FilterSet(model, items)

        return Annotated[FilterSet, Depends(_filters)]  # type: ignore
