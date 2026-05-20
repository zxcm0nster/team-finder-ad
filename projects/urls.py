from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('list/', views.ProjectListView.as_view(), name='list'),
    path('create-project/', views.ProjectCreateView.as_view(), name='create'),
    path('skills/', views.search_skills, name='skills_search'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='edit'),
    path('<int:project_id>/skills/add/', views.add_skill_to_project, name='add_skill'),
    path('<int:project_id>/skills/<int:skill_id>/remove/', views.remove_skill_from_project, name='remove_skill'),
]
