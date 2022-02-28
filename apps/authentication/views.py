from urllib.parse import urlencode

from django.http import HttpResponse
from django.shortcuts import redirect
from rest_framework import serializers
from rest_framework import status as s
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer
from .utils import GoogleOAuthApi, GoogleConnectError


def ping(request):
    return HttpResponse("pong")


class UserSignup(APIView):
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=s.HTTP_201_CREATED)
        return Response(serializer.errors, status=s.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    def post(self, request, format=None):
        body = request.data
        if ("email" not in body) or ("password" not in body):
            return Response({"message": "email and password required"})

        email = body.get('email')
        password = body.get('password')
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message": "No user with provided email"})
        else:
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response({'refresh': str(refresh), 'access': str(refresh.access_token)})
            else:
                return Response({"message": "Email or Password incorrect"})


class GoogleLogin(APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    def get(self, request, format=None):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)
        body = input_serializer.data

        code = body.get('code')
        error = body.get('error')

        login_url = "http://localhost:3000/login"

        if error or not code:
            params = urlencode({'error': error})
            return redirect(f'{login_url}?{params}')

        # todo -> Change this later
        redirect_url = "http://localhost:8000/auth/login/google/"

        try:
            gapi = GoogleOAuthApi(code=code, redirect_url=redirect_url)
            access_token = gapi.ACCESS_TOKEN
            user_info = gapi.get_user_info()

        except GoogleConnectError as e:
            return Response(e.args)

        return redirect("https://localhost:3000/")
