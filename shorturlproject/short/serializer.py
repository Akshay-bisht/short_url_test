from rest_framework import serializers
from .models import MyUser, UrlDetail

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = ("__all__")

    def get_name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name)

class ChangePasswordSerializer(serializers.Serializer):
    model = MyUser

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UrlDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = UrlDetail
        fields = "__all__"
    