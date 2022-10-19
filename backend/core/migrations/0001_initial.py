# Generated by Django 2.2.16 on 2022-10-18 11:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name="Ingredient's title")),
                ('amount', models.IntegerField(verbose_name='Amount of ingredients')),
                ('measurement_unit', models.CharField(max_length=20, verbose_name='Units')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name="Tag's title")),
                ('color', models.CharField(max_length=8, verbose_name="Tag's HEX color")),
                ('slug', models.SlugField(unique=True, verbose_name='URL')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name="Recipe's Title")),
                ('image', models.ImageField(upload_to='core/', verbose_name="Recipe's Image")),
                ('text', models.TextField(verbose_name="Recipe's text")),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL)),
                ('ingredient', models.ManyToManyField(related_name='ingredients', to='core.Ingredient')),
                ('tag', models.ManyToManyField(related_name='tags', to='core.Tag')),
            ],
        ),
    ]