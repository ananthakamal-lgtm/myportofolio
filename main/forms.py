from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, Textarea, NumberInput, URLInput, Select
from django.utils.html import strip_tags
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

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama proyek tidak boleh hanya berisi tag HTML.")
        return title

    def clean_category(self):
        category = self.cleaned_data.get("category", "")
        return strip_tags(category).strip()

    def clean_tech_stack(self):
        return strip_tags(self.cleaned_data["tech_stack"]).strip()

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()


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

    def clean_title(self):
        title = strip_tags(self.cleaned_data.get("title", "")).strip()
        if not title:
            raise ValidationError("Judul pengalaman tidak boleh hanya berisi tag HTML.")
        return title

    def clean_category(self):
        category = self.cleaned_data.get("category", "")
        return strip_tags(category).strip()

    def clean_description(self):
        description = strip_tags(self.cleaned_data.get("description", "")).strip()
        if not description:
            raise ValidationError("Deskripsi pengalaman tidak boleh hanya berisi tag HTML.")
        return description
