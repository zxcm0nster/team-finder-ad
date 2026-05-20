from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static


def redirect_auth_to_users(request, path):
    if path:
        target = f"/users/{path}"
    else:
        target = "/users/list/"
    if request.GET:
        target = f"{target}?{request.GET.urlencode()}"
    return HttpResponseRedirect(target)


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^auth/(?P<path>.*)$", redirect_auth_to_users),
    path('users/', include('users.urls', namespace='users')),
    path('projects/', include('projects.urls', namespace='projects')),
    path('', RedirectView.as_view(url='/projects/list/', permanent=False), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
