# Generated by Django 2.0 on 2017-12-12 03:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('monster', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsterstate',
            name='monster',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='monsters', to='monster.Monster'),
        ),
    ]
