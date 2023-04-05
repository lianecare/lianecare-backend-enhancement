from django.urls import path
from lianecare.quizes import views

app_name = 'quizes'
urlpatterns = [
    path('<pk>/', views.quiz_view, name='quiz-detail'),
    path('<pk>/save/', views.save_quiz_view, name='save-view'),
    path('<pk>/data/', views.quiz_data_view, name='quiz-data-view'),
]
