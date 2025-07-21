from django.core.exceptions import ValidationError
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from sentry_sdk import capture_exception

from palenso.api.serializers.media import MediaAssetSerializer
from palenso.db.models.library import MediaAssets


class UploadMediaEndpoint(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            asset_type = request.data.get("asset_type", "other")
            file = request.FILES.get("file")

            if not file:
                return Response(
                    {"error": "No file uploaded."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = MediaAssetSerializer(
                data={"file": file, "asset_type": asset_type}
            )
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
