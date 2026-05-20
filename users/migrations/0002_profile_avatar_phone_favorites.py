# Generated manually for Profile optional avatar/phone + favorites

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
        ("projects", "0002_skill_project_skills"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="avatar",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="avatars/",
                verbose_name="Аватар",
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="phone",
            field=models.CharField(
                blank=True,
                default="",
                max_length=12,
                verbose_name="Телефон",
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="favorite_projects",
            field=models.ManyToManyField(
                blank=True,
                related_name="favorited_by_profiles",
                to="projects.project",
                verbose_name="Избранные проекты",
            ),
        ),
    ]
