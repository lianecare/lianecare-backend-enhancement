from django.urls import path

from lianecare.memberships import views

app_name = "memberships"
urlpatterns = [
    path('', views.home, name='home'),
    path('config/', views.stripe_config, name='stripe_config'),
    path('create-checkout-session/', views.create_checkout_session, name='new_checkout_session'),
    path('success/', views.success, name='success_page'),
    path('cancel/', views.cancel, name='cancel_page'),
    path('webhook/', views.stripe_webhook, name='webhook'),
]
