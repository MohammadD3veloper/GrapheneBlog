from rest_framework import serializers
from .models import Post, Category, Tag


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'slug', 'image', 'text', 'category', 'tags', 'is_vip']


    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug']



class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']