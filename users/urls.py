from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.custom_logout, name="logout"),
    path("<int:id>/", views.UserDetailView.as_view(), name="user_detail"),
    path("list/", views.ParticipantListView.as_view(), name="list"),
    path("<int:user_id>/edit/", views.edit_profile, name="edit_profile"),
    path("<int:user_id>/password/", views.change_password, name="change_password"),
]
