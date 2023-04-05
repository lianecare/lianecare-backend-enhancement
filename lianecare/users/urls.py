from django.urls import path

from lianecare.users.views import (
    user_redirect_view,
    user_update_redirect_view,
    user_confirmed_view,
    user_logout_view
)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_redirect_view, name="update"),
    path("confirmed/", view=user_confirmed_view, name="confirmed"),
    path("logout/", view=user_logout_view, name="user_logout"),

]
