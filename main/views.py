import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import PermissionDenied
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project, Achievement


_migration_checked = False


def ensure_portfolio_owner_superuser(user):
    global _migration_checked
    if not _migration_checked:
        try:
            from django.core.management import call_command
            call_command("migrate", interactive=False)
        except Exception:
            pass
        _migration_checked = True

    if user and user.is_authenticated and user.username.lower() in ["anantha.kamal", "anantha"]:
        if not user.is_superuser or not user.is_staff:
            user.is_superuser = True
            user.is_staff = True
            try:
                user.save(update_fields=["is_superuser", "is_staff"])
            except Exception:
                user.save()


def show_main(request):
    ensure_portfolio_owner_superuser(request.user)
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": "Anantha",
        "npm": "2506656425",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada pengembangan perangkat lunak dan pendidikan."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Anantha",
        "form": form,
    }
    return render(request, "register.html", context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        ensure_portfolio_owner_superuser(user)
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Anantha",
        "form": form,
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response


def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    experiences_json = serializers.serialize("json", experiences)
    return HttpResponse(experiences_json, content_type="application/json")


def show_experience(request):
    json_response = get_experience_json(request)

    experiences = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    experiences = [exp.object for exp in experiences]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Anantha",
        "experience_list": experiences,
        "title_query": title_query,
    }
    return render(request, "experience.html", context)


def create_experience(request):
    form = ExperienceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": "Anantha",
        "form": form,
        "page_title": "Add New Experience",
        "button_text": "Tambah Pengalaman",
    }
    return render(request, "experience_form.html", context)


def update_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman berhasil diperbarui!")
        return redirect("main:show_experience")

    context = {
        "name": "Anantha",
        "form": form,
        "experience": experience,
        "page_title": "Edit Experience",
        "button_text": "Simpan Perubahan",
    }
    return render(request, "experience_form.html", context)


def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Pengalaman berhasil dihapus!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize(
        "json", projects, use_natural_foreign_keys=True
    )
    return HttpResponse(projects_json, content_type="application/json")


def show_projects(request):
    ensure_portfolio_owner_superuser(request.user)
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Anantha",
        "project_list": projects,
        "title_query": title_query,
    }
    return render(request, "projects.html", context)


@login_required(login_url="/login/")
def create_project(request):
    ensure_portfolio_owner_superuser(request.user)
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Anantha",
        "form": form,
        "page_title": "Add New Project",
        "button_text": "Tambah Proyek",
    }
    return render(request, "projects_form.html", context)


@login_required(login_url="/login/")
def update_project(request, project_id):
    ensure_portfolio_owner_superuser(request.user)
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek berhasil diperbarui!")
        return redirect("main:show_projects")

    context = {
        "name": "Anantha",
        "form": form,
        "project": project,
        "page_title": "Edit Project",
        "button_text": "Simpan Perubahan",
    }
    return render(request, "projects_form.html", context)


@login_required(login_url="/login/")
def delete_project(request, project_id):
    ensure_portfolio_owner_superuser(request.user)
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")

    return redirect("main:show_projects")


@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_projects")


def show_achievements(request):
    achievement = Achievement.objects.order_by("-achieved_at")
    context = {
        'name':'Anantha',
        'achievement_list':achievement,
    }

    return render(request, 'achievements.html', context)
