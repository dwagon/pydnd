# Generated by Django 2.0 on 2017-12-12 03:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('equipment', '0001_initial'),
        ('world', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('charclass', models.CharField(choices=[('F', 'Fighter'), ('T', 'Thief'), ('M', 'Mage'), ('C', 'Cleric')], max_length=5)),
                ('race', models.CharField(choices=[('HU', 'Human'), ('EL', 'Elf'), ('DW', 'Dwarf'), ('HE', 'Half Elven'), ('HL', 'Halfling'), ('GN', 'Gnome')], default='HU', max_length=2)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unknown')], default='U', max_length=1)),
                ('hp', models.IntegerField(default=0)),
                ('max_hp', models.IntegerField(default=0)),
                ('ac', models.IntegerField(default=10)),
                ('thaco', models.IntegerField(default=0)),
                ('dmg', models.IntegerField(default=1)),
                ('encumbrance', models.IntegerField(default=0)),
                ('movement', models.IntegerField(default=12)),
                ('xp', models.IntegerField(default=0)),
                ('align', models.CharField(choices=[('LG', 'Lawful Good'), ('LN', 'Lawful Neutral'), ('LE', 'Lawful Evil'), ('NG', 'Neutral Good'), ('N', 'True Neutral'), ('NE', 'Neutral Evil'), ('CG', 'Chaotic Good'), ('CN', 'Chaotic Neutral'), ('CE', 'Chaotic Evil')], default='N', max_length=2)),
                ('level', models.IntegerField(default=1)),
                ('status', models.CharField(choices=[('XX', 'XX'), ('OK', 'OK'), ('DE', 'Dead'), ('UC', 'Unconscious')], default='XX', max_length=2)),
                ('x', models.IntegerField(default=-1)),
                ('y', models.IntegerField(default=-1)),
                ('stat_str', models.IntegerField(default=-1)),
                ('bonus_str', models.IntegerField(default=-1)),
                ('stat_int', models.IntegerField(default=-1)),
                ('stat_wis', models.IntegerField(default=-1)),
                ('stat_dex', models.IntegerField(default=-1)),
                ('stat_con', models.IntegerField(default=-1)),
                ('stat_cha', models.IntegerField(default=-1)),
                ('plat', models.IntegerField(default=0)),
                ('gold', models.IntegerField(default=0)),
                ('silver', models.IntegerField(default=0)),
                ('copper', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='EquipState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ready', models.BooleanField(default=False)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.Character')),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='equipment.Equipment')),
            ],
        ),
        migrations.CreateModel(
            name='Spell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('level', models.IntegerField()),
                ('charclass', models.CharField(choices=[('M', 'Mage'), ('C', 'Cleric')], max_length=5)),
                ('spellfile', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='SpellState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('memorized', models.BooleanField(default=False)),
                ('default', models.BooleanField(default=False)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.Character')),
                ('spell', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.Spell')),
            ],
        ),
        migrations.AddField(
            model_name='character',
            name='gear',
            field=models.ManyToManyField(blank=True, through='character.EquipState', to='equipment.Equipment'),
        ),
        migrations.AddField(
            model_name='character',
            name='spells',
            field=models.ManyToManyField(blank=True, through='character.SpellState', to='character.Spell'),
        ),
        migrations.AddField(
            model_name='character',
            name='world',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='world.World'),
        ),
    ]
