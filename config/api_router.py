from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from lianecare.solace.api import views as solace_views
from lianecare.courses.api import views as courses_views
from lianecare.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

#router.register("users", UserViewSet)
router.register("services", solace_views.ServiceViewSet)

app_name = "api"
urlpatterns = router.urls
urlpatterns += [
    path('caregivers/<str:username>/', solace_views.CaregiverProDetailAPIView.as_view(), name="caregiver_patch"),
    path('skillUpdate', solace_views.skillUpdateFragmentAjax, name="skill_update"),
    path('getSubCategories/', solace_views.getSubcategoriesAjax, name="get_subcategories"),
    path('service-update/', solace_views.serviceUpdateView, name="service-update"),
    path('changeViewedModule', courses_views.changeViewedModuleAjax, name="change-viewed-module"),
    path('jobpost-update/', solace_views.jobPostUpdateView, name="jobpost-update"),
    path('jobposts/<int:pk>/', solace_views.JobPostUpdate.as_view(), name="jobpost-detail"),
]
