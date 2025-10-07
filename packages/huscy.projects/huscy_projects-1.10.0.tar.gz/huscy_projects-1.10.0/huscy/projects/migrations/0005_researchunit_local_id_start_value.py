from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_remove_project_project_manager'),
    ]

    operations = [
        migrations.AddField(
            model_name='researchunit',
            name='local_id_start_value',
            field=models.PositiveIntegerField(default=1, verbose_name='Local ID start value'),
        ),
    ]
