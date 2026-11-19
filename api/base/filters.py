import django_filters
from rest_framework import filters
from django.db import models
from typing import List
from typing import Tuple


class FilterFields:
    String = ['iexact', 'exact', 'contains', 'icontains', 'startswith', 'istartswith', 'endswith', 'iendswith',
              'isnull', 'in', 'regex', 'iregex']
    Number = ['iexact', 'exact', 'gt', 'gte', 'lt', 'lte', 'isnull']
    Date = ['range', 'year', 'month', 'day', 'week', 'week_day', 'quarter', 'isnull', 'gte', 'lte']
    Boolean = ['iexact', 'exact', 'isnull']
    List = ['in']


class BaseFilterSet(django_filters.FilterSet):
    """Base FilterSet that adds lookups for the common id/created/updated fields.

    Subclasses declare their own fields in Meta.fields as a {field: [lookups]} dict;
    the common fields are merged in automatically (when the model has them).
    """
    base_filter_fields = {
        "id": FilterFields.String,
        "updated": FilterFields.Date,
        "created": FilterFields.Date,
    }

    @classmethod
    def get_fields(cls):
        fields = super().get_fields()
        model_field_names = {f.name for f in cls._meta.model._meta.get_fields()}
        for name, lookups in cls.base_filter_fields.items():
            if name in model_field_names and name not in fields:
                fields[name] = lookups
        return fields


class RelatedOrderingFilter(filters.OrderingFilter):
    _max_related_depth = 3

    @staticmethod
    def _get_verbose_name(field: models.Field, non_verbose_name: str) -> str:
        return field.verbose_name if hasattr(field, 'verbose_name') else non_verbose_name.replace('_', ' ')

    def _retrieve_all_related_fields(
            self,
            fields: Tuple[models.Field],
            model: models.Model,
            depth: int = 0
    ) -> List[tuple]:
        valid_fields = []
        if depth > self._max_related_depth:
            return valid_fields
        for field in fields:
            if field.related_model and field.related_model != model:
                rel_fields = self._retrieve_all_related_fields(field.related_model._meta.get_fields(),
                                                               field.related_model,
                                                               depth + 1)
                for rel_field in rel_fields:
                    valid_fields.append((
                        f'{field.name}__{rel_field[0]}',
                        self._get_verbose_name(field, rel_field[1])
                    ))
            else:
                valid_fields.append((
                    field.name,
                    self._get_verbose_name(field, field.name),
                ))
        return valid_fields

    def get_valid_fields(self, queryset: models.QuerySet, view, context: dict = None) -> List[tuple]:
        valid_fields = getattr(view, 'ordering_fields', self.ordering_fields)
        if not valid_fields == '__all_related__':
            if not context:
                context = {}
            valid_fields = super().get_valid_fields(queryset, view, context)
        else:
            valid_fields = [
                *self._retrieve_all_related_fields(queryset.model._meta.get_fields(), queryset.model),
                *[(key, key.title().split('__')) for key in queryset.query.annotations]
            ]
        return valid_fields
