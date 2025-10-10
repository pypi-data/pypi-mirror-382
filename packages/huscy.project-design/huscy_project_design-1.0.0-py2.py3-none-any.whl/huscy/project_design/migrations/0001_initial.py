import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0004_remove_project_project_manager'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DataAcquisitionMethodType',
            fields=[
                ('short_name', models.CharField(editable=False, max_length=32, primary_key=True, serialize=False, verbose_name='Short name')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Data acquisition method type',
                'verbose_name_plural': 'Data acquisition method types',
                'ordering': ('short_name',),
            },
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(blank=True, default='', verbose_name='Description')),
                ('order', models.PositiveSmallIntegerField(verbose_name='Order')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiments', to='projects.project', verbose_name='Project')),
            ],
            options={
                'verbose_name': 'Experiment',
                'verbose_name_plural': 'Experiments',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(blank=True, default='', verbose_name='Description')),
                ('order', models.PositiveSmallIntegerField(verbose_name='Order')),
                ('contacts', models.ManyToManyField(related_name='+', to=settings.AUTH_USER_MODEL)),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='project_design.experiment', verbose_name='Experiment')),
            ],
            options={
                'verbose_name': 'Session',
                'verbose_name_plural': 'Sessions',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='DataAcquisitionMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stimulus', models.CharField(blank=True, choices=[('auditive', 'Auditive'), ('gustatory', 'Gustatory'), ('olfactory', 'Olfactory'), ('somatosensory', 'Somatosensory'), ('visual', 'Visual')], max_length=16, null=True, verbose_name='Stimulus')),
                ('duration', models.DurationField(verbose_name='Duration')),
                ('location', models.CharField(blank=True, max_length=255, null=True, verbose_name='Location')),
                ('order', models.PositiveSmallIntegerField(verbose_name='Order')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='project_design.dataacquisitionmethodtype', verbose_name='Type')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_acquisition_methods', to='project_design.session', verbose_name='Session')),
            ],
            options={
                'verbose_name': 'Data acquisition method',
                'verbose_name_plural': 'Data acquisition methods',
                'ordering': ('order',),
            },
        ),
    ]
