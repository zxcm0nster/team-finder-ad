import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ProjectForm
from .models import Project, Skill


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    paginate_by = 6

    def get_queryset(self):
        queryset = Project.objects.all().order_by("-created_at")
        skill_name = self.request.GET.get("skill")
        if skill_name:
            queryset = queryset.filter(skills__name=skill_name).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_skills"] = Skill.objects.all().order_by("name")
        context["active_skill"] = self.request.GET.get("skill", "")
        skill = self.request.GET.get("skill")
        context["query_prefix"] = f"skill={skill}&" if skill else ""
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project-details.html"
    context_object_name = "project"


def search_skills(request):
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse([], safe=False)

    skills = Skill.objects.filter(name__istartswith=q).order_by("name")[:10]
    data = [{"id": skill.id, "name": skill.name} for skill in skills]
    return JsonResponse(data, safe=False)


def _parse_json_body(request):
    ctype = (request.content_type or "").lower()
    if "application/json" in ctype and request.body:
        try:
            return json.loads(request.body.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
    return {}


@login_required
@require_http_methods(["POST"])
def add_skill_to_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user != project.owner:
        return JsonResponse({"error": "Доступ запрещен"}, status=403)

    payload = _parse_json_body(request)
    if not payload and request.POST:
        payload = {
            "skill_id": request.POST.get("skill_id"),
            "name": request.POST.get("name"),
        }

    skill_id = payload.get("skill_id")
    name = (payload.get("name") or "").strip() if payload.get("name") else None

    if skill_id is not None:
        try:
            skill_id = int(skill_id)
        except (TypeError, ValueError):
            return JsonResponse({"error": "Неверные данные"}, status=400)

    created = False
    if skill_id is not None:
        skill = get_object_or_404(Skill, id=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"error": "Неверные данные"}, status=400)

    added = False
    if not project.skills.filter(pk=skill.pk).exists():
        project.skills.add(skill)
        added = True

    return JsonResponse(
        {
            "skill_id": skill.id,
            "name": skill.name,
            "created": created,
            "added": added,
        }
    )


@login_required
@require_http_methods(["POST"])
def remove_skill_from_project(request, project_id, skill_id):
    project = get_object_or_404(Project, id=project_id)

    if request.user != project.owner:
        return JsonResponse({"error": "Доступ запрещен"}, status=403)

    skill = get_object_or_404(Skill, id=skill_id)
    if not project.skills.filter(pk=skill.pk).exists():
        return JsonResponse(
            {"error": "Этот навык не привязан к проекту"},
            status=400,
        )
    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})


@login_required
@require_http_methods(["POST"])
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    if project.status != "open":
        return JsonResponse({"status": "error", "message": "Уже закрыт"}, status=400)
    project.status = "closed"
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok"})


@login_required
@require_http_methods(["POST"])
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner_id == request.user.id:
        return JsonResponse({"status": "error", "message": "Владелец не может участвовать"}, status=403)

    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        return JsonResponse({"status": "ok", "participant": False})

    project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": True})


@login_required
@require_http_methods(["POST"])
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    profile = request.user.profile
    if profile.favorite_projects.filter(pk=project.pk).exists():
        profile.favorite_projects.remove(project)
        return JsonResponse({"status": "ok", "favorite": False})
    profile.favorite_projects.add(project)
    return JsonResponse({"status": "ok", "favorite": True})


class FavoriteProjectListView(LoginRequiredMixin, ListView):
    template_name = "projects/favorite_projects.html"
    context_object_name = "projects"
    paginate_by = 6

    def get_queryset(self):
        return self.request.user.profile.favorite_projects.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query_prefix"] = ""
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = False
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        self.object.participants.add(self.request.user)
        return response

    def get_success_url(self):
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.id})


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.id})
