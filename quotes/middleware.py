from django.http import HttpResponse
from django.conf import settings


class HtmxRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the response from the next middleware or view function
        response = self.get_response(request)
        
        # Temporarily disable the functionality
        # if request.user.is_authenticated and 'HX-Request' in request.headers:
        #     redirect_url = settings.LOGIN_REDIRECT_URL
        #     htmx_response = HttpResponse(status=204)
        #     htmx_response['HX-Redirect'] = redirect_url
        #     return htmx_response
        
        # Return the original response
        return response
