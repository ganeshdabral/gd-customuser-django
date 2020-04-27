from django.urls import path
from django.conf import settings
from django.conf.urls import static
from .views import registration, update_user, user_login, user_listing, activation, new_activation, logout_view
app_name="account"
urlpatterns = [
    path("logout/", logout_view, name="logout"),
    path("list/", user_listing, name="list"),
    path("myaccount/", update_user, name="update_user"),
    path("verification/<key>/", activation, name="verification"),
    path("newverification/<key>/", new_activation, name="newverification"),
]