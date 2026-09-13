from django.shortcuts import render

from main.models import Experience, Project


def show_main(request):
    context = {
        "name": "Anantha",
        "npm": "2506656425",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada pengembangan perangkat lunak dan pendidikan."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Anantha",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


def show_projects(request):
    context = {
        "name": "Anantha",
        "project_list": Project.objects.all(),
    }
    return render(request, "projects.html", context)
