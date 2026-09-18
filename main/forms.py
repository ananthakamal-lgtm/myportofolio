from django.forms import ModelForm, TextInput, Textarea, NumberInput, URLInput, Select
from main.models import Experience, Project


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


class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "category",
            "description",
            "thumbnail",
        ]
        labels = {
            "title": "Judul / Posisi Pengalaman",
            "category": "Kategori Pengalaman",
            "description": "Deskripsi Pengalaman",
            "thumbnail": "URL Thumbnail / Logo (Opsional)",
        }
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Contoh: Software Engineering Intern",
                    "maxlength": 255,
                }
            ),
            "category": Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Jelaskan peran, tanggung jawab, dan pencapaian Anda...",
                    "rows": 4,
                }
            ),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://example.com/logo.png",
                }
            ),
        }
