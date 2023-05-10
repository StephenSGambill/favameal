from django.db import models
from django.contrib.auth.models import User


class Meal(models.Model):
    """Meal Model"""

    name = models.CharField(max_length=55)
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)
    user_favorite = models.ManyToManyField(User, related_name="favorited_meal")

    @property
    def is_favorite(self):
        return self.__is_favorite

    @is_favorite.setter
    def is_favorite(self, value):
        self.__is_favorite = value

    @property
    def user_rating(self):
        return self.__user_rating

    @user_rating.setter
    def user_rating(self, value):
        self.__user_rating = value

    @property
    def avg_rating(self):
        return self.__avg_rating
