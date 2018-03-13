# Generated by Django 2.0.2 on 2018-03-13 07:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('encounter', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Monster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('align', models.CharField(choices=[('LG', 'Lawful Good'), ('LN', 'Lawful Neutral'), ('LE', 'Lawful Evil'), ('NG', 'Neutral Good'), ('N', 'True Neutral'), ('NE', 'Neutral Evil'), ('CG', 'Chaotic Good'), ('CN', 'Chaotic Neutral'), ('CE', 'Chaotic Evil'), ('U', 'Unaligned')], default='N', max_length=2)),
                ('size', models.CharField(choices=[('T', 'Tiny'), ('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('H', 'Huge'), ('G', 'Gargantuan')], default='M', max_length=2)),
                ('ac', models.IntegerField(default=10, verbose_name='AC')),
                ('hitdie', models.CharField(default='1d8', max_length=10, verbose_name='Hit Die')),
                ('speed', models.IntegerField(default=30)),
                ('stat_str', models.IntegerField(default=-1)),
                ('stat_int', models.IntegerField(default=-1)),
                ('stat_wis', models.IntegerField(default=-1)),
                ('stat_dex', models.IntegerField(default=-1)),
                ('stat_con', models.IntegerField(default=-1)),
                ('stat_cha', models.IntegerField(default=-1)),
                ('dmg_vuln', models.CharField(default='', max_length=200)),
                ('dmg_immun', models.CharField(default='', max_length=200)),
                ('cond_immun', models.CharField(default='', max_length=200)),
                ('challenge', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='MonsterAttack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('desc', models.CharField(max_length=200, unique=True)),
                ('to_hit', models.IntegerField()),
                ('reach', models.IntegerField()),
                ('damage', models.CharField(max_length=10)),
                ('damage_cat', models.CharField(choices=[('B', 'Bludgeoning'), ('N', 'Necrotic'), ('P', 'Piercing'), ('S', 'Slashing')], max_length=2)),
                ('normal_range', models.IntegerField(default=0)),
                ('long_range', models.IntegerField(default=0)),
                ('monster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attacks', to='monster.Monster')),
            ],
        ),
        migrations.CreateModel(
            name='MonsterState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=200)),
                ('hp', models.IntegerField(default=-1)),
                ('max_hp', models.IntegerField(default=-1)),
                ('status', models.CharField(choices=[('XX', 'XX'), ('OK', 'OK'), ('DE', 'Dead'), ('UC', 'Unconscious')], default='XX', max_length=2)),
                ('x', models.IntegerField(default=-1)),
                ('y', models.IntegerField(default=-1)),
                ('moves', models.IntegerField(default=-1)),
                ('initiative', models.IntegerField(default=-1)),
                ('attacks', models.IntegerField(default=-1)),
                ('encounter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='monsters', to='encounter.Encounter')),
                ('monster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monster.Monster')),
            ],
        ),
    ]
