from rest_framework import status

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters as rest_filters
from django_filters import rest_framework as filters

from sentry_sdk import capture_exception

from palenso.api.filters.event import EventFilter
from palenso.api.serializers.event import EventSerializer, EventRegistrationSerializer, AnonymousEventRegistrationSerializer
from palenso.db.models.event import Event, EventRegistration


class EventListCreateEndpoint(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    filter_backends = (
        filters.DjangoFilterBackend,
        rest_filters.SearchFilter,
    )
    filterset_class = EventFilter
    search_fields = (
        "^title",
        "^event_type",
        "^location",
        "^description",
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
            if request.user.role == "student":
                return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)
            payload = request.data
            if hasattr(request.user, "company"):
                payload["company"] = request.user.company.id
            serializer = EventSerializer(data=payload)
            if serializer.is_valid():
                serializer.save(
                    organizer=request.user,
                    created_by=request.user,
                    updated_by=request.user,
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EventDetailEndpoint(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, event_id):
        try:
            queryset = Event.objects.get(pk=event_id)
            serializer = EventSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response(
                {"error": "Sorry, Event not found. Please try again."},
                status=status.HTTP_404_NOT_FOUND,
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
                {"error": "Sorry, Event not found. Please try again."},
                status=status.HTTP_404_NOT_FOUND,
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
            if request.user.role != "admin" and request.user != queryset.organizer:
                return Response("Restricted", status=status.HTTP_403_FORBIDDEN)
            queryset.delete()
            return Response("Deleted successfully!", status=status.HTTP_204_NO_CONTENT)

        except Event.DoesNotExist:
            return Response(
                {"error": "Sorry, Event not found. Please try again."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EventRegistrationListCreateEndpoint(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        try:
            if request.user.role in ["admin", "employer"]:
                # Admin/Employer sees all registrations for events they organize
                if request.user.role == "employer":
                    queryset = EventRegistration.objects.filter(
                        event__organizer=request.user
                    )
                else:
                    queryset = EventRegistration.objects.all()
            else:
                # Student sees their own registrations
                queryset = EventRegistration.objects.filter(participant=request.user)

            serializer = EventRegistrationSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            # Choose serializer based on authentication status
            if request.user.is_authenticated:
                # Use regular serializer for authenticated users
                payload = request.data.copy()
                payload["participant"] = request.user.id
                serializer = EventRegistrationSerializer(data=payload)
            else:
                # Use anonymous serializer for unauthenticated users
                serializer = AnonymousEventRegistrationSerializer(data=request.data)
            
            if serializer.is_valid():
                registration = serializer.save(
                    created_by=request.user if request.user.is_authenticated else None,
                    updated_by=request.user if request.user.is_authenticated else None,
                )
                
                # Return appropriate response based on authentication status
                if request.user.is_authenticated:
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    # Return simplified response for anonymous users
                    response_data = {
                        "message": "Registration successful!",
                        "registration_id": registration.id,
                        "event_title": registration.event.title,
                        "participant_name": registration.participant.get_full_name(),
                        "participant_email": registration.participant.email,
                        "registration_date": registration.registration_date,
                        "status": registration.status,
                        "payment_status": registration.payment_status,
                        "payment_amount": str(registration.payment_amount),
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EventRegistrationDetailEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, registration_id):
        try:
            if request.user.role in ["admin", "employer"]:
                if request.user.role == "employer":
                    queryset = EventRegistration.objects.get(
                        pk=registration_id, event__organizer=request.user
                    )
                else:
                    queryset = EventRegistration.objects.get(pk=registration_id)
            else:
                queryset = EventRegistration.objects.get(
                    pk=registration_id, participant=request.user
                )
            serializer = EventRegistrationSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except EventRegistration.DoesNotExist:
            return Response(
                {"error": "Registration not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, registration_id):
        try:
            if request.user.role in ["admin", "employer"]:
                if request.user.role == "employer":
                    queryset = EventRegistration.objects.get(
                        pk=registration_id, event__organizer=request.user
                    )
                else:
                    queryset = EventRegistration.objects.get(pk=registration_id)
            else:
                queryset = EventRegistration.objects.get(
                    pk=registration_id, participant=request.user
                )
            serializer = EventRegistrationSerializer(
                queryset, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except EventRegistration.DoesNotExist:
            return Response(
                {"error": "Registration not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            capture_exception(e)
            return Response(
                {"message": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
