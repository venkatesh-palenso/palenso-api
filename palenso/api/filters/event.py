from django_filters import rest_framework as filters
from django.db.models import Q

from palenso.db.models.event import Event


class EventFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr="icontains")
    event_type = filters.CharFilter(lookup_expr="iexact")
    location = filters.CharFilter(lookup_expr="icontains")
    is_virtual = filters.BooleanFilter()
    is_active = filters.BooleanFilter()
    is_featured = filters.BooleanFilter()
    is_registration_required = filters.BooleanFilter()
    start_date = filters.DateTimeFromToRangeFilter()
    end_date = filters.DateTimeFromToRangeFilter()
    registration_fee_min = filters.NumberFilter(field_name="registration_fee", lookup_expr="gte")
    registration_fee_max = filters.NumberFilter(field_name="registration_fee", lookup_expr="lte")
    company_name = filters.CharFilter(field_name="company__name", lookup_expr="icontains")

    class Meta:
        model = Event
        fields = [
            "event_type",
            "is_virtual",
            "is_active",
            "is_featured",
            "is_registration_required",
            "start_date",
            "end_date",
            "registration_fee_min",
            "registration_fee_max",
            "company_name",
        ]
