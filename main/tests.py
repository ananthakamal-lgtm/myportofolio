import json
import uuid
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_projects")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_projects")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")


class ExperienceCRUDTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Software Engineering Intern",
            category="internship",
            description="Membangun fitur backend dengan Django dan REST API.",
            thumbnail="https://example.com/logo.png",
        )

    def test_experience_form_valid(self):
        data = {
            "title": "Teaching Assistant",
            "category": "part-time",
            "description": "Mengajar dasar-dasar pemrograman.",
            "thumbnail": "https://example.com/ta.png",
        }
        form = ExperienceForm(data=data)
        self.assertTrue(form.is_valid())

    def test_experience_form_invalid(self):
        form = ExperienceForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("description", form.errors)

    def test_create_experience_get(self):
        response = self.client.get(reverse("main:create_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, "Add New Experience")

    def test_create_experience_post_valid(self):
        data = {
            "title": "Machine Learning Research Intern",
            "category": "research",
            "description": "Melakukan eksperimen model CNN untuk segmentasi citra medis.",
            "thumbnail": "https://example.com/research.png",
        }
        response = self.client.post(reverse("main:create_experience"), data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertTrue(Experience.objects.filter(title="Machine Learning Research Intern").exists())

    def test_create_experience_post_invalid(self):
        initial_count = Experience.objects.count()
        response = self.client.post(reverse("main:create_experience"), {"title": ""})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Experience.objects.count(), initial_count)
        self.assertFormError(response.context["form"], "title", "This field is required.")

    def test_update_experience_get(self):
        response = self.client.get(
            reverse("main:update_experience", kwargs={"experience_id": self.experience.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")
        self.assertContains(response, "Edit Experience")
        self.assertContains(response, self.experience.title)

    def test_update_experience_post_valid(self):
        data = {
            "title": "Senior Software Engineering Intern",
            "category": "internship",
            "description": "Memimpin inisiatif optimasi query database dan caching.",
            "thumbnail": "https://example.com/updated_logo.png",
        }
        response = self.client.post(
            reverse("main:update_experience", kwargs={"experience_id": self.experience.id}),
            data,
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:show_experience"))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Senior Software Engineering Intern")
        self.assertEqual(self.experience.description, "Memimpin inisiatif optimasi query database dan caching.")

    def test_update_experience_nonexistent_returns_404(self):
        response = self.client.get(
            reverse("main:update_experience", kwargs={"experience_id": uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_experience_post(self):
        exp_id = self.experience.id
        response = self.client.post(
            reverse("main:delete_experience", kwargs={"experience_id": exp_id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(id=exp_id).exists())

    def test_delete_experience_get_redirects_without_deleting(self):
        response = self.client.get(
            reverse("main:delete_experience", kwargs={"experience_id": self.experience.id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Experience.objects.filter(id=self.experience.id).exists())

    def test_delete_experience_nonexistent_returns_404(self):
        response = self.client.post(
            reverse("main:delete_experience", kwargs={"experience_id": uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 404)

    def test_get_experience_json_endpoint(self):
        response = self.client.get(reverse("main:get_experience_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/json")
        data = json.loads(response.content.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertTrue(any(item["fields"]["title"] == "Software Engineering Intern" for item in data))

    def test_get_experience_json_filter(self):
        response = self.client.get(reverse("main:get_experience_json") + "?title=Software")
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["fields"]["title"], self.experience.title)

        response_empty = self.client.get(reverse("main:get_experience_json") + "?title=NonExistent")
        data_empty = json.loads(response_empty.content.decode("utf-8"))
        self.assertEqual(len(data_empty), 0)

    def test_show_experience_search_matching(self):
        response = self.client.get(reverse("main:show_experience") + "?title=Software")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.experience.title)

    def test_show_experience_search_non_matching(self):
        response = self.client.get(reverse("main:show_experience") + "?title=NotFoundTitle123")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, "Tidak ada pengalaman dengan kata kunci tersebut.")


class ProjectTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Automated Manga Translator",
            category="Computer Vision · NLP",
            description="End-to-end pipeline untuk translasi manga otomatis.",
            year=2026,
            tech_stack="Python, YOLO, Gradio",
            demo_url="https://huggingface.co/spaces/example/manga",
            repo_url="https://github.com/example/manga-translator",
        )

    def test_project_model(self):
        self.assertEqual(str(self.project), "Automated Manga Translator")
        self.assertEqual(self.project.year, 2026)
        self.assertEqual(self.project.tech_list, ["Python", "YOLO", "Gradio"])

    def test_projects_url_and_template(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    def test_projects_page_displays_data(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.description)
        self.assertContains(response, self.project.category)
        self.assertContains(response, "Python")
        self.assertContains(response, "YOLO")
        self.assertContains(response, "Gradio")
        self.assertContains(response, self.project.demo_url)
        self.assertContains(response, self.project.repo_url)
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_empty_projects_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Belum ada proyek yang ditambahkan.")
        self.assertNotContains(response, self.project.title)

    def test_create_project_get(self):
        response = self.client.get(reverse("main:create_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, "Add New Project")

    def test_create_project_post_valid(self):
        data = {
            "title": "New AI Tool",
            "category": "Artificial Intelligence",
            "description": "Sebuah tool AI baru.",
            "year": 2026,
            "tech_stack": "PyTorch, FastAPI",
            "demo_url": "https://example.com",
            "repo_url": "https://github.com/example/tool",
        }
        response = self.client.post(reverse("main:create_project"), data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(title="New AI Tool").exists())

    def test_create_project_post_invalid(self):
        initial_count = Project.objects.count()
        response = self.client.post(reverse("main:create_project"), {"title": ""})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.count(), initial_count)
        self.assertFormError(response.context["form"], "title", "This field is required.")

    def test_update_project_get(self):
        response = self.client.get(
            reverse("main:update_project", kwargs={"project_id": self.project.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")
        self.assertContains(response, "Edit Project")
        self.assertContains(response, self.project.title)

    def test_update_project_post_valid(self):
        data = {
            "title": "Automated Manga Translator v2",
            "category": "Computer Vision · NLP",
            "description": "Versi revisi dengan inferensi lebih cepat.",
            "year": 2026,
            "tech_stack": "Python, TensorRT, FastAPI",
            "demo_url": "https://example.com/v2",
            "repo_url": "https://github.com/example/v2",
        }
        response = self.client.post(
            reverse("main:update_project", kwargs={"project_id": self.project.id}),
            data,
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Automated Manga Translator v2")

    def test_update_project_nonexistent_returns_404(self):
        response = self.client.get(
            reverse("main:update_project", kwargs={"project_id": uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_project_post(self):
        project_id = self.project.id
        response = self.client.post(
            reverse("main:delete_project", kwargs={"project_id": project_id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(id=project_id).exists())

    def test_delete_project_get_redirects_without_deleting(self):
        response = self.client.get(
            reverse("main:delete_project", kwargs={"project_id": self.project.id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_delete_nonexistent_project_returns_404(self):
        response = self.client.post(
            reverse("main:delete_project", kwargs={"project_id": uuid.uuid4()})
        )

        self.assertEqual(response.status_code, 404)

    def test_projects_search_matching(self):
        response = self.client.get(reverse("main:show_projects") + "?title=Manga")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.title)

    def test_projects_search_non_matching(self):
        response = self.client.get(reverse("main:show_projects") + "?title=NonExistentProject123")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.project.title)
        self.assertContains(response, "Tidak ada proyek dengan nama tersebut.")

    def test_get_projects_json_endpoint(self):
        response = self.client.get(reverse("main:get_projects_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/json")
        data = json.loads(response.content.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertTrue(any(item["fields"]["title"] == "Automated Manga Translator" for item in data))

    def test_get_projects_json_filter(self):
        response = self.client.get(reverse("main:get_projects_json") + "?title=Manga")
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["fields"]["title"], self.project.title)

        response_empty = self.client.get(reverse("main:get_projects_json") + "?title=NotExisting")
        data_empty = json.loads(response_empty.content.decode("utf-8"))
        self.assertEqual(len(data_empty), 0)