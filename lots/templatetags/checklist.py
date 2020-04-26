from django import template
from django.http import HttpRequest

register = template.Library()

@register.simple_tag
def checklist(item: int, request: HttpRequest, key: str):
    #checking is item available in in list 
    items = request.GET.getlist(key)

    return str(item) in items
        