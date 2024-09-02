from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from django.db.models import Q
from rest_framework import status, generics
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase

from user import serializers
from user.models import FriendRequest

User = get_user_model()


class LoginView(TokenViewBase):
    """
    View to authenticate and generate access and refresh tokens for a user.
    """
    serializer_class = serializers.UserTokenSerializer
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        """
        Authenticate the user and generate access and refresh tokens.

        Returns:
            Response: Response object containing access and refresh tokens.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {
            'access': serializer.validated_data['access'],
            'refresh': serializer.validated_data['refresh']
        }
        update_last_login(None, serializer.validated_data['user'])
        return Response(data, status=status.HTTP_200_OK)


class SignUpView(GenericAPIView):
    """
    View to create a new user account.
    """
    serializer_class = serializers.SignUpSerializer
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        """
        Create a new user account.

        Returns:
            Response: Response object with a success message.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Account created successfully"}, status=status.HTTP_200_OK)


class UserSearchView(generics.ListAPIView):
    """
    View to search for users by name or email.
    """
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        """
        Get the queryset of users based on the search query.

        Returns:
            queryset: Filtered queryset of users.
        """
        qs = super().get_queryset()
        q = self.request.GET.get('q', '')

        if '@' in q:  # Search by exact email
            qs = qs.filter(email=q)
        elif q:  # Search by name (partial match)
            qs = qs.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q))
        else:
            qs = qs.none()
        qs = qs.exclude(id=self.request.user.id)
        return qs


class SendFriendRequestView(GenericAPIView):
    """
    View to send a friend request to another user.
    """
    serializer_class = serializers.SendRequestSerializer

    def post(self, request, *args, **kwargs):
        """
        Send a friend request to another user.

        Returns:
            Response: Response object with a success message.
        """
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        recipient_id = serializer.validated_data['recipient_id']
        FriendRequest.objects.create(recipient_id=recipient_id, sender_id=request.user.id)
        return Response({"message": "Friend request sent successfully"}, status=status.HTTP_201_CREATED)


class AcceptFriendRequestView(GenericAPIView):
    """
    View to accept a friend request.
    """
    serializer_class = serializers.AcceptRequestSerializer

    def post(self, request, *args, **kwargs):
        """
        Accept a friend request.

        Returns:
            Response: Response object with a success message.
        """
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        friend_request = serializer.validated_data['friend_request']
        friend_request.accepted = True
        friend_request.save()
        return Response({'message': "Friend request accepted"})


class RejectFriendRequestView(GenericAPIView):
    """
    View to reject a friend request.
    """
    serializer_class = serializers.RejectRequestSerializer

    def post(self, request, *args, **kwargs):
        """
        Reject a friend request.

        Returns:
            Response: Response object with a success message.
        """
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        friend_request = serializer.validated_data['friend_request']
        friend_request.delete()
        return Response({'message': 'Friend request rejected.'})


class FriendListView(generics.ListAPIView):
    """
    View to retrieve a list of friends for a user.
    """
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        """
        Get the queryset of friends for the current user.

        Returns:
            queryset: Filtered queryset of friends.
        """
        user_id = self.request.user.id
        send_friends = User.objects.filter(sent_friend_requests__sender_id=user_id,
                                           sent_friend_requests__accepted=True)
        receive_friends = User.objects.filter(received_friend_requests__sender_id=user_id,
                                              received_friend_requests__accepted=True)
        return send_friends | receive_friends


class PendingFriendRequestListView(generics.ListAPIView):
    """
    View to retrieve a list of pending friend requests for a user.
    """
    serializer_class = serializers.FriendRequestSerializer

    def get_queryset(self):
        """
        Get the queryset of pending friend requests for the current user.

        Returns:
            queryset: Filtered queryset of pending friend requests.
        """
        user_id = self.request.user.id
        return FriendRequest.objects.filter(recipient_id=user_id, accepted=False)
