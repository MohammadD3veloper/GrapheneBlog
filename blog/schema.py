from graphene_django.rest_framework.mutation import SerializerMutation
from django.http import Http404
from graphql import middlewares
from blog.middleware import WebsiteViewsMiddleware
from blog.serializers import PostSerializer
from .models import Category, Like, Post, Tag, View, Comment, WebsiteView
from django.contrib.auth import get_user_model
from graphene_django.types import DjangoObjectType
import graphene
from graphene import relay
from rest_framework import serializers
from graphene_django.filter import DjangoFilterConnectionField


class LikeObjectType(DjangoObjectType):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post']



class ViewObjectType(DjangoObjectType):
    class Meta:
        model = View
        fields = ['id', 'user', 'post']



class CommentObjectType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ['id', 'parent', 'post', 'user', 'text']



class WebsiteViewObjectType(DjangoObjectType):
    class Meta:
        model = WebsiteView
        fields = ['id', 'user_ip', 'user_agent']



class AuthorObjectType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'photo', 'username']



class TagObjectType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = '__all__'



class CategoryObjectType(DjangoObjectType):
    class Meta:
        model = Category
        fields = '__all__'



class PostObjectType(DjangoObjectType):
    class Meta:
        model = Post
        fields = [ 
            'id' ,'title', 'slug', 'image', 'text', 'category', 'author', 'tags',
                'is_vip', 'status', 'rejected_reason', 'created_date', 'updated_date'
        ]
        filter_fields = {
            'title': ['exact', 'icontains', 'istartswith'],
            'text': ['exact', 'icontains'],
            'category__name': ['exact'],
        }
        interfaces = (relay.Node, )



class PostMutation(SerializerMutation):
    class Meta:
        serializer_class = PostSerializer
        model_operations = ('create', 'update')
        lookup_field = 'id'

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        if 'id' in input:
            instance = Post.objects.filter(
                id=input['id'], owner=info.context.user
            ).first()
            if instance:
                return {'instance': instance, 'data': input, 'partial': True}
            else:
                raise Http404
        return {'data': input, 'partial': True}
 
    @classmethod
    def mutate(cls, root, info, **input):
        input = input['input']
        input['author'] = info.context.user
        category = Category.objects.get(name=input.pop('category'))
        tag = Tag.objects.get(name=input.pop('tags'))
        post, created = Post.objects.update_or_create(**input)
        post.category.add(category)
        post.tags.add(tag)
        post.save()
        return post



class LikeMutation(graphene.Mutation):
    class Arguements:
        id = graphene.Int()

    def mutate(root, info, id):
        post = Post.objects.get(pk=id)
        user = info.context.user
        Like.objects.create(
            post=post,
            user=user
        )
        return post



class Mutation(graphene.ObjectType):
    create_and_update_post = PostMutation.Field()



class Query(graphene.ObjectType):
    all_posts = graphene.List(PostObjectType)
    post = graphene.Field(PostObjectType, slug=graphene.String())
    all_posts_filtered = DjangoFilterConnectionField(PostObjectType)
    website_view = graphene.List(WebsiteViewObjectType)

    def resolve_all_posts(root, info):
        return Post.objects.all().order_by('-id').filter(status='A')

    def resolve_post(root, info, slug):
        try:
            if info.context.user.is_premium:
                post = Post.objects.get(slug=slug, status='A')
                View.objects.create(
                    user=info.context.user,
                    post=post
                )
                return post
            else:
                post = Post.objects.get(slug=slug, status='A')
                if post.is_vip:
                    if info.context.is_authenticated:
                        return {'payment_url': ''}
                    else:
                        return {'register_url': ''}
                else:
                    View.objects.create(
                        post=post
                    )
                    return post
        except Post.DoesNotExist:
            return {
                '404NotFound': 'Object not found'
            }

    def resolve_all_posts_by_category(root, info, slug):
        return Post.objects.order_by('-id').filter(category__slug=slug, status='A')

    def resolve_all_posts_filtered(root, info, *args, **kwargs):
        return Post.objects.order_by('-id')

    def resolve_website_view(root, info):
        if info.context.user.is_staff:
            wv = WebsiteView.objects.order_by('-id')
            return {
                'total_count': wv.count(),
                'website_views': wv
            }
        return {
            'PermissionDenied': "You don't have permissions to see this"
        }


schema = graphene.Schema(query=Query, mutation=Mutation)
