import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

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


def serialize_experience(experience, user):
    starred_users = list(experience.starred_by.all())
    is_starred = user.is_authenticated and any(u.pk == user.pk for u in starred_users)

    return {
        "pk": str(experience.id),
        "fields": {
            "title": experience.title,
            "category": experience.category,
            "category_display": experience.get_category_display(),
            "description": experience.description,
            "thumbnail": experience.thumbnail or "",
            "started_at": experience.started_at.isoformat() if experience.started_at else None,
            "ended_at": experience.ended_at.isoformat() if experience.ended_at else None,
            "is_ongoing": experience.is_ongoing,
            "star_count": len(starred_users),
            "is_starred": is_starred,
            "starred_by_names": ", ".join(u.username for u in starred_users),
        },
    }


def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.prefetch_related("starred_by").order_by("-started_at")

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    data = [serialize_experience(exp, request.user) for exp in experiences]
    return JsonResponse(data, safe=False)


@ensure_csrf_cookie
def show_experience(request):
    ensure_portfolio_owner_superuser(request.user)
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Anantha",
        "title_query": title_query,
        "form": ExperienceForm(),
    }
    return render(request, "experience.html", context)


@require_POST
def create_experience_ajax(request):
    ensure_portfolio_owner_superuser(request.user)
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan pengalaman."},
            status=403,
        )

    form = ExperienceForm(request.POST)
    if form.is_valid():
        experience = form.save()
        return JsonResponse(
            {
                "message": "Pengalaman baru berhasil ditambahkan.",
                "pk": str(experience.id),
                "data": serialize_experience(experience, request.user),
            },
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@login_required(login_url="/login/")
def create_experience(request):
    ensure_portfolio_owner_superuser(request.user)
    if not request.user.is_superuser:
        raise PermissionDenied

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


@login_required(login_url="/login/")
def update_experience(request, experience_id):
    ensure_portfolio_owner_superuser(request.user)
    if not (
        request.user.is_superuser
        or request.user.groups.filter(name__iexact="Editor").exists()
        or request.user.has_perm("main.change_experience")
    ):
        raise PermissionDenied

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


@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    ensure_portfolio_owner_superuser(request.user)
    if not request.user.is_superuser:
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Pengalaman berhasil dihapus!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")


@login_required(login_url="/login/")
def toggle_experience_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        if experience.starred_by.filter(pk=request.user.pk).exists():
            experience.starred_by.remove(request.user)
        else:
            experience.starred_by.add(request.user)

        if "application/json" in request.headers.get("Accept", ""):
            experience = Experience.objects.prefetch_related("starred_by").get(pk=experience.pk)
            return JsonResponse(serialize_experience(experience, request.user))

    return redirect("main:show_experience")


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related('starred_by').all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    data = []
    for project in projects:
        starred_users = project.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "category": project.category,
                "description": project.description,
                "year": project.year,
                "tech_stack": project.tech_stack,
                "demo_url": project.demo_url,
                "repo_url": project.repo_url,
                "project_url": project.demo_url or project.repo_url or "",
                "project_image_url": "",
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
                "starred_by": [[u.username] for u in starred_users],
            }
        })

    return JsonResponse(data, safe=False)


def show_projects(request):
    ensure_portfolio_owner_superuser(request.user)
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Anantha",
        "title_query": title_query,
        "form": ProjectForm(),
    }
    return render(request, "projects.html", context)


@require_POST
def create_project_ajax(request):
    ensure_portfolio_owner_superuser(request.user)
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(project.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


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
    if not (
        request.user.is_superuser
        or request.user.groups.filter(name__iexact="Editor").exists()
        or request.user.has_perm("main.change_project")
    ):
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
