from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from django.views.generic.base import TemplateView

User = get_user_model()


class UserUpdateRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        user_type = self.request.user.type
        if user_type == User.Types.PRO:
            return reverse("solace:caregiver_update")
        # elif user_type is {User.Types.EMPLOYEE, User.Types.PERSON}:
        #    return reverse("solace:person_update")
        if user_type == User.Types.STAFF:
            return reverse("admin:index")
        else:
            return reverse("solace:person_update")


user_update_redirect_view = UserUpdateRedirectView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        user = self.request.user
        if user.type == User.Types.PRO:
            return reverse("solace:caregiver_detail", kwargs={"username": user.username})
        if user.type == User.Types.STAFF:
            return reverse("admin:index")
        else:
            return reverse("solace:person_detail", kwargs={"username": user.username})


user_redirect_view = UserRedirectView.as_view()


class UserConfirmedView(TemplateView):
    template_name = 'users/confirmed.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['categories'] = Category.objects.all()
    #     return context

user_confirmed_view = UserConfirmedView.as_view()


class UserLogoutView(TemplateView):
    """Method for custom logout for website"""
    def post(self, request, **kwargs):
        if request.user.is_authenticated:
            user = self.request.user
            if user.type == User.Types.EMPLOYEE:
                logout(request)
                return redirect("solace:person_signup")
            else:
                logout(request)
                return redirect("home")
        else:
            return redirect("home")

user_logout_view = UserLogoutView.as_view()
