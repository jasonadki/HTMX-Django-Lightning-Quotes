from django.contrib.auth import logout
from allauth.account.views import LoginView
from allauth.account.views import SignupView
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template.loader import render_to_string

class CustomLoginView(LoginView):
    def form_valid(self, form):
        """Override to add custom behavior on successful login."""
        
        # Calling the original form_valid to perform the actual login
        response = super().form_valid(form)
        
        # Check if it's an HTMX request
        if 'HX-Request' in self.request.headers:
            # Redirect after successful HTMX login
            return HttpResponseRedirect(self.get_success_url())
        
        return response

    def form_invalid(self, form):
        """Override to customize the behavior when the form is invalid (e.g., wrong credentials)."""
        
        # Check if it's an HTMX request
        if 'HX-Request' in self.request.headers:
            # Render and return the login form with errors for HTMX request
            form_html = render_to_string('account/login_error.html', {'form': form}, request=self.request)
            return HttpResponse(form_html, status=400)
        
        # If it's not an HTMX request, proceed with the default behavior
        return super().form_invalid(form)
    

class CustomSignupView(SignupView):
    def form_valid(self, form):
        """Override to add custom behavior on successful signup."""
        
        # Calling the original form_valid to perform the actual signup
        response = super().form_valid(form)
        
        # Check if it's an HTMX request
        if 'HX-Request' in self.request.headers:
            # Redirect after successful HTMX signup
            return HttpResponseRedirect(self.get_success_url())
        
        return response

    def form_invalid(self, form):
        """Override to customize the behavior when the form is invalid (e.g., invalid signup details)."""
        
        # Check if it's an HTMX request
        if 'HX-Request' in self.request.headers:
            # Render and return the signup form with errors for HTMX request
            form_html = render_to_string('account/signup_error.html', {'form': form}, request=self.request)
            return HttpResponse(form_html, status=400)
        
        # If it's not an HTMX request, proceed with the default behavior
        return super().form_invalid(form)
        
def custom_logout(request):
    """Handle logout functionality."""
    logout(request)
    
    # If it's an HTMX request, you might want to return a specific response
    if 'HX-Request' in request.headers:
        # For example, you could return a snippet of HTML indicating the user has been logged out
        # Or instruct the client-side to redirect to the login page
        return HttpResponse("<script>window.location.href='{}'</script>".format(reverse('account_login')), status=200)
    
    # For non-HTMX requests, redirect to the login page or home page
    return HttpResponseRedirect(reverse('account_login'))
