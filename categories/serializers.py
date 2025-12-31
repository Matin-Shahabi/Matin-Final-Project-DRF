# api/serializers.py
from rest_framework import serializers
from categories.models import Category

class CategoryListSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image']

class CategoryDetailSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)
    children = CategoryListSerializer(many=True, read_only=True)  # زیر دسته‌ها رو نشون میده

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'parent', 'children']