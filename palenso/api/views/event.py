from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters as rest_filters
from django_filters import rest_framework as filters

from sentry_sdk import capture_exception

from palenso.api.filters.event import EventFilter
from palenso.api.serializers.event import EventSerializer
from palenso.db.models import Event


class EventListCreateEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    filter_backends = (
        filters.DjangoFilterBackend,
        rest_filters.SearchFilter,
    )
    filterset_class = EventFilter
    search_fields = (
        "^name",
        "^industry",
        "^city",
        "^state",
        "^country",
    )

    def filter_queryset(self, request, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(request, queryset, self)
        return queryset

    def get(self, request):
        try:
            queryset = Event.objects.all()
            filtered_queryset = self.filter_queryset(request, queryset)
            serializer = EventSerializer(filtered_queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            payload = request.data
            payload["employer"] = request.user.id
            serializer = EventSerializer(data=payload)
            if serializer.is_valid():
                serializer.save(created_by=request.user, updated_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EventDetailEndpoint(APIView):
    def get(self, request, event_id):
        try:
            queryset = Event.objects.get(pk=event_id)
            serializer = EventSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response(
                {"error": "Sorry, Company not found. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, event_id):
        try:
            queryset = Event.objects.get(pk=event_id)
            serializer = EventSerializer(queryset, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Event.DoesNotExist:
            return Response(
                {"error": "Sorry, Company not found. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, event_id):
        try:
            queryset = Event.objects.get(pk=event_id)
            if request.user.role != "admin" and request.user != queryset.user:
                return Response("Restricted", status=status.HTTP_403_FORBIDDEN)
            queryset.delete()
            return Response("Deleted successfully!", status=status.HTTP_204_NO_CONTENT)

        except Event.DoesNotExist:
            return Response(
                {"error": "Sorry, Company not found. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
