from django.contrib import admin
from .models import Category, Post, Tag, Like, Comment, View, WebsiteView

# Register your models here.
admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(View)
admin.site.register(WebsiteView)
