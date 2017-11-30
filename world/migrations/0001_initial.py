# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-11-30 10:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('monster', '0001_initial'),
        ('character', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Arena',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arena_x', models.IntegerField(default=0)),
                ('arena_y', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Encounter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turn', models.IntegerField(default=0)),
                ('arena', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='world.Arena')),
                ('monster_types', models.ManyToManyField(blank=True, to='monster.Monster')),
                ('monsters', models.ManyToManyField(blank=True, to='monster.MonsterState')),
                ('pcs', models.ManyToManyField(blank=True, to='character.Character')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.IntegerField(default=-1)),
                ('y', models.IntegerField(default=-1)),
                ('object_id', models.PositiveIntegerField()),
                ('arena', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='world.Arena')),
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
            ],
        ),
        migrations.AddField(
            model_name='encounter',
            name='world',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='world.World'),
        ),
        migrations.AddField(
            model_name='arena',
            name='world',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='world.World'),
        ),
    ]
