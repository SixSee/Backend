import jwt
import requests
from django.core.mail import EmailMessage, EmailMultiAlternatives

from Excelegal import settings as config
from .models import User


class GoogleConnectError(Exception):
    pass


class GoogleOAuthApi:
    def __init__(self, code='', redirect_url='', access_token=''):
        self.CODE = code
        self.CLIENT_ID = config.CLIENT_ID
        self.CLIENT_SECRET = config.CLIENT_SECRET
        self.GRANT_TYPE = "authorization_code"
        self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
        self.GOOGLE_ID_TOKEN_INFO_URL = "https://www.googleapis.com/oauth2/v3/tokeninfo"
        self.GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
        self.REDIRECT_URL = redirect_url
        self.ACCESS_TOKEN = access_token

        if not access_token:
            self.ACCESS_TOKEN = self.get_access_token()

    def get_user_info(self) -> dict:
        response = requests.get(self.GOOGLE_USER_INFO_URL, headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
        if response.ok:
            return response.json()
        else:
            raise GoogleConnectError(response.reason)

    def get_access_token(self) -> str:
        data = {
            "code": self.CODE,
            "client_secret": self.CLIENT_SECRET,
            "client_id": self.CLIENT_ID,
            "redirect_uri": self.REDIRECT_URL,
            "access_type": "offline",
            "grant_type": self.GRANT_TYPE
        }
        response = requests.post(url=self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL, json=data)
        if response.ok:
            response = response.json()
            ACCESS_TOKEN = response['access_token']
            return ACCESS_TOKEN
        else:
            raise GoogleConnectError(response.json())


def create_user(email, password=None, **kwargs) -> User:
    extra_fields = {
        'is_staff': False,
        'is_superuser': False,
        **kwargs
    }
    user = User.objects.create(email=email, **extra_fields)
    if password:
        user.set_password(password)
    else:
        user.set_unusable_password()
    user.full_clean()
    user.save()
    return user


class Email:
    TO = []
    FROM = config.EMAIL_HOST_USER
    CONTENT = ""
    SUBJECT = None

    def __init__(self, to: list = None, subject=None):
        self.TO = to
        self.SUBJECT = subject

    def send_email(self):
        email = EmailMultiAlternatives(subject=self.SUBJECT, from_email=self.FROM, to=self.TO)
        email.content_subtype = "html"
        email.body = f"{self.CONTENT}"
        return email.send()


class MagicLink:
    SECRET = config.SECRET_KEY
    USER: User = None
    ALGORITHM = ["HS256"]
    FE_URL = config.FRONTEND_URL

    def __init__(self, user: User = None):
        self.USER = user

    def create_encoded_token(self, link_type=None, user: User = None):
        data = {
            'type': link_type,
            "user_id": str(self.USER.id),
        }
        encoded_jwt = jwt.encode(data, self.SECRET, algorithm=self.ALGORITHM[0])
        return encoded_jwt

    def decode_token(self, token):
        decoded_jwt = jwt.decode(token, self.SECRET, algorithms=self.ALGORITHM)
        return decoded_jwt

    def create_magic_link(self, link_type=None):
        token = self.create_encoded_token(link_type, self.USER)
        return f"{self.FE_URL}{link_type}?key={token}"
