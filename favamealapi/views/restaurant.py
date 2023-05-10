"""View module for handling requests about restaurants"""
from rest_framework.exceptions import ValidationError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from favamealapi.models import Restaurant
from django.contrib.auth.models import User
from rest_framework.decorators import action


class RestaurantSerializer(serializers.ModelSerializer):
    """JSON serializer for restaurants"""

    is_favorite = serializers.BooleanField(read_only=True)

    class Meta:
        model = Restaurant
        fields = ("id", "name", "address", "is_favorite")


class RestaurantView(ViewSet):
    """ViewSet for handling restuarant requests"""

    def create(self, request):
        """Handle POST operations for restaurants

        Returns:
            Response -- JSON serialized event instance
        """
        try:
            rest = Restaurant.objects.create(
                name=request.data["name"], address=request.data["address"]
            )
            serializer = RestaurantSerializer(rest)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single event

        Returns:
            Response -- JSON serialized game instance
        """
        try:
            user = request.user
            restaurant = Restaurant.objects.get(pk=pk)

            restaurant.is_favorite = user in restaurant.user_favorite.all()

            serializer = RestaurantSerializer(restaurant)
            return Response(serializer.data)

        except Restaurant.DoesNotExist as ex:
            return Response({"reason": ex.message}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handle GET requests to restaurants resource

        Returns:
            Response -- JSON serialized list of restaurants
        """
        user = request.user
        restaurants = Restaurant.objects.all()

        for restaurant in restaurants:
            restaurant.is_favorite = user in restaurant.user_favorite.all()

        serializer = RestaurantSerializer(restaurants, many=True)

        return Response(serializer.data)

    # TODO: Write a custom action named `favorite` that will allow a client to
    # send a POST request to /restaurant/2/favorite and add the restaurant as a favorite

    @action(methods=["post"], detail=True)
    def favorite(self, request, pk):
        """Request for a user to favorite an event"""
        user = request.user
        restaurant = Restaurant.objects.get(pk=pk)
        restaurant.user_favorite.add(user)
        return Response(
            {"message": "Added as user favorite"}, status=status.HTTP_201_CREATED
        )

    @action(methods=["post"], detail=True)
    def unfavorite(self, request, pk):
        """Request for a user to un-favorite an event"""
        user = request.user
        restaurant = Restaurant.objects.get(pk=pk)
        restaurant.user_favorite.remove(user)
        return Response(
            {"message": "Removed as user favorite"}, status=status.HTTP_201_CREATED
        )
