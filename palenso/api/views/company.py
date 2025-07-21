from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from sentry_sdk import capture_exception

from palenso.api.serializers.company import CompanySerializer
from palenso.db.models.company import Company


class CompanyProfileListCreateEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            queryset = Company.objects.all()
            serializer = CompanySerializer(queryset, many=True)
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
            serializer = CompanySerializer(data=payload)
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


class CompanyProfileDetailEndpoint(APIView):
    def get(self, request, company_id):
        try:
            queryset = Company.objects.get(pk=company_id)
            serializer = CompanySerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Company.DoesNotExist:
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

    def put(self, request, company_id):
        try:
            queryset = Company.objects.get(pk=company_id)
            serializer = CompanySerializer(queryset, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Company.DoesNotExist:
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

    def delete(self, request, company_id):
        try:
            queryset = Company.objects.get(pk=company_id)
            if request.user.role != "admin" and request.user != queryset.user:
                return Response("Restricted", status=status.HTTP_403_FORBIDDEN)
            queryset.delete()
            return Response("Deleted successfully!", status=status.HTTP_204_NO_CONTENT)

        except Company.DoesNotExist:
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
