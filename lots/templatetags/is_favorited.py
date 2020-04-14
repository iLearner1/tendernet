from django import template
from django.http import HttpRequest
from lots.models import FavoriteSearch

register = template.Library()

@register.simple_tag
def is_favorited(request: HttpRequest):
    item_id = request.GET.get('item_id')
    if item_id:
        item_id = int(item_id)
        return FavoriteSearch.objects.filter(id=item_id).exists()
    
    return False