from django.urls import path
from rest_framework import routers

from user import views

app_name = 'user'
router = routers.DefaultRouter()

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("search/", views.UserSearchView.as_view(), name="search"),
    path("send-friend-request/", views.SendFriendRequestView.as_view(), name="send_friend_request"),
    path("accept-friend-request/", views.AcceptFriendRequestView.as_view(), name="accept_friend_request"),
    path("reject-friend-request/", views.RejectFriendRequestView.as_view(), name="reject_friend_request"),
    path("friends/", views.FriendListView.as_view(), name="friends"),
    path("pending-requests/", views.PendingFriendRequestListView.as_view(), name="pending_requests"),
]

urlpatterns += router.urls
