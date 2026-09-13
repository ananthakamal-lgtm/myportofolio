from django.contrib import admin
from main.models import Experience, Project

# Register your models here.

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "started_at", "ended_at")
    list_filter = ("category",)
    search_fields = ("title", "description")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "year", "created_at")
    list_filter = ("category", "year")
    search_fields = ("title", "description", "tech_stack")

