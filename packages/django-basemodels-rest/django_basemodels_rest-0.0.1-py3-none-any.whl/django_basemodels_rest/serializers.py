from rest_framework import serializers
from django_basemodels.models import BaseModel


class BaseModelSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()
    polymorphic_ctype = serializers.SerializerMethodField()

    class Meta:
        model = BaseModel
        fields = ("pk", "created_at", "updated_at", "active_start", "active_end")
        writable_fields = tuple()
        read_only_fields = tuple()

        def __init_subclass__(cls, **kwargs):
            cls.read_only_fields = tuple(
                f
                for f in getattr(cls, "fields", ())
                if f not in tuple(getattr(cls, "writable_fields", ())) + ("pk", "created_at", "updated_at")
            )

            super().__init_subclass__(**kwargs)

    def get_polymorphic_ctype(self, obj: BaseModel | dict):
        if isinstance(obj, BaseModel):
            return obj.polymorphic_ctype.id

        if isinstance(obj, dict):
            return obj.get("polymorphic_ctype")

        return None

    def get_is_active(self, obj: BaseModel | dict):
        if isinstance(obj, BaseModel):
            return obj.is_active_real

        return None

    def to_representation(self, instance: BaseModel | dict):
        representation = super().to_representation(instance)

        if isinstance(instance, BaseModel):
            representation["is_active"] = self.get_is_active(instance)

        return representation
