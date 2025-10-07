from django.urls import path
from .views import EmbeddedSignupCallbackView

urlpatterns = [
    path('callback/', EmbeddedSignupCallbackView.as_view(), name='embedded_signup_callback'),
]
