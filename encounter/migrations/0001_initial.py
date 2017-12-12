# Generated by Django 2.0 on 2017-12-12 05:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('world', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Encounter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turn', models.IntegerField(default=0)),
                ('size_x', models.IntegerField(default=0)),
                ('size_y', models.IntegerField(default=0)),
                ('world', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='world.World')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.IntegerField(default=-1)),
                ('y', models.IntegerField(default=-1)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('encounter', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='encounter.Encounter')),
            ],
        ),
        migrations.CreateModel(
            name='Wall',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.IntegerField(default=-1)),
                ('y', models.IntegerField(default=-1)),
            ],
        ),
    ]
