from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters as rest_filters
from django_filters import rest_framework as filters

from sentry_sdk import capture_exception

from palenso.api.filters.job import JobFilter
from palenso.api.serializers.job import JobSerializer
from palenso.db.models import Job


class JobListCreateEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    filter_backends = (
        filters.DjangoFilterBackend,
        rest_filters.SearchFilter,
    )
    filterset_class = JobFilter
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
            queryset = Job.objects.all()
            filtered_queryset = self.filter_queryset(request, queryset)
            serializer = JobSerializer(filtered_queryset, many=True)
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
            payload["company"] = request.user.company.id
            serializer = JobSerializer(data=payload)
            if serializer.is_valid():
                serializer.save(created_by=request.user, updated_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class JobDetailEndpoint(APIView):
    def get(self, request, job_id):
        try:
            queryset = Job.objects.get(pk=job_id)
            serializer = JobSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Job.DoesNotExist:
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

    def put(self, request, job_id):
        try:
            queryset = Job.objects.get(pk=job_id)
            serializer = JobSerializer(queryset, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Job.DoesNotExist:
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

    def delete(self, request, job_id):
        try:
            queryset = Job.objects.get(pk=job_id)
            if request.user.role != "admin" and request.user != queryset.user:
                return Response("Restricted", status=status.HTTP_403_FORBIDDEN)
            queryset.delete()
            return Response("Deleted successfully!", status=status.HTTP_204_NO_CONTENT)

        except Job.DoesNotExist:
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
