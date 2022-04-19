from urllib.parse import urlencode

from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from Excelegal.helpers import respond
from .models import User
from .serializers import UserSerializer
from .utils import GoogleOAuthApi, GoogleConnectError, create_user


class AdminLoginView(APIView):
    def post(self, request, format=None):
        body = request.data
        if ("email" not in body) or ("password" not in body):
            return respond(200, "Email and Password required")
        email = body.get('email')
        password = body.get('password')
        user = User.objects.filter(email=email).first()
        if not user:
            return respond(200, "No user with provided email")
        else:
            if user.role < user.STAFF:
                return respond(200, "You dont have permission to login")
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                user.last_login = timezone.now()
                user.save()
                return respond(200, "Success", {'refresh': str(refresh), 'access': str(refresh.access_token)})
            else:
                return respond(200, "Email or Password incorrect")


class UserSignupView(APIView):
    def post(self, request, format=None):
        body = request.data
        email_already = User.objects.filter(email=body.get('email')).first()
        if email_already:
            return respond(400, "Email already registered")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return respond(200, "Success")
        return respond(400, "Error", serializer.errors)


class AdminSignupView(APIView):
    def post(self, request, format=None):
        body = request.data
        email_already = User.objects.filter(email=body.get('email')).first()
        if email_already:
            return respond(400, "Email already registered")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.role = User.STAFF
            user.save()
            return respond(200, "Success")
        return respond(400, "Error", serializer.errors)


class UserLoginView(APIView):
    def post(self, request, format=None):
        body = request.data
        if ("email" not in body) or ("password" not in body):
            return respond(200, "Email and Password required")

        email = body.get('email')
        password = body.get('password')
        user = User.objects.filter(email=email).first()
        if not user:
            return respond(200, "No user with provided email")
        else:
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                user.last_login = timezone.now()
                user.save()
                return respond(200, "Success", {'refresh': str(refresh), 'access': str(refresh.access_token)})
            else:
                return respond(200, "Email or Password incorrect")


# todo change soon
class GoogleLoginView(APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    def get(self, request, format=None):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)
        body = input_serializer.data

        code = body.get('code')
        error = body.get('error')

        # todo -> Change this later
        login_url = "http://localhost:3000/login"
        redirect_url = "http://localhost:8000/auth/login/google/"

        if error or not code:
            params = urlencode({'error': error})
            return redirect(f'{login_url}?{params}')

        try:
            gapi = GoogleOAuthApi(code=code, redirect_url=redirect_url)
            access_token = gapi.ACCESS_TOKEN
            user_info: dict = gapi.get_user_info()
        except GoogleConnectError as error:
            return Response(error.args)

        user = User.objects.filter(email=user_info.get('email')).first()
        if not user:
            user = create_user(email=user_info.get('email'), password=None,
                               **{"first_name": user_info.get('given_name'),
                                  "last_name": user_info.get('family_name'),
                                  "access_token": access_token,
                                  "from_google": True,
                                  "is_email_verified": user_info.get('email_verified')})

        refresh = RefreshToken.for_user(user)
        params = urlencode({'access': refresh.access_token, 'refresh': str(refresh)})
        # return respond(200, "Success", {'access': refresh.access_token, 'refresh': str(refresh)})
        return redirect(f"{login_url}?{params}")


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ('id', 'email', 'first_name', 'last_name', 'role',
                      'device_id', 'is_email_verified')
            extra_kwargs = {
                'id': {'read_only': True},
                'role': {'read_only': True},
                'is_email_verified': {'read_only': True},
                'device_id': {'read_only': True}
            }

    class InputSerializer(serializers.Serializer):
        first_name = serializers.CharField(required=False)
        last_name = serializers.CharField(required=False)

    def get(self, request):
        user = request.user
        serializer = self.OutputSerializer(user)
        return respond(200, "Success", serializer.data)

    def put(self, request):
        user = request.user
        serializer = self.InputSerializer(data=request.data)
        if serializer.is_valid():
            user.__dict__.update(serializer.validated_data)
            user.save()
            return respond(200, "Success")
        return respond(400, "Success", serializer.errors)
