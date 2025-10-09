from . import register_views, views

urlpatterns = register_views(
    views.LocaleRestView,
    views.AuthenticationView,
    views.SignupView,
    views.ForgottenPasswordView,
    views.OtpEmailView)
