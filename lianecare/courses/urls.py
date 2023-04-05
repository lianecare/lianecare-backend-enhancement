from django.urls import path
from lianecare.courses import views

app_name = "courses"
urlpatterns = [
    path('', view=views.CourseListView.as_view(), name='course_list'),
    path('iscrizione/', view=views.free_enroll, name='free_enroll'),
    path('<slug:slug>/', view=views.CourseDetailView.as_view(), name='course_detail'),
    #path('<slug:slug>/<int:pk>/', view=views.ModuleDetailView.as_view(), name='module_detail'),
]
