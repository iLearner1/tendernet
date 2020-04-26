from django import template

register = template.Library()

@register.simple_tag
def compare(a=None, b=None):
    #this tag will be used for compare numeric value in django template
    if not a or not b:
        return False

    a = int(a)
    b = int(b)
    return a == b;