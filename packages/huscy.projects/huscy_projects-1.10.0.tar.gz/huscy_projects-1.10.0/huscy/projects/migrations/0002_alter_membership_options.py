from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='membership',
            options={'ordering': ('project', 'user'), 'verbose_name': 'Membership', 'verbose_name_plural': 'Memberships'},
        ),
    ]
