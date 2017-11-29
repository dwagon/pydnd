# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-11-28 07:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Monster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('treasure', models.CharField(max_length=50)),
                ('align', models.CharField(choices=[('LG', 'Lawful Good'), ('LN', 'Lawful Neutral'), ('LE', 'Lawful Evil'), ('NG', 'Neutral Good'), ('N', 'True Neutral'), ('NE', 'Neutral Evil'), ('CG', 'Chaotic Good'), ('CN', 'Chaotic Neutral'), ('CE', 'Chaotic Evil')], default='N', max_length=2)),
                ('numappearing', models.CharField(max_length=20, verbose_name='Num Appearing')),
                ('ac', models.IntegerField(verbose_name='AC')),
                ('movement', models.IntegerField(default=9)),
                ('hitdie', models.CharField(default='1d8', max_length=5, verbose_name='Hit Die')),
                ('thaco', models.IntegerField()),
                ('numattacks', models.IntegerField(default=1, verbose_name='Num Attacks')),
                ('damage', models.CharField(max_length=50)),
                ('xp', models.IntegerField()),
                ('reach', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='MonsterState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hp', models.IntegerField(default=-1)),
                ('max_hp', models.IntegerField(default=-1)),
                ('status', models.CharField(choices=[('OK', 'OK'), ('DE', 'Dead'), ('UC', 'Unconscious')], default='XX', max_length=2)),
                ('x', models.IntegerField(default=-1)),
                ('y', models.IntegerField(default=-1)),
                ('monster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monster.Monster')),
            ],
        ),
    ]
