from django.urls import path
from lianecare.orders import views

app_name = "orders"
urlpatterns = [
    path('config/', views.stripe_config, name='stripe_config'),
    path('course-checkout-session', views.create_payment_checkout_session, name="course_checkout_session"),
    path('corso/success/', views.orderCourseSuccess, name='course_course_complete'),
    path('cancellato/', views.CancelledView.as_view()),
    path('webhook/', views.stripe_webhook, name='stripe_webhook')
]
