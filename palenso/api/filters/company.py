from django_filters import rest_framework as filters
from django.db.models import Q

from palenso.db.models.company import Company


class CompanyFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    location = filters.CharFilter(method="filter_location")
    founded_year = filters.DateFromToRangeFilter()
    company_size = filters.CharFilter(lookup_expr="iexact")
    is_verified = filters.BooleanFilter()
    is_active = filters.BooleanFilter()
    industry = filters.CharFilter(lookup_expr="icontains")
    country = filters.CharFilter(lookup_expr="icontains")
    state = filters.CharFilter(lookup_expr="icontains")
    city = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Company
        fields = [
            "name",
            "founded_year",
            "company_size",
            "is_verified",
            "is_active",
            "industry",
            "country",
            "state",
            "city",
        ]

    def filter_location(self, queryset, name, value):
        return queryset.filter(
            Q(address__icontains=value)
            | Q(city__icontains=value)
            | Q(state__icontains=value)
            | Q(country__icontains=value)
        )
