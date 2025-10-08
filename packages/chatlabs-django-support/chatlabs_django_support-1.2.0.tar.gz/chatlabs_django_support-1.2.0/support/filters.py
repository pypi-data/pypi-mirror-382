from django_filters import rest_framework as filters

from . import models


class Ticket(filters.FilterSet):
    user_id = filters.NumberFilter(
        field_name='user',
    )
    manager = filters.NumberFilter(
        field_name='support_manager',
    )
    manager__isnull = filters.BooleanFilter(
        field_name='support_manager',
        lookup_expr='isnull',
    )

    class Meta:
        model = models.Ticket
        fields = [
            'user_id',
            'resolved',
            'manager',
        ]
