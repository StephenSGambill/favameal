"""View module for handling requests about meals"""
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from favamealapi.models import Meal, MealRating, Restaurant, FavoriteMeal
from favamealapi.views.restaurant import RestaurantSerializer


class MealSerializer(serializers.ModelSerializer):
    """JSON serializer for meals"""

    is_favorite = serializers.BooleanField(read_only=True)
    restaurant = RestaurantSerializer(many=False)
    user_rating = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    def get_user_rating(self, obj):
        # Implement your logic to calculate the user rating here
        user = self.context["request"].user
        meal_rating = MealRating.objects.filter(meal=obj, user=user).first()
        if meal_rating:
            return meal_rating.rating
        return 0

    def get_avg_rating(self, obj):
        ratings = obj.mealrating.values_list("rating", flat=True)
        return sum(ratings) / len(ratings) if ratings else 0

    class Meta:
        model = Meal
        # TODO: Add 'user_rating', 'avg_rating', 'is_favorite' fields to MealSerializer
        fields = (
            "id",
            "name",
            "restaurant",
            "is_favorite",
            "user_rating",
            "avg_rating",
        )


class MealView(ViewSet):
    """ViewSet for handling meal requests"""

    def create(self, request):
        """Handle POST operations for meals

        Returns:
            Response -- JSON serialized meal instance
        """
        try:
            meal = Meal.objects.create(
                name=request.data["name"],
                restaurant=Restaurant.objects.get(pk=request.data["restaurant_id"]),
            )
            serializer = MealSerializer(meal)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single meal
        Returns:
            Response -- JSON serialized meal instance
        """
        try:
            meal = Meal.objects.get(pk=pk)
            user = request.user

            serializer = MealSerializer(meal, context={"request": request})
            serialized_data = serializer.data

            serialized_data["is_favorite"] = user in meal.user_favorite.all()

            ratings = meal.mealrating.values_list("rating", flat=True)
            serialized_data["avg_rating"] = (
                sum(ratings) / len(ratings) if ratings else 0
            )

            return Response(serialized_data)

        except Meal.DoesNotExist as ex:
            return Response({"reason": ex.message}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handle GET requests to meals resource
        Returns:
            Response -- JSON serialized list of meals
        """
        user = request.user
        meals = Meal.objects.all()

        for meal in meals:
            meal.is_favorite = user in meal.user_favorite.all()
            mealrating = MealRating.objects.filter(meal=meal, user=user).first()

            if mealrating:
                meal.user_rating = mealrating.rating
            else:
                meal.user_rating = 0

        serializer = MealSerializer(meals, many=True, context={"request": request})

        return Response(serializer.data)

    @action(methods=["post", "put"], detail=True)
    def rate(self, request, pk):
        """Request for a user to POST or PUT a meal rating"""
        user = request.user
        meal = Meal.objects.get(pk=pk)
        rating = request.data.get("rating")  # Get the rating from the request data
        meal_rating, created = MealRating.objects.get_or_create(
            meal=meal, user=user, defaults={"rating": rating}
        )
        if not created:
            meal_rating.rating = rating
            meal_rating.save()

        if created:
            message = "Added user rating"
        else:
            message = "Updated user rating"

        return Response({"message": message}, status=status.HTTP_201_CREATED)

    @action(methods=["post"], detail=True)
    def favorite(self, request, pk):
        """Request for a user to favorite a meal"""
        user = request.user
        meal = Meal.objects.get(pk=pk)
        meal.user_favorite.add(user)
        return Response(
            {"message": "Added as user favorite"}, status=status.HTTP_201_CREATED
        )

    @action(methods=["put"], detail=True)
    def unfavorite(self, request, pk):
        """Request for a user to un-favorite an event"""
        user = request.user
        meal = Meal.objects.get(pk=pk)
        meal.user_favorite.remove(user)
        return Response(
            {"message": "Removed as user favorite"}, status=status.HTTP_201_CREATED
        )
