# Generated by Django 2.1 on 2018-09-13 04:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.IntegerField(default=-1)),
                ('y', models.IntegerField(default=-1)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
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
        migrations.CreateModel(
            name='World',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('turn', models.IntegerField(default=0)),
                ('phase', models.IntegerField(default=-1)),
                ('size_x', models.IntegerField(default=50)),
                ('size_y', models.IntegerField(default=50)),
            ],
        ),
        migrations.AddField(
            model_name='location',
            name='world',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='world.World'),
        ),
    ]
