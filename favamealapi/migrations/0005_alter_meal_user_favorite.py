# Generated by Django 4.2.1 on 2023-05-10 20:34

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('favamealapi', '0004_remove_meal_user_rating_meal_user_favorite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal',
            name='user_favorite',
            field=models.ManyToManyField(related_name='favorited_meal', to=settings.AUTH_USER_MODEL),
        ),
    ]
