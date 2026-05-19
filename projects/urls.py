from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Путь будет выглядеть как /projects/list/
    path('list/', views.ProjectListView.as_view(), name='list'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
]
