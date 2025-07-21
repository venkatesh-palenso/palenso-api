from rest_framework import serializers

from palenso.db.models.library import MediaAssets


class MediaAssetSerializer(serializers.ModelSerializer):
    display_url = serializers.ReadOnlyField()

    class Meta:
        model = MediaAssets
        fields = [
            "id",
            "file",
            "asset_type",
            "display_url",
            "is_active",
        ]
        read_only_fields = ["id", "display_url", "is_active"]
