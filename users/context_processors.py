"""Шаблонный контекст"""


def favorite_project_ids(request):
    if request.user.is_authenticated:
        return {
            "favorite_project_ids": set(
                request.user.profile.favorite_projects.values_list("id", flat=True)
            )
        }
    return {"favorite_project_ids": set()}
