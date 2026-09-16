from django.forms import ModelForm, TextInput, Textarea, NumberInput, URLInput
from main.models import Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "category",
            "description",
            "year",
            "tech_stack",
            "demo_url",
            "repo_url",
        ]
        labels = {
            "title": "Nama Proyek",
            "category": "Kategori Proyek",
            "description": "Deskripsi Proyek",
            "year": "Tahun",
            "tech_stack": "Teknologi yang Digunakan",
            "demo_url": "URL Live Demo",
            "repo_url": "URL Repositori",
        }
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "category": TextInput(
                attrs={
                    "placeholder": "Web Development, Machine Learning, dll.",
                    "maxlength": 100,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan ringkasan proyekmu...",
                    "rows": 3,
                }
            ),
            "year": NumberInput(
                attrs={
                    "placeholder": "2026",
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "demo_url": URLInput(
                attrs={
                    "placeholder": "https://example.com/demo",
                }
            ),
            "repo_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/username/project",
                }
            ),
        }
