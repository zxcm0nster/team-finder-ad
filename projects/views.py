import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from team_finder.utils import parse_json_body

from .forms import ProjectForm
from .models import STATUS_CLOSED, STATUS_OPEN, Project, Skill

# Константы (PEP 8)
PAGINATE_BY_COUNT = 6
MAX_SKILLS_SEARCH_RESULT = 10


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    paginate_by = PAGINATE_BY_COUNT

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
    search_query = request.GET.get("q", "").strip()
    if not search_query:
        return JsonResponse([], safe=False)

    skills = Skill.objects.filter(name__istartswith=search_query).order_by("name")[:MAX_SKILLS_SEARCH_RESULT]
    data = [{"id": skill.id, "name": skill.name} for skill in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_http_methods(["POST"])
def add_skill_to_project(request, project_id):
    project = Project.objects.filter(id=project_id).first()
    if not project:
        return JsonResponse({"error": "Проект не найден"}, status=HTTPStatus.NOT_FOUND)

    if request.user != project.owner:
        return JsonResponse({"error": "Доступ запрещен"}, status=HTTPStatus.FORBIDDEN)

    payload = parse_json_body(request)
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
            return JsonResponse({"error": "Неверные данные"}, status=HTTPStatus.BAD_REQUEST)

    created = False
    if skill_id is not None:
        skill = Skill.objects.filter(id=skill_id).first()
        if not skill:
            return JsonResponse({"error": "Навык не найден"}, status=HTTPStatus.NOT_FOUND)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"error": "Неверные данные"}, status=HTTPStatus.BAD_REQUEST)

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
    project = Project.objects.filter(id=project_id).first()
    if not project:
        return JsonResponse({"error": "Проект не найден"}, status=HTTPStatus.NOT_FOUND)

    if request.user != project.owner:
        return JsonResponse({"error": "Доступ запрещен"}, status=HTTPStatus.FORBIDDEN)

    skill = Skill.objects.filter(id=skill_id).first()
    if not skill:
        return JsonResponse({"error": "Навык не найден"}, status=HTTPStatus.NOT_FOUND)

    if not project.skills.filter(pk=skill.pk).exists():
        return JsonResponse(
            {"error": "Этот навык не привязан к проекту"},
            status=HTTPStatus.BAD_REQUEST,
        )
        
    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})


@login_required
@require_http_methods(["POST"])
def complete_project(request, project_id):
    project = Project.objects.filter(id=project_id, owner=request.user).first()
    if not project:
        return JsonResponse({"error": "Проект не найден"}, status=HTTPStatus.NOT_FOUND)
        
    if project.status != STATUS_OPEN:
        return JsonResponse({"status": "error", "message": "Уже закрыт"}, status=HTTPStatus.BAD_REQUEST)
        
    project.status = STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok"})


@login_required
@require_http_methods(["POST"])
def toggle_participate(request, project_id):
    project = Project.objects.filter(id=project_id).first()
    if not project:
        return JsonResponse({"error": "Проект не найден"}, status=HTTPStatus.NOT_FOUND)

    if project.owner_id == request.user.id:
        return JsonResponse({"status": "error", "message": "Владелец не может участвовать"}, status=HTTPStatus.FORBIDDEN)

    is_participant = project.participants.filter(pk=request.user.pk).exists()
    if is_participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
        
    return JsonResponse({"status": "ok", "participant": not is_participant})


@login_required
@require_http_methods(["POST"])
def toggle_favorite(request, project_id):
    project = Project.objects.filter(id=project_id).first()
    if not project:
        return JsonResponse({"error": "Проект не найден"}, status=HTTPStatus.NOT_FOUND)

    profile = request.user.profile
    is_favorite = profile.favorite_projects.filter(pk=project.pk).exists()
    
    if is_favorite:
        profile.favorite_projects.remove(project)
    else:
        profile.favorite_projects.add(project)
        
    return JsonResponse({"status": "ok", "favorite": not is_favorite})


class FavoriteProjectListView(LoginRequiredMixin, ListView):
    template_name = "projects/favorite_projects.html"
    context_object_name = "projects"
    paginate_by = PAGINATE_BY_COUNT

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
        return reverse("projects:detail", kwargs={"pk": self.object.id})


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context

    def get_queryset(self):
        return self.request.user.owned_projects.all()

    def get_success_url(self):
        return reverse("projects:detail", kwargs={"pk": self.object.id})
