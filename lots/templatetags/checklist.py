from django import template
from django.http import HttpRequest

register = template.Library()

@register.simple_tag
def checklist(item: int, request: HttpRequest, key: str):
    #checking is item available in in list
    code = request.GET.get(key)
    return  code == item
        