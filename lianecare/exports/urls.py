from django.urls import path

from lianecare.exports import views

app_name = "exports"
urlpatterns = [
    path('caregivers_pro/', views.caregiverpro_export_view, name='caregiverpro_export'),
]
