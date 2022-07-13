from django.db import models
from django.urls import reverse_lazy
from django.template.defaultfilters import slugify
from django.conf import settings


POST_STATUS = (
    ('A', 'Accepted'),
    ('C', 'Checking'),
    ('P', 'Pending'),
    ('R', 'Rejected'),
)


def upload_image(instance, filename):
    return f'posts/{instance.author.username}/{filename}'


# Create your models here.
class WebsiteView(models.Model):
    user_ip = models.GenericIPAddressField(unique=True)
    user_agent = models.CharField(max_length=1000)

    def __str__(self):
        return self.user_agent



class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='liked_posts',
        null=True, blank=True
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='likes'
    )

    def __str__(self):
        return self.user.username + " : " + self.post.title



class View(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vieweds',
        null=True, blank=True
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='views'
    )

    def __str__(self):
        return self.user.username + " viewd: " + self.post.title



class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name



class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('blog:post_list_category', slug=self.slug)



class Comment(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True,
                    on_delete=models.CASCADE, related_name="replies")
    post = models.ForeignKey('Post', 
                    on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE, related_name="user_comments")
    text = models.CharField(max_length=700)

    def __str__(self):
        return 'Comment for: ' + self.post.title



class Post(models.Model):
    title = models.CharField(max_length=70)
    slug = models.SlugField(max_length=50, unique=True)
    image = models.ImageField(upload_to=upload_image)
    text = models.TextField(max_length=15000)
    category = models.ManyToManyField(Category)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_posts'
    )
    tags = models.ManyToManyField(Tag)
    is_vip = models.BooleanField(default=False)
    status = models.CharField(
        choices=POST_STATUS, 
        max_length=10, 
        default=POST_STATUS[2][1]
    )
    rejected_reason = models.TextField(
        max_length=500, 
        null=True, 
        blank=True
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy('blog:post_detail', slug=self.slug)

    def save(self, *args, **kwargs):
        save = super().save(*args, **kwargs)
        self.title = slugify(self.title)
        return save
