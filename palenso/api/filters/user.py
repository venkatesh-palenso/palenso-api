from django_filters import rest_framework as filters
from django.db.models import Q

from palenso.db.models.user import User


class UserFilter(filters.FilterSet):
    # Search fields
    search = filters.CharFilter(method="search_users")
    
    # Individual field filters
    email = filters.CharFilter(lookup_expr="icontains")
    first_name = filters.CharFilter(lookup_expr="icontains")
    last_name = filters.CharFilter(lookup_expr="icontains")
    mobile_number = filters.CharFilter(lookup_expr="icontains")
    
    # Choice-based filters
    role = filters.CharFilter(lookup_expr="iexact")
    is_active = filters.BooleanFilter()
    is_email_verified = filters.BooleanFilter()
    is_mobile_verified = filters.BooleanFilter()
    
    # Date range filters
    date_joined = filters.DateTimeFromToRangeFilter()
    last_active = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = User
        fields = [
            "email",
            "first_name", 
            "last_name",
            "mobile_number",
            "role",
            "is_active",
            "is_email_verified",
            "is_mobile_verified",
            "date_joined",
            "last_active",
        ]

    def search_users(self, queryset, name, value):
        """Search across multiple user fields"""
        return queryset.filter(
            Q(email__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(mobile_number__icontains=value) |
            Q(username__icontains=value)
        ) 