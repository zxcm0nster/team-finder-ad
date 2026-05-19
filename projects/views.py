import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView
from .models import Project, Skill

class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    paginate_by = 6  # Количество проектов на одной странице
    
    def get_queryset(self):
        # Выводим только проекты со статусом "Open" и сортируем по дате создания
        queryset = Project.objects.filter(status='open').order_by('-created_at')
        
        # Читаем параметр skill из URL (?skill=Python)
        skill_name = self.request.GET.get('skill')
        if skill_name:
            # Оставляем только те проекты, у которых есть навык с таким именем
            # distinct() нужен, чтобы проекты не дублировались в выдаче
            queryset = queryset.filter(skills__name=skill_name).distinct()
            
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаем projects для проверки в шаблоне (чтобы показывать кнопку создания)
        context['projects'] = Project.objects.all()
        
        # Достаем все навыки из базы данных (уже отсортированные по алфавиту)
        context['all_skills'] = Skill.objects.all()
        context['active_skill'] = self.request.GET.get('skill', '')
        
        # Сохраняем параметры запроса для правильной работы пагинации с фильтрами
        skill = self.request.GET.get('skill')
        # Если навык выбран, добавляем его в ссылки страниц (например, ?skill=Python&page=2)
        context['query_prefix'] = f"skill={skill}&" if skill else ""
        
        return context

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'

# Поиск навыков (доступен всем)
def search_skills(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse([], safe=False)
    
    # Ищем навыки, в названии которых есть запрос q (регистронезависимо), берем первые 10
    skills = Skill.objects.filter(name__icontains=q)[:10]
    data = [{'id': skill.id, 'name': skill.name} for skill in skills]
    return JsonResponse(data, safe=False)


# Добавление навыка к проекту (только для авторизованных и только POST-запрос)
@login_required
@require_http_methods(["POST"])
def add_skill_to_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Защита: только владелец может добавлять навыки
    if request.user != project.owner:
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)
    
    data = json.loads(request.body)
    skill_id = data.get('skill_id')
    name = data.get('name')
    
    if skill_id:
        # Если пришел ID, берем существующий навык
        skill = get_object_or_404(Skill, id=skill_id)
    elif name:
        # Если пришло имя, ищем такой навык или создаем новый (get_or_create)
        skill, created = Skill.objects.get_or_create(name=name.strip())
    else:
        return JsonResponse({'error': 'Неверные данные'}, status=400)
        
    # Добавляем навык в проект (ManyToManyField сам следит, чтобы не было дублей)
    project.skills.add(skill)
    return JsonResponse({'id': skill.id, 'name': skill.name})


# Удаление навыка из проекта
@login_required
@require_http_methods(["POST"])
def remove_skill_from_project(request, project_id, skill_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.user != project.owner:
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)
        
    skill = get_object_or_404(Skill, id=skill_id)
    project.skills.remove(skill) # Удаляем связь, сам навык в базе остается
    return JsonResponse({'status': 'ok'})
