"""
DRF Serializers for Project (Tutorial 07) and Experience (Tugas 6).

Handles bidirectional conversion between Django ORM instances and JSON-ready
Python primitives, computed star metadata, and server-side XSS input validation.
"""

from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Experience, Project


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for the Project model with computed star metadata and XSS validation."""

    project_url = serializers.URLField(required=False, allow_blank=True)
    project_image_url = serializers.URLField(required=False, allow_blank=True)
    category = serializers.CharField(max_length=100, required=False, allow_blank=True)
    year = serializers.IntegerField(required=False)
    demo_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    repo_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "category", "description", "year", "tech_stack",
            "demo_url", "repo_url",
            "project_url", "project_image_url",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_category(self, value):
        return strip_tags(value).strip()

    def validate_description(self, value):
        return strip_tags(value)

    def validate_tech_stack(self, value):
        return strip_tags(value)

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())

    def create(self, validated_data):
        project_url = validated_data.pop("project_url", None)
        project_image_url = validated_data.pop("project_image_url", "")
        if project_url and not validated_data.get("demo_url"):
            validated_data["demo_url"] = project_url
        instance = super().create(validated_data)
        instance.project_image_url = project_image_url
        return instance

    def update(self, instance, validated_data):
        project_url = validated_data.pop("project_url", None)
        project_image_url = validated_data.pop("project_image_url", None)
        if project_url is not None and "demo_url" not in validated_data:
            validated_data["demo_url"] = project_url
        instance = super().update(instance, validated_data)
        if project_image_url is not None:
            instance.project_image_url = project_image_url
        return instance


class ExperienceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Experience model (Tugas 6).

    Exposes explicit model fields alongside read-only computed star fields
    (star_count, is_starred, starred_by_names) without leaking sensitive User data.
    Sanitizes text fields with strip_tags to prevent stored XSS.
    """

    thumbnail = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = [
            "id", "title", "category", "category_display", "description",
            "thumbnail", "started_at", "ended_at", "is_ongoing",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id", "started_at", "category_display", "is_ongoing"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Description cannot be empty.")
        return value

    def validate_category(self, value):
        return strip_tags(value).strip()

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())
