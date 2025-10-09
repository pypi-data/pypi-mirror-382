from norman_objects.services.authenticate.login.login_response import LoginResponse
from norman_objects.services.authenticate.signup.signup_email_request import SignupEmailRequest
from norman_objects.services.authenticate.signup.signup_password_request import SignupPasswordRequest
from norman_objects.shared.accounts.account import Account

from norman_core.clients.http_client import HttpClient


class Signup:
    @staticmethod
    async def signup_default(http_client: HttpClient):
        response = await http_client.put("authenticate/signup/default")
        return LoginResponse.model_validate(response)

    @staticmethod
    async def signup_with_password(http_client: HttpClient, signup_request: SignupPasswordRequest):
        response = await http_client.put("authenticate/signup/password", json=signup_request.model_dump(mode="json"))
        return Account.model_validate(response)

    @staticmethod
    async def signup_with_email(http_client: HttpClient, signup_request: SignupEmailRequest):
        response = await http_client.put("authenticate/signup/email", json=signup_request.model_dump(mode="json"))
        return Account.model_validate(response)
