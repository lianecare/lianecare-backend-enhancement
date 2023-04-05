from django.urls import path

from lianecare.courses.views import StudentCourseListView, StudentModuleDetailView, StudentModuleViewed
from lianecare.solace import views

app_name = "solace"
urlpatterns = [
    path("user/registrazione/", view=views.person_signup_view, name="person_signup"),
    path("user/update/", view=views.person_update_view, name="person_update"),
    path("user/impostazioni/", view=views.person_settings_view, name="person_settings"),
    path("user/jobposts/", view=views.person_job_posts_view, name="person_job_posts"),
    path("user/jobpost", view=views.person_create_job_post_view, name="person_create_job_post"),
    path("user/jobpost/<int:pk>/update/", view=views.person_update_job_post_view, name="person_update_job_post"),
    path("user/jobpost/<int:pk>/proposals/", view=views.person_detail_jobpost_view, name="person_jobpost_proposals"),
    path("user/proposals/<uuid:uuid>/", view=views.person_proposal_detail_view, name="person_proposal_detail"),
    path("user/corsi/", view=StudentCourseListView.as_view(), name="student_courses"),
    path('user/modulo/<uuid:uuid>/', view=StudentModuleDetailView.as_view(), name='student_module_detail'),
    path('user/modulo/update/<uuid:uuid>/', view=StudentModuleViewed, name='student_module_viewed'),
    path("user/<str:username>/", view=views.person_detail_view, name="person_detail"),
    path("caregiver/registrazione/", view=views.caregiver_signup_view, name="caregiver_signup"),
    path("diventa-caregiver-pro/", view=views.CaregiverSignupLandingView.as_view(), name="landing-caregiver-signup"),
    path("caregiver/update/", view=views.caregiver_update_view, name="caregiver_update"),
    path("caregiver/impostazioni/", view=views.caregiver_settings_view, name="caregiver_settings"),
    path("caregiver/proposals/", view=views.caregiver_proposals_view, name="caregiver_proposals"),
    path("caregiver/proposals/<uuid:uuid>/", view=views.caregiver_proposal_detail_view, name="caregiver_proposal_detail"),
    path("caregiver/<str:username>/", view=views.caregiver_detail_view, name="caregiver_detail"),
    path("caregiver/proposals/<uuid:pk>/ignore/", view=views.ignore_proposal, name="ignore_proposal"),
    path("check/email/exists/", view=views.check_email_exists, name="check_user_email_exists"),
]
