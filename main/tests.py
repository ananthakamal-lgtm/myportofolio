import json
import uuid
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project, Achievement


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
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_projects")}"')
        self.assertContains(response, 'id="experience-loading"')
        self.assertContains(response, 'id="experience-error"')
        self.assertContains(response, 'id="experience-empty"')
        self.assertContains(response, 'id="experience-grid"')

        # Data diambil via endpoint JSON
        data = self.client.get(reverse("main:get_experience_json")).json()
        fields = data[0]["fields"]
        self.assertEqual(fields["title"], self.experience.title)
        self.assertEqual(fields["description"], self.experience.description)
        self.assertEqual(fields["category_display"], "Part-Time")
        self.assertTrue(fields["is_ongoing"])

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")
        self.assertEqual(self.client.get(reverse("main:get_experience_json")).json(), [])

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        data = self.client.get(reverse("main:get_experience_json")).json()

        self.assertFalse(self.experience.is_ongoing)
        self.assertFalse(data[0]["fields"]["is_ongoing"])
        self.assertIsNotNone(data[0]["fields"]["ended_at"])


class ExperienceCRUDTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin_exp",
            password="AdminPassword123!",
            email="admin_exp@example.com",
        )
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
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("main:create_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, "Add New Experience")

    def test_create_experience_post_valid(self):
        self.client.force_login(self.superuser)
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
        self.client.force_login(self.superuser)
        initial_count = Experience.objects.count()
        response = self.client.post(reverse("main:create_experience"), {"title": ""})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Experience.objects.count(), initial_count)
        self.assertFormError(response.context["form"], "title", "This field is required.")

    def test_update_experience_get(self):
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("main:update_experience", kwargs={"experience_id": self.experience.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")
        self.assertContains(response, "Edit Experience")
        self.assertContains(response, self.experience.title)

    def test_update_experience_post_valid(self):
        self.client.force_login(self.superuser)
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
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("main:update_experience", kwargs={"experience_id": uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_experience_post(self):
        self.client.force_login(self.superuser)
        exp_id = self.experience.id
        response = self.client.post(
            reverse("main:delete_experience", kwargs={"experience_id": exp_id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(id=exp_id).exists())

    def test_delete_experience_get_redirects_without_deleting(self):
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("main:delete_experience", kwargs={"experience_id": self.experience.id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Experience.objects.filter(id=self.experience.id).exists())

    def test_delete_experience_nonexistent_returns_404(self):
        self.client.force_login(self.superuser)
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
        self.assertContains(response, 'value="Software"')

    def test_show_experience_search_non_matching(self):
        response = self.client.get(reverse("main:show_experience") + "?title=NotFoundTitle123")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="NotFoundTitle123"')


class ProjectTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin_test",
            password="admin_password",
            email="admin@example.com",
        )
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
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, 'id="loading"')
        self.assertContains(response, 'id="error"')
        self.assertContains(response, 'id="empty"')
        self.assertContains(response, 'id="grid"')

    def test_empty_projects_page(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Belum ada proyek yang ditambahkan atau ditemukan.")

    def test_create_project_get(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("main:create_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, "Add New Project")

    def test_create_project_post_valid(self):
        self.client.force_login(self.superuser)
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
        self.client.force_login(self.superuser)
        initial_count = Project.objects.count()
        response = self.client.post(reverse("main:create_project"), {"title": ""})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.count(), initial_count)
        self.assertFormError(response.context["form"], "title", "This field is required.")

    def test_update_project_get(self):
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("main:update_project", kwargs={"project_id": self.project.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")
        self.assertContains(response, "Edit Project")
        self.assertContains(response, self.project.title)

    def test_update_project_post_valid(self):
        self.client.force_login(self.superuser)
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
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("main:update_project", kwargs={"project_id": uuid.uuid4()})
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_project_post(self):
        self.client.force_login(self.superuser)
        project_id = self.project.id
        response = self.client.post(
            reverse("main:delete_project", kwargs={"project_id": project_id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(id=project_id).exists())

    def test_delete_project_get_redirects_without_deleting(self):
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("main:delete_project", kwargs={"project_id": self.project.id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_delete_nonexistent_project_returns_404(self):
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse("main:delete_project", kwargs={"project_id": uuid.uuid4()})
        )

        self.assertEqual(response.status_code, 404)

    def test_projects_search_matching(self):
        response = self.client.get(reverse("main:show_projects") + "?title=Manga")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Manga"')

    def test_projects_search_non_matching(self):
        response = self.client.get(reverse("main:show_projects") + "?title=NonExistentProject123")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="NonExistentProject123"')

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


class AuthTest(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "ValidPassword123!"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_register_page_get(self):
        response = self.client.get(reverse("main:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")
        self.assertContains(response, "Buat Akun")

    def test_register_post_success(self):
        data = {
            "username": "newuser",
            "password1": "ComplexPass123!@",
            "password2": "ComplexPass123!@",
        }
        response = self.client.post(reverse("main:register"), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:login"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_post_password_mismatch(self):
        data = {
            "username": "mismatchuser",
            "password1": "ComplexPass123!@",
            "password2": "DifferentPass123!@",
        }
        response = self.client.post(reverse("main:register"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="mismatchuser").exists())

    def test_login_page_get(self):
        response = self.client.get(reverse("main:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")
        self.assertContains(response, "Login")

    def test_login_post_success_and_cookie(self):
        data = {
            "username": self.username,
            "password": self.password,
        }
        response = self.client.post(reverse("main:login"), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertIn("last_login", response.cookies)
        self.assertTrue(response.cookies["last_login"].value)

    def test_login_post_invalid(self):
        data = {
            "username": self.username,
            "password": "wrongpassword",
        }
        response = self.client.post(reverse("main:login"), data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("last_login", response.cookies)

    def test_logout_deletes_cookie(self):
        self.client.login(username=self.username, password=self.password)
        self.client.cookies["last_login"] = "2026-09-27 12:00:00"
        response = self.client.get(reverse("main:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertEqual(response.cookies["last_login"].value, "")

    def test_show_main_last_login_cookie_display(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Belum ada sesi login / Cookie tidak ditemukan")

        self.client.cookies["last_login"] = "2026-09-27 15:30:00"
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2026-09-27 15:30:00")

    def test_navbar_guest(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, f'href="{reverse("main:login")}"')
        self.assertContains(response, f'href="{reverse("main:register")}"')
        self.assertNotContains(response, reverse("main:logout"))

    def test_navbar_authenticated(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, self.username)
        self.assertContains(response, f'href="{reverse("main:logout")}"')
        self.assertNotContains(response, f'href="{reverse("main:login")}"')


class AuthorizationAndStarTest(TestCase):
    def setUp(self):
        self.regular_user = User.objects.create_user(
            username="regular_user",
            password="RegularPassword123!",
        )
        self.superuser = User.objects.create_superuser(
            username="super_user",
            password="SuperPassword123!",
            email="super@example.com",
        )
        self.project = Project.objects.create(
            title="Star Project",
            category="Web Dev",
            description="Testing stars and authorization",
            year=2026,
            tech_stack="Django, HTML",
        )

    def test_guest_cannot_access_create_project(self):
        response = self.client.get(reverse("main:create_project"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_regular_user_forbidden_create_project(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse("main:create_project"))
        self.assertEqual(response.status_code, 403)

    def test_guest_cannot_delete_project(self):
        response = self.client.post(
            reverse("main:delete_project", kwargs={"project_id": self.project.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_regular_user_forbidden_delete_project(self):
        self.client.force_login(self.regular_user)
        response = self.client.post(
            reverse("main:delete_project", kwargs={"project_id": self.project.id})
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_guest_cannot_toggle_star(self):
        response = self.client.post(
            reverse("main:toggle_star", kwargs={"project_id": self.project.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_authenticated_user_can_star_and_unstar(self):
        self.client.force_login(self.regular_user)
        url = reverse("main:toggle_star", kwargs={"project_id": self.project.id})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertIn(self.regular_user, self.project.starred_by.all())
        self.assertEqual(self.project.starred_by.count(), 1)

        response2 = self.client.post(url)
        self.assertEqual(response2.status_code, 302)
        self.assertRedirects(response2, reverse("main:show_projects"))
        self.assertNotIn(self.regular_user, self.project.starred_by.all())
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_projects_page_star_and_buttons_visibility(self):
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "project-add-button")
        self.assertNotContains(response, 'id="add-project-modal"')

        self.client.force_login(self.regular_user)
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "project-add-button")
        self.assertNotContains(response, 'id="add-project-modal"')

        self.client.force_login(self.superuser)
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "project-add-button")
        self.assertContains(response, 'id="add-project-modal"')

    def test_get_projects_json_includes_natural_keys(self):
        self.project.starred_by.add(self.regular_user)
        response = self.client.get(reverse("main:get_projects_json"))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode("utf-8"))
        target = next(item for item in data if item["pk"] == str(self.project.id))
        self.assertEqual(target["fields"]["starred_by"], [[self.regular_user.username]])

class ExperienceAuthorizationAndStarTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group
        self.editor_group, _ = Group.objects.get_or_create(name="Editor")

        self.regular_user = User.objects.create_user(
            username="regular_exp_user",
            password="RegularPassword123!",
        )

        self.editor_user = User.objects.create_user(
            username="editor_exp_user",
            password="EditorPassword123!",
        )
        self.editor_user.groups.add(self.editor_group)

        self.superuser = User.objects.create_superuser(
            username="superuser_exp_user",
            password="SuperPassword123!",
            email="superuser_exp@example.com",
        )

        self.experience = Experience.objects.create(
            title="Backend Engineer Intern",
            category="internship",
            description="Mengembangkan microservices.",
        )

        self.project = Project.objects.create(
            title="Search Engine",
            category="Web Dev",
            description="Search engine.",
            year=2026,
            tech_stack="Python, Elasticsearch",
        )

    def test_guest_redirected_to_login(self):
        # Create
        res_create_get = self.client.get(reverse("main:create_experience"))
        self.assertEqual(res_create_get.status_code, 302)
        self.assertIn("/login/", res_create_get.url)

        res_create_post = self.client.post(reverse("main:create_experience"), {"title": "X"})
        self.assertEqual(res_create_post.status_code, 302)
        self.assertIn("/login/", res_create_post.url)

        # Update
        res_update_get = self.client.get(reverse("main:update_experience", kwargs={"experience_id": self.experience.id}))
        self.assertEqual(res_update_get.status_code, 302)
        self.assertIn("/login/", res_update_get.url)

        res_update_post = self.client.post(reverse("main:update_experience", kwargs={"experience_id": self.experience.id}), {"title": "X"})
        self.assertEqual(res_update_post.status_code, 302)
        self.assertIn("/login/", res_update_post.url)

        # Delete
        res_del = self.client.post(reverse("main:delete_experience", kwargs={"experience_id": self.experience.id}))
        self.assertEqual(res_del.status_code, 302)
        self.assertIn("/login/", res_del.url)

        # Star
        res_star = self.client.post(reverse("main:toggle_experience_star", kwargs={"experience_id": self.experience.id}))
        self.assertEqual(res_star.status_code, 302)
        self.assertIn("/login/", res_star.url)
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_regular_user_permissions(self):
        self.client.force_login(self.regular_user)

        # Create -> 403 Forbidden
        res_create_get = self.client.get(reverse("main:create_experience"))
        self.assertEqual(res_create_get.status_code, 403)

        res_create_post = self.client.post(reverse("main:create_experience"), {
            "title": "Unauthorized Add",
            "category": "internship",
            "description": "Not allowed",
        })
        self.assertEqual(res_create_post.status_code, 403)

        # Update -> 403 Forbidden
        res_update_get = self.client.get(reverse("main:update_experience", kwargs={"experience_id": self.experience.id}))
        self.assertEqual(res_update_get.status_code, 403)

        res_update_post = self.client.post(reverse("main:update_experience", kwargs={"experience_id": self.experience.id}), {
            "title": "Unauthorized Edit",
            "category": "internship",
            "description": "Not allowed",
        })
        self.assertEqual(res_update_post.status_code, 403)

        # Delete -> 403 Forbidden
        res_del = self.client.post(reverse("main:delete_experience", kwargs={"experience_id": self.experience.id}))
        self.assertEqual(res_del.status_code, 403)

        # Star / Unstar -> Allowed!
        star_url = reverse("main:toggle_experience_star", kwargs={"experience_id": self.experience.id})
        res_star1 = self.client.post(star_url)
        self.assertEqual(res_star1.status_code, 302)
        self.assertIn(self.regular_user, self.experience.starred_by.all())
        self.assertEqual(self.experience.starred_by.count(), 1)

        res_star2 = self.client.post(star_url)
        self.assertEqual(res_star2.status_code, 302)
        self.assertNotIn(self.regular_user, self.experience.starred_by.all())
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_editor_permissions(self):
        self.client.force_login(self.editor_user)

        # Cannot Create -> 403 Forbidden
        res_create = self.client.post(reverse("main:create_experience"), {
            "title": "Editor Should Not Create",
            "category": "internship",
            "description": "Not allowed",
        })
        self.assertEqual(res_create.status_code, 403)

        # Cannot Delete -> 403 Forbidden
        res_del = self.client.post(reverse("main:delete_experience", kwargs={"experience_id": self.experience.id}))
        self.assertEqual(res_del.status_code, 403)
        self.assertTrue(Experience.objects.filter(id=self.experience.id).exists())

        # Can Update Experience -> Allowed!
        res_update_get = self.client.get(reverse("main:update_experience", kwargs={"experience_id": self.experience.id}))
        self.assertEqual(res_update_get.status_code, 200)

        res_update_post = self.client.post(reverse("main:update_experience", kwargs={"experience_id": self.experience.id}), {
            "title": "Updated by Editor",
            "category": "internship",
            "description": "Deskripsi diperbarui oleh editor.",
        })
        self.assertEqual(res_update_post.status_code, 302)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Updated by Editor")

        # Can Update Project -> Allowed!
        res_proj_update = self.client.post(reverse("main:update_project", kwargs={"project_id": self.project.id}), {
            "title": "Updated Project by Editor",
            "category": "Web Dev",
            "description": "Updated desc.",
            "year": 2026,
            "tech_stack": "Python",
        })
        self.assertEqual(res_proj_update.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Updated Project by Editor")

        # Cannot Create Project -> 403
        res_proj_create = self.client.post(reverse("main:create_project"), {"title": "X"})
        self.assertEqual(res_proj_create.status_code, 403)

        # Cannot Delete Project -> 403
        res_proj_del = self.client.post(reverse("main:delete_project", kwargs={"project_id": self.project.id}))
        self.assertEqual(res_proj_del.status_code, 403)

        # Can Star Experience -> Allowed!
        star_url = reverse("main:toggle_experience_star", kwargs={"experience_id": self.experience.id})
        res_star = self.client.post(star_url)
        self.assertEqual(res_star.status_code, 302)
        self.assertEqual(self.experience.starred_by.count(), 1)

    def test_superuser_full_permissions(self):
        self.client.force_login(self.superuser)

        # Can Create
        res_create = self.client.post(reverse("main:create_experience"), {
            "title": "Superuser Experience",
            "category": "full-time",
            "description": "Dibuat oleh admin.",
        })
        self.assertEqual(res_create.status_code, 302)
        new_exp = Experience.objects.get(title="Superuser Experience")

        # Can Update
        res_update = self.client.post(reverse("main:update_experience", kwargs={"experience_id": new_exp.id}), {
            "title": "Superuser Experience Edited",
            "category": "full-time",
            "description": "Diperbarui oleh admin.",
        })
        self.assertEqual(res_update.status_code, 302)
        new_exp.refresh_from_db()
        self.assertEqual(new_exp.title, "Superuser Experience Edited")

        # Can Delete
        res_del = self.client.post(reverse("main:delete_experience", kwargs={"experience_id": new_exp.id}))
        self.assertEqual(res_del.status_code, 302)
        self.assertFalse(Experience.objects.filter(id=new_exp.id).exists())

    def test_experience_template_action_buttons_visibility(self):
        # Guest
        res_guest = self.client.get(reverse("main:show_experience"))
        self.assertEqual(res_guest.status_code, 200)
        self.assertNotContains(res_guest, "project-add-button")
        self.assertNotContains(res_guest, 'id="add-experience-modal"')
        self.assertContains(res_guest, 'data-is-authenticated="false"')
        self.assertContains(res_guest, 'data-can-edit="false"')
        self.assertContains(res_guest, 'data-can-delete="false"')

        # Regular user
        self.client.force_login(self.regular_user)
        res_regular = self.client.get(reverse("main:show_experience"))
        self.assertEqual(res_regular.status_code, 200)
        self.assertNotContains(res_regular, "project-add-button")
        self.assertNotContains(res_regular, 'id="add-experience-modal"')
        self.assertContains(res_regular, 'data-is-authenticated="true"')
        self.assertContains(res_regular, 'data-can-edit="false"')
        self.assertContains(res_regular, 'data-can-delete="false"')

        # Editor
        self.client.force_login(self.editor_user)
        res_editor = self.client.get(reverse("main:show_experience"))
        self.assertEqual(res_editor.status_code, 200)
        self.assertNotContains(res_editor, "project-add-button")
        self.assertNotContains(res_editor, 'id="add-experience-modal"')
        self.assertContains(res_editor, 'data-is-authenticated="true"')
        self.assertContains(res_editor, 'data-can-edit="true"')
        self.assertContains(res_editor, 'data-can-delete="false"')

        # Superuser
        self.client.force_login(self.superuser)
        res_super = self.client.get(reverse("main:show_experience"))
        self.assertEqual(res_super.status_code, 200)
        self.assertContains(res_super, "project-add-button")
        self.assertContains(res_super, 'id="add-experience-modal"')
        self.assertContains(res_super, 'data-is-authenticated="true"')
        self.assertContains(res_super, 'data-can-edit="true"')
        self.assertContains(res_super, 'data-can-delete="true"')

    def test_get_experience_json_security(self):
        res = self.client.get(reverse("main:get_experience_json"))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content.decode("utf-8"))
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        for item in data:
            self.assertIn("title", item["fields"])
            self.assertIn("category", item["fields"])
            self.assertIn("description", item["fields"])
            self.assertNotIn("password", item["fields"])


class Tutorial5AJAXAndXSSTest(TestCase):
    def setUp(self):
        self.regular_user = User.objects.create_user(
            username="regular_tut5",
            password="RegularPassword123!",
        )
        self.superuser = User.objects.create_superuser(
            username="super_tut5",
            password="SuperPassword123!",
            email="super_tut5@example.com",
        )
        self.project = Project.objects.create(
            title="Interactive Portfolio",
            category="Web Development",
            description="A modern portfolio built with Django and AJAX.",
            year=2026,
            tech_stack="Django, JavaScript, HTML, CSS",
            demo_url="https://example.com/demo",
            repo_url="https://github.com/example/repo",
        )

    def test_create_project_ajax_guest_forbidden(self):
        response = self.client.post(reverse("main:create_project_ajax"), {
            "title": "Guest Project",
            "category": "Web Dev",
            "description": "Attempting to create",
            "year": 2026,
            "tech_stack": "Django",
        })
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content.decode("utf-8"))
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Hanya pemilik portofolio yang dapat menambahkan proyek.")

    def test_create_project_ajax_regular_user_forbidden(self):
        self.client.force_login(self.regular_user)
        response = self.client.post(reverse("main:create_project_ajax"), {
            "title": "Regular User Project",
            "category": "Web Dev",
            "description": "Attempting to create",
            "year": 2026,
            "tech_stack": "Django",
        })
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content.decode("utf-8"))
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Hanya pemilik portofolio yang dapat menambahkan proyek.")

    def test_create_project_ajax_superuser_success(self):
        self.client.force_login(self.superuser)
        response = self.client.post(reverse("main:create_project_ajax"), {
            "title": "New AJAX Project",
            "category": "Machine Learning",
            "description": "Project created asynchronously.",
            "year": 2026,
            "tech_stack": "Python, Django, JS",
            "demo_url": "https://example.com/ajax-demo",
            "repo_url": "https://github.com/example/ajax-repo",
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content.decode("utf-8"))
        self.assertIn("pk", data)
        self.assertEqual(data["message"], "Proyek berhasil ditambahkan.")
        self.assertTrue(Project.objects.filter(title="New AJAX Project").exists())

    def test_create_project_ajax_invalid(self):
        self.client.force_login(self.superuser)
        response = self.client.post(reverse("main:create_project_ajax"), {
            "title": "",
            "category": "Web Dev",
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode("utf-8"))
        self.assertIn("errors", data)
        self.assertIn("title", data["errors"])

    def test_create_project_ajax_method_not_allowed(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("main:create_project_ajax"))
        self.assertEqual(response.status_code, 405)

    def test_project_form_clean_title_xss_empty(self):
        form = ProjectForm(data={
            "title": '<img src="x" onerror="alert(1)">',
            "category": "Security",
            "description": "Testing XSS",
            "year": 2026,
            "tech_stack": "Security",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("Nama proyek tidak boleh hanya berisi tag HTML.", form.errors["title"])

    def test_project_form_clean_fields_strip_tags(self):
        form = ProjectForm(data={
            "title": 'Safe Title <b>Bold</b>',
            "category": 'Web <script>alert("hack")</script>',
            "description": 'Description with <i>italics</i> and <script>bad()</script>',
            "year": 2026,
            "tech_stack": 'Python, <style>body{}</style>Django',
        })
        self.assertTrue(form.is_valid())
        cleaned = form.cleaned_data
        self.assertEqual(cleaned["title"], "Safe Title Bold")
        self.assertEqual(cleaned["category"], "Web alert(\"hack\")")
        self.assertEqual(cleaned["description"], "Description with italics and bad()")
        self.assertEqual(cleaned["tech_stack"], "Python, body{}Django")

    def test_get_projects_json_star_info(self):
        self.project.starred_by.add(self.regular_user)

        # Unauthenticated: is_starred is False
        res_guest = self.client.get(reverse("main:get_projects_json"))
        self.assertEqual(res_guest.status_code, 200)
        data_guest = json.loads(res_guest.content.decode("utf-8"))
        proj_guest = next(p for p in data_guest if p["pk"] == str(self.project.id))
        self.assertEqual(proj_guest["fields"]["star_count"], 1)
        self.assertFalse(proj_guest["fields"]["is_starred"])
        self.assertIn(self.regular_user.username, proj_guest["fields"]["starred_by_names"])

        # Authenticated as regular user: is_starred is True
        self.client.force_login(self.regular_user)
        res_user = self.client.get(reverse("main:get_projects_json"))
        data_user = json.loads(res_user.content.decode("utf-8"))
        proj_user = next(p for p in data_user if p["pk"] == str(self.project.id))
        self.assertTrue(proj_user["fields"]["is_starred"])

        # Authenticated as superuser: is_starred is False
        self.client.force_login(self.superuser)
        res_super = self.client.get(reverse("main:get_projects_json"))
        data_super = json.loads(res_super.content.decode("utf-8"))
        proj_super = next(p for p in data_super if p["pk"] == str(self.project.id))
        self.assertFalse(proj_super["fields"]["is_starred"])


class Tugas5ExperienceAJAXTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group
        self.editor_group, _ = Group.objects.get_or_create(name="Editor")

        self.regular_user = User.objects.create_user(
            username="regular_tugas5",
            password="RegularPassword123!",
        )
        self.editor_user = User.objects.create_user(
            username="editor_tugas5",
            password="EditorPassword123!",
        )
        self.editor_user.groups.add(self.editor_group)

        self.superuser = User.objects.create_superuser(
            username="super_tugas5",
            password="SuperPassword123!",
            email="super_tugas5@example.com",
        )
        self.experience = Experience.objects.create(
            title="Software Engineering Intern",
            category="internship",
            description="Developing scalable backend services.",
            thumbnail="https://example.com/logo.png",
        )

    def test_create_experience_ajax_guest_forbidden(self):
        response = self.client.post(reverse("main:create_experience_ajax"), {
            "title": "Guest Experience",
            "category": "internship",
            "description": "Attempting to create",
        })
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Hanya pemilik portofolio yang dapat menambahkan pengalaman.")

    def test_create_experience_ajax_regular_user_forbidden(self):
        self.client.force_login(self.regular_user)
        response = self.client.post(reverse("main:create_experience_ajax"), {
            "title": "Regular Experience",
            "category": "internship",
            "description": "Attempting to create",
        })
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Hanya pemilik portofolio yang dapat menambahkan pengalaman.")

    def test_create_experience_ajax_editor_user_forbidden(self):
        self.client.force_login(self.editor_user)
        response = self.client.post(reverse("main:create_experience_ajax"), {
            "title": "Editor Experience",
            "category": "internship",
            "description": "Editor cannot create",
        })
        self.assertEqual(response.status_code, 403)

    def test_create_experience_ajax_superuser_success(self):
        self.client.force_login(self.superuser)
        response = self.client.post(reverse("main:create_experience_ajax"), {
            "title": "AI Research Assistant",
            "category": "research",
            "description": "Working on NLP and transformers.",
            "thumbnail": "https://example.com/ai.png",
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("pk", data)
        self.assertEqual(data["message"], "Pengalaman baru berhasil ditambahkan.")
        self.assertTrue(Experience.objects.filter(title="AI Research Assistant").exists())

    def test_create_experience_ajax_invalid(self):
        self.client.force_login(self.superuser)
        response = self.client.post(reverse("main:create_experience_ajax"), {
            "title": "",
            "category": "internship",
            "description": "",
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("errors", data)
        self.assertIn("title", data["errors"])

    def test_create_experience_ajax_method_not_allowed(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("main:create_experience_ajax"))
        self.assertEqual(response.status_code, 405)

    def test_experience_form_clean_title_xss_empty(self):
        form = ExperienceForm(data={
            "title": '<img src="x" onerror="alert(1)">',
            "category": "internship",
            "description": "Valid description",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("Judul pengalaman tidak boleh hanya berisi tag HTML.", form.errors["title"])

    def test_experience_form_clean_description_xss_empty(self):
        form = ExperienceForm(data={
            "title": "Valid Title",
            "category": "internship",
            "description": '<img src="x" onerror="alert(1)">',
        })
        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)
        self.assertIn("Deskripsi pengalaman tidak boleh hanya berisi tag HTML.", form.errors["description"])

    def test_experience_form_clean_fields_strip_tags(self):
        form = ExperienceForm(data={
            "title": 'Intern <b>Lead</b>',
            "category": "internship",
            "description": 'Doing <i>cool</i> tasks <script>bad()</script>',
        })
        self.assertTrue(form.is_valid())
        cleaned = form.cleaned_data
        self.assertEqual(cleaned["title"], "Intern Lead")
        self.assertEqual(cleaned["description"], "Doing cool tasks bad()")

    def test_get_experience_json_star_info(self):
        self.experience.starred_by.add(self.regular_user)

        # Guest
        res_guest = self.client.get(reverse("main:get_experience_json"))
        self.assertEqual(res_guest.status_code, 200)
        data_guest = res_guest.json()
        target_guest = next(x for x in data_guest if x["pk"] == str(self.experience.id))
        self.assertEqual(target_guest["fields"]["star_count"], 1)
        self.assertFalse(target_guest["fields"]["is_starred"])
        self.assertIn(self.regular_user.username, target_guest["fields"]["starred_by_names"])

        # Authenticated as regular user (who starred)
        self.client.force_login(self.regular_user)
        res_user = self.client.get(reverse("main:get_experience_json"))
        data_user = res_user.json()
        target_user = next(x for x in data_user if x["pk"] == str(self.experience.id))
        self.assertTrue(target_user["fields"]["is_starred"])

    def test_toggle_experience_star_ajax_json_response(self):
        self.client.force_login(self.regular_user)
        star_url = reverse("main:toggle_experience_star", kwargs={"experience_id": self.experience.id})

        # Request with Accept: application/json
        response = self.client.post(star_url, HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["fields"]["star_count"], 1)
        self.assertTrue(data["fields"]["is_starred"])

        # Toggle again
        response2 = self.client.post(star_url, HTTP_ACCEPT="application/json")
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertEqual(data2["fields"]["star_count"], 0)
        self.assertFalse(data2["fields"]["is_starred"])
