from django.views.generic import DetailView, ListView
from .models import Project

class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    paginate_by = 6  # Количество проектов на одной странице
    
    def get_queryset(self):
        # Выводим только проекты со статусом "Open" и сортируем по дате создания
        return Project.objects.filter(status='open').order_by('-created_at')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаем projects для проверки в шаблоне (чтобы показывать кнопку создания)
        context['projects'] = Project.objects.all()
        
        # Заглушки для фильтра по навыкам (пока его нет в базе)
        context['all_skills'] = []
        context['active_skill'] = self.request.GET.get('skill', '')
        
        # Сохраняем параметры запроса для правильной работы пагинации с фильтрами
        skill = self.request.GET.get('skill')
        context['query_prefix'] = f"skill={skill}&" if skill else ""
        
        return context

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'
