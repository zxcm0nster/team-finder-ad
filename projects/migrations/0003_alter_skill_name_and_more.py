# Skill.name max_length per spec (124)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0002_skill_project_skills"),
    ]

    operations = [
        migrations.AlterField(
            model_name="skill",
            name="name",
            field=models.CharField(
                max_length=124,
                unique=True,
                verbose_name="Название навыка",
            ),
        ),
    ]
