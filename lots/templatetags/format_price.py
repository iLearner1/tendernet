from django import template
from lots.models import Article

register = template.Library()


@register.simple_tag
def format_price(post: Article):

    group3 = []
    LAST_INDEX = 0
    if post.price:
        decimal_idx = str(post.price).index(".")
        decimals = str(post.price)[decimal_idx:]
        price = str(int(post.price))
        price = price[::-1]
        for k, v in enumerate(price):
            if k%3==0 and k>0:
                LAST_INDEX = k
                group3.append(price[k-3:k])

        if LAST_INDEX < len(price):
            group3.append(price[LAST_INDEX:])
        group3 = group3[::-1]
        return " ".join(group3) + decimals
    else:
        return 0