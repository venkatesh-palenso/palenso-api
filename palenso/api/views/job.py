from rest_framework import status

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters as rest_filters
from django_filters import rest_framework as filters

from sentry_sdk import capture_exception

from palenso.api.filters.job import JobFilter
from palenso.api.serializers.job import (
    JobSerializer, JobApplicationSerializer, SavedJobSerializer,
    InterviewSerializer, OfferSerializer
)
from palenso.db.models.job import Job, JobApplication, SavedJob, Interview, Offer


class JobListCreateEndpoint(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    filter_backends = (
        filters.DjangoFilterBackend,
        rest_filters.SearchFilter,
    )
    filterset_class = JobFilter
    search_fields = (
        "^title",
        "^job_type",
        "^experience_level",
        "^location",
        "^category",
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
            # Check if employer has company
            if request.user.role == "employer" and not request.user.is_employer_with_company:
                return Response(
                    {"error": "Please create a company profile before posting jobs."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            payload = request.data
            serializer = JobSerializer(data=payload)
            if serializer.is_valid():
                serializer.save(company=request.user.company,created_by=request.user, updated_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class JobDetailEndpoint(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get(self, request, job_id):
        try:
            queryset = Job.objects.get(pk=job_id)
            serializer = JobSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Job.DoesNotExist:
            return Response(
                {"error": "Sorry, Job not found. Please try again."},
                status=status.HTTP_404_NOT_FOUND,
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
                {"error": "Sorry, Job not found. Please try again."},
                status=status.HTTP_404_NOT_FOUND,
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
            if request.user.role != "admin" and request.user != queryset.company.employer:
                return Response("Restricted", status=status.HTTP_403_FORBIDDEN)
            queryset.delete()
            return Response("Deleted successfully!", status=status.HTTP_204_NO_CONTENT)

        except Job.DoesNotExist:
            return Response(
                {"error": "Sorry, Job not found. Please try again."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class JobApplicationListCreateEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role == "employer":
                # Check if employer has company
                if not request.user.is_employer_with_company:
                    return Response([], status=status.HTTP_200_OK)
                # Employer sees applications for their company's jobs
                queryset = JobApplication.objects.filter(job__company__employer=request.user)
            else:
                # Student sees their own applications
                queryset = JobApplication.objects.filter(applicant=request.user)
            
            serializer = JobApplicationSerializer(queryset, many=True)
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
            serializer = JobApplicationSerializer(data=payload)
            if serializer.is_valid():
                serializer.save(applicant=request.user,created_by=request.user, updated_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class JobApplicationDetailEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, application_id):
        try:
            if request.user.role == "employer":
                queryset = JobApplication.objects.get(
                    pk=application_id, job__company__employer=request.user
                )
            else:
                queryset = JobApplication.objects.get(
                    pk=application_id, applicant=request.user
                )
            serializer = JobApplicationSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JobApplication.DoesNotExist:
            return Response(
                {"error": "Application not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, application_id):
        try:
            if request.user.role == "employer":
                queryset = JobApplication.objects.get(
                    pk=application_id, job__company__employer=request.user
                )
            else:
                queryset = JobApplication.objects.get(
                    pk=application_id, applicant=request.user
                )
            serializer = JobApplicationSerializer(queryset, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JobApplication.DoesNotExist:
            return Response(
                {"error": "Application not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SavedJobListCreateEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            queryset = SavedJob.objects.filter(student=request.user)
            serializer = SavedJobSerializer(queryset, many=True)
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
            payload["student"] = request.user.id
            serializer = SavedJobSerializer(data=payload)
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


class SavedJobDetailEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, saved_job_id):
        try:
            saved_job = SavedJob.objects.get(pk=saved_job_id, student=request.user)
            saved_job.delete()
            return Response("Removed from saved jobs!", status=status.HTTP_204_NO_CONTENT)
        except SavedJob.DoesNotExist:
            return Response(
                {"error": "Saved job not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class InterviewListCreateEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role == "employer":
                # Check if employer has company
                if not request.user.is_employer_with_company:
                    return Response([], status=status.HTTP_200_OK)
                # Employer sees interviews for their company's applications
                queryset = Interview.objects.filter(
                    application__job__company__employer=request.user
                )
            else:
                # Student sees interviews for their applications
                queryset = Interview.objects.filter(application__applicant=request.user)
            
            serializer = InterviewSerializer(queryset, many=True)
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
            payload["interviewer"] = request.user.id
            serializer = InterviewSerializer(data=payload)
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


class InterviewDetailEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, interview_id):
        try:
            if request.user.role == "employer":
                queryset = Interview.objects.get(
                    pk=interview_id, application__job__company__employer=request.user
                )
            else:
                queryset = Interview.objects.get(
                    pk=interview_id, application__applicant=request.user
                )
            serializer = InterviewSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Interview.DoesNotExist:
            return Response(
                {"error": "Interview not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, interview_id):
        try:
            if request.user.role == "employer":
                queryset = Interview.objects.get(
                    pk=interview_id, application__job__company__employer=request.user
                )
            else:
                queryset = Interview.objects.get(
                    pk=interview_id, application__applicant=request.user
                )
            serializer = InterviewSerializer(queryset, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Interview.DoesNotExist:
            return Response(
                {"error": "Interview not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfferListCreateEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role == "employer":
                # Check if employer has company
                if not request.user.is_employer_with_company:
                    return Response([], status=status.HTTP_200_OK)
                # Employer sees offers made by their company
                queryset = Offer.objects.filter(
                    application__job__company__employer=request.user
                )
            else:
                # Student sees offers for their applications
                queryset = Offer.objects.filter(application__applicant=request.user)
            
            serializer = OfferSerializer(queryset, many=True)
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
            payload["offered_by"] = request.user.id
            serializer = OfferSerializer(data=payload)
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


class OfferDetailEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, offer_id):
        try:
            if request.user.role == "employer":
                queryset = Offer.objects.get(
                    pk=offer_id, application__job__company__employer=request.user
                )
            else:
                queryset = Offer.objects.get(
                    pk=offer_id, application__applicant=request.user
                )
            serializer = OfferSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Offer.DoesNotExist:
            return Response(
                {"error": "Offer not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, offer_id):
        try:
            if request.user.role == "employer":
                queryset = Offer.objects.get(
                    pk=offer_id, application__job__company__employer=request.user
                )
            else:
                queryset = Offer.objects.get(
                    pk=offer_id, application__applicant=request.user
                )
            serializer = OfferSerializer(queryset, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Offer.DoesNotExist:
            return Response(
                {"error": "Offer not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
