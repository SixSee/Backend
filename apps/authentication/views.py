from urllib.parse import urlencode

from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from Excelegal.helpers import respond
from .helpers import GoogleOAuthApi, GoogleConnectError, create_user, MagicLink, Email
from .models import User
from .serializers import UserSerializer


class SendEmail():
    def send_verification_email(self, user):
        magic_link = MagicLink(user)
        magic_link = magic_link.create_magic_link(link_type="email-verify")
        email = Email(to=[user.email], subject="Email Verification")
        email.CONTENT = f"<strong>Click on this link to verify your email:</strong> {magic_link}"
        status = email.send_email()
        return status

    def send_forgot_password_email(self, user):
        magic_link = MagicLink(user)
        magic_link = magic_link.create_magic_link(link_type="forgot-password")
        email = Email(to=[user.email], subject="Forgot Password")
        email.CONTENT = f"<strong>Click on this link to create a new password:</strong> {magic_link}"
        status = email.send_email()
        return status


class AdminLoginView(APIView, SendEmail):
    def post(self, request, format=None):
        body = request.data
        if ("email" not in body) or ("password" not in body):
            return respond(200, "Email and Password required")
        email = body.get('email')
        password = body.get('password')
        user = User.objects.filter(email=email).first()
        if not user:
            return respond(200, "No user with provided email")
        if user.role < user.STAFF:
            return respond(200, "You dont have permission to login")

        if not user.is_email_verified:
            status = self.send_verification_email(user=user)
            if status:
                return respond(200, "Please Verify your email")
            else:
                return respond(400, "Error in sending email")

        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            user.last_login = timezone.now()
            user.save()
            return respond(200, "Success", {'refresh': str(refresh), 'access': str(refresh.access_token)})
        else:
            return respond(401, "Email or Password incorrect")


class UserSignupView(APIView, SendEmail):
    def post(self, request, format=None):
        body = request.data
        email_already = User.objects.filter(email=body.get('email')).first()
        if email_already:
            if email_already.is_email_verified is False:
                status = self.send_verification_email(user=email_already)
                if status:
                    return respond(200, "Verify your email")
                else:
                    return respond(400, "Error in sending email")
            else:
                return respond(400, "Email already registered")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Email verification
            status = self.send_verification_email(user)
            if status:
                return respond(200, "Verify your email")
            else:
                return respond(400, "Error in sending email")
        return respond(400, "Error", serializer.errors)


class AdminSignupView(APIView, SendEmail):
    def post(self, request, format=None):
        body = request.data
        email_already = User.objects.filter(email=body.get('email')).first()
        if email_already:
            if email_already.is_email_verified is False:
                self.send_verification_email(user=email_already)
                return respond(200, "Verify your email")
            else:
                return respond(400, "Email already registered")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.role = User.STAFF
            user.save()
            # Email verification
            status = self.send_verification_email(user)
            if status:
                return respond(200, "Verify your email")
            else:
                return respond(400, "Error in sending email")
        return respond(400, "Error", serializer.errors)


class UserLoginView(APIView, SendEmail):
    def post(self, request, format=None):
        body = request.data
        if ("email" not in body) or ("password" not in body):
            return respond(400, "Email and Password required")

        email = body.get('email')
        password = body.get('password')
        user = User.objects.filter(email=email).first()
        if not user:
            return respond(400, "No user with provided email")

        if not user.is_email_verified:
            status = self.send_verification_email(user=user)
            if status:
                return respond(200, "Please Verify your email")
            else:
                return respond(400, "Error in sending email")

        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            user.last_login = timezone.now()
            user.save()
            return respond(200, "Success", {'refresh': str(refresh), 'access': str(refresh.access_token)})
        else:
            return respond(401, "Email or Password incorrect")


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


class MagicLinkVerifyView(APIView):
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return respond(400, "field token required")
        magic_link = MagicLink()
        data = magic_link.decode_token(token)
        token_type = data.get('type')
        user_id = data.get('user_id')
        user = User.objects.get(id=user_id)

        if token_type == "email-verify":
            user.is_email_verified = True
            user.save()
            return respond(200, "Email Verified")

        elif token_type == 'forgot-password':
            try:
                password = request.data.get('password', "")
                if not password:
                    return respond(400, "Password field is required")
                user.set_password(password)
                user.save()
                return respond(200, "Password changed successfully!")
            except Exception as e:
                return respond(200, e)
        else:
            return respond(400, "BAD TYPE")


class ForgotPasswordView(APIView, SendEmail):
    def post(self, request):
        body = request.data
        if "email" not in body:
            return respond(200, "Email required")
        email = body.get('email')
        user = User.objects.filter(email=email).first()
        if not user.is_email_verified:
            self.send_verification_email(user=user)
            return respond(200, "Please Verify your email")
        status = self.send_forgot_password_email(user)
        if status:
            return respond(200, "Email Sent to create new password")
        return respond(400, "Error in sending email")


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        body = request.data
        if "password" not in body:
            return respond(400, "Password Field required")
        password = body.get("password")
        try:
            user.set_password(password)
            user.save()
        except Exception as err:
            print(err)
            return respond(400, str(err))
        return respond(200, "Password Changed Successfully")
