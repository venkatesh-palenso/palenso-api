from django_filters import rest_framework as filters
from django.db.models import Q

from palenso.db.models.job import Job


class JobFilter(filters.FilterSet):
    location = filters.CharFilter(lookup_expr="icontains")
    job_type = filters.CharFilter(lookup_expr="iexact")
    experience_level = filters.CharFilter(lookup_expr="iexact")
    is_remote = filters.BooleanFilter()
    is_active = filters.BooleanFilter()
    is_featured = filters.BooleanFilter()
    category = filters.CharFilter(lookup_expr="icontains")
    salary_min = filters.NumberFilter(field_name="salary_min", lookup_expr="gte")
    salary_max = filters.NumberFilter(field_name="salary_max", lookup_expr="lte")
    company_name = filters.CharFilter(field_name="company__name", lookup_expr="icontains")
    company_industry = filters.CharFilter(field_name="company__industry", lookup_expr="icontains")

    class Meta:
        model = Job
        fields = [
            "job_type",
            "experience_level",
            "is_remote",
            "is_active",
            "is_featured",
            "category",
            "salary_min",
            "salary_max",
            "company_name",
            "company_industry",
        ]
