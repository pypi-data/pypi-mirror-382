from norman_objects.services.authenticate.login.account_id_password_login_request import AccountIDPasswordLoginRequest
from norman_objects.services.authenticate.login.api_key_login_request import ApiKeyLoginRequest
from norman_objects.services.authenticate.login.email_password_login_request import EmailPasswordLoginRequest
from norman_objects.services.authenticate.login.login_response import LoginResponse
from norman_objects.services.authenticate.login.name_password_login_request import NamePasswordLoginRequest

from norman_core.clients.http_client import HttpClient


class Login:
    @staticmethod
    async def login_default(http_client: HttpClient, account_id: str):
        response = await http_client.post(f"authenticate/login/default/{account_id}")
        return LoginResponse.model_validate(response)

    @staticmethod
    async def login_with_key(http_client: HttpClient, api_key_login_request: ApiKeyLoginRequest):
        response = await http_client.post("authenticate/login/key", json=api_key_login_request.model_dump(mode="json"))
        return LoginResponse.model_validate(response)

    @staticmethod
    async def login_password_account_id(http_client: HttpClient, login_request: AccountIDPasswordLoginRequest):
        response = await http_client.post("authenticate/login/password/account_id", json=login_request.model_dump(mode="json"))
        return LoginResponse.model_validate(response)

    @staticmethod
    async def login_password_name(http_client: HttpClient, login_request: NamePasswordLoginRequest):
        response = await http_client.post("authenticate/login/password/name", json=login_request.model_dump(mode="json"))
        return LoginResponse.model_validate(response)

    @staticmethod
    async def login_password_email(http_client: HttpClient, login_request: EmailPasswordLoginRequest):
        response = await http_client.post("authenticate/login/password/email", json=login_request.model_dump(mode="json"))
        return LoginResponse.model_validate(response)

    @staticmethod
    async def login_email_otp(http_client: HttpClient, email: str):
        await http_client.post("authenticate/login/email/otp", json={"email": email})

    @staticmethod
    async def verify_email_otp(http_client: HttpClient, email: str, code: str):
        response = await http_client.post("authenticate/login/email/otp/verify", json={"email": email, "code": code})
        return LoginResponse.model_validate(response)
