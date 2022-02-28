from Excelegal.settings import base as config
import requests


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

    def get_user_info(self):
        response = requests.get(self.GOOGLE_USER_INFO_URL,  headers={'Authorization': f"Bearer {self.ACCESS_TOKEN}"})
        if response.ok:
            return response.json()
        else:
            raise GoogleConnectError(response.reason)


    def get_access_token(self):
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
