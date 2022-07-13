from django.urls import path
from graphene_django.views import GraphQLView

from blog.middleware import WebsiteViewsMiddleware
from .schema import schema



urlpatterns = [
    path('', GraphQLView.as_view(graphiql=True, schema=schema, middleware=[WebsiteViewsMiddleware]))
]
