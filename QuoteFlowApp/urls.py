
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from quotes import views as quote_views
from QuoteFlowApp.views import CustomLoginView, CustomSignupView, custom_logout
from django.conf import settings
from django.conf.urls.static import static

from payments.views import payment_webhook, update_quote_status

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', quote_views.dashboard, name='home'),
    path('accounts/login/', CustomLoginView.as_view(), name='account_login'),
    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),
    path('accounts/logout/', custom_logout, name='custom_logout'),
    path('accounts/', include('allauth.urls')),
    path('quotes/dashboard/', quote_views.dashboard, name='quotes-dashboard'),
    path('quotes/add/', quote_views.add_quote, name='add_quote'),

    path('payment-webhook/', payment_webhook, name='payment_webhook'),
    path('quotes/update_status/<str:invoice_id>/', update_quote_status, name='update_quote_status'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
