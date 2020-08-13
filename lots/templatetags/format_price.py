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
                group3.append(price[k-3:k][::-1])

        if LAST_INDEX < len(price):
            group3.append(price[LAST_INDEX:][::-1])

        group3 = group3[::-1]


        joined = " ".join(group3)
        without_leading_0 = ""
        for i, digit in enumerate(joined):
            if digit == "0":
                without_leading_0 = joined[i+1:]
            else:
                without_leading_0 = joined
                break

        return without_leading_0 + decimals
    else:
        return 0