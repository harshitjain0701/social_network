from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user.models import FriendRequest

User = get_user_model()


class UserTokenSerializer(TokenObtainPairSerializer):
    """
    Serializer for obtaining JWT tokens for a user.
    """
    default_error_messages = {
        'no_active_account': _('Invalid Email ID or Password')
    }

    def validate(self, attrs):
        """
        Validate the user credentials and generate tokens.

        Returns:
            dict: Dictionary containing user, refresh, and access tokens.
        """
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['user'] = self.user
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data


class SignUpSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    """
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate_email(self, value):
        """
        Validate the email field.

        Args:
            value (str): Email address.

        Returns:
            str: Validated email address.

        Raises:
            serializers.ValidationError: If the email is not in a valid format or already exists.
        """
        try:
            validate_email(value)
        except serializers.ValidationError:
            raise serializers.ValidationError("Invalid email format")

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists")

        return value

    def create(self, validated_data):
        """
        Create a new user.

        Args:
            validated_data (dict): Validated data.

        Returns:
            User: Created user object.
        """
        email = validated_data.get('email')
        password = validated_data.get('password')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    class Meta:
        model = User
        fields = ['id', 'email']


class SendRequestSerializer(serializers.Serializer):
    """
    Serializer for sending a friend request.
    """
    recipient_id = serializers.IntegerField()

    def validate(self, attrs):
        """
        Validate the friend request data.

        Args:
            attrs (dict): Serializer attributes.

        Returns:
            dict: Validated data.

        Raises:
            serializers.ValidationError: If the sender and recipient are the same,
                a friend request already exists between the two users,
                or the sender has reached the limit of friend requests within a minute.
        """
        request = self.context['request']
        recipient_id = attrs['recipient_id']
        sender = User.objects.get(id=request.user.id)
        recipient = User.objects.get(id=recipient_id)

        if sender == recipient:
            raise serializers.ValidationError("Sender and recipient cannot be the same.")

        existing_request = FriendRequest.objects.filter(sender=sender, recipient=recipient).exists()
        if existing_request:
            raise serializers.ValidationError('Friend request already sent.')

        received_request = FriendRequest.objects.filter(sender=recipient, recipient=sender).exists()
        if received_request:
            raise serializers.ValidationError('You already have a friend request')

        current_time = timezone.now()
        minute_ago = current_time - timezone.timedelta(minutes=1)
        request_count = FriendRequest.objects.filter(sender=sender, created_at__gte=minute_ago).count()
        if request_count >= 3:
            raise serializers.ValidationError("You have reached the limit of friend requests within a minute.")
        return attrs


class RequestSerializer(serializers.Serializer):
    """
    Base serializer for friend request actions.
    """
    request_id = serializers.IntegerField()

    def validate(self, attrs):
        """
        Validate the friend request data.

        Args:
            attrs (dict): Serializer attributes.

        Returns:
            dict: Validated data.

        Raises:
            serializers.ValidationError: If the friend request is invalid or already accepted.
        """
        request = self.context['request']
        request_id = attrs['request_id']
        try:
            friend_request = FriendRequest.objects.get(id=request_id, recipient=request.user.id)
        except FriendRequest.DoesNotExist:
            raise serializers.ValidationError('Invalid recipient or friend request.')
        if friend_request.accepted:
            raise serializers.ValidationError(self.error_messages['already_accepted'])
        attrs['friend_request'] = friend_request
        return attrs


class AcceptRequestSerializer(RequestSerializer):
    """
    Serializer for accepting a friend request.
    """
    error_messages = {
        'already_accepted': _('Friend request already accepted.')
    }


class RejectRequestSerializer(RequestSerializer):
    """
    Serializer for rejecting a friend request.
    """
    error_messages = {
        'already_accepted': _('Cannot reject an accepted friend request.')
    }


class FriendRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for FriendRequest model.
    """
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    recipient = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FriendRequest
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        """
        Validate the friend request data.

        Args:
            data (dict): Serializer data.

        Returns:
            dict: Validated data.

        Raises:
            serializers.ValidationError: If the sender and recipient are the same or a friend request already exists.
        """
        sender = data.get('sender')
        recipient = data.get('recipient')

        if sender == recipient:
            raise serializers.ValidationError("Sender and recipient cannot be the same.")

        existing_request = FriendRequest.objects.filter(sender=sender, recipient=recipient).exists()
        if existing_request:
            raise serializers.ValidationError("Friend request already exists.")

        return data
