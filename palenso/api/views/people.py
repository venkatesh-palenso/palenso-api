from rest_framework import status
from rest_framework import filters as rest_filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from sentry_sdk import capture_exception
from django_filters import rest_framework as filters


from palenso.api.serializers.people import UserSerializer

from palenso.utils.paginator import BasePaginator

from palenso.db.models import User


class PeopleView(APIView, BasePaginator):

    filterset_fields = ("date_joined",)

    search_fields = (
        "^first_name",
        "^last_name",
        "^email",
        "^username",
    )

    filter_backends = (
        filters.DjangoFilterBackend,
        rest_filters.SearchFilter,
    )

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request):
        try:
            users = User.objects.all().order_by("-date_joined")

            if (
                request.GET.get("search", None) is not None
                and len(request.GET.get("search")) < 3
            ):
                return Response(
                    {"message": "Search term must be at least 3 characters long"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return self.paginate(
                request=request,
                queryset=self.filter_queryset(users),
                on_results=lambda data: UserSerializer(data, many=True).data,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = User.objects.get(pk=request.user.id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "Sorry, User not found. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
