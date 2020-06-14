from django import template
from django.http import HttpRequest
from lots.models import Article

register = template.Library()

@register.simple_tag
def is_favourite_post(post: Article, request: HttpRequest):

    if post.favourite.filter(id=request.user.id).exists():
        return True
    else:
        return False