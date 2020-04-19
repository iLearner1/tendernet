from django.core.cache import cache


class SaveCurrentDomain:
    # this middleware save current site url
    # to cache for later use where user don't have access of
    # request object directly
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        cache.set('current_url', request.build_absolute_uri('/').strip('/'))
        return response
