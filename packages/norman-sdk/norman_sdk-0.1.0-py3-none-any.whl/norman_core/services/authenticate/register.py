from norman_objects.services.authenticate.register.register_auth_factor_request import RegisterAuthFactorRequest
from norman_objects.services.authenticate.register.register_email_request import RegisterEmailRequest
from norman_objects.services.authenticate.register.register_password_request import RegisterPasswordRequest
from norman_objects.services.authenticate.register.resend_email_verification_code_request import ResendEmailVerificationCodeRequest
from norman_objects.shared.authentication.account_authentication_methods import AccountAuthenticationMethods
from norman_objects.shared.security.sensitive import Sensitive

from norman_core.clients.http_client import HttpClient


class Register:
    @staticmethod
    async def get_authentication_factors(http_client: HttpClient, token: Sensitive[str], account_id: str):
        response = await http_client.get(f"authenticate/register/get/authentication/factors/{account_id}", token)
        return AccountAuthenticationMethods.model_validate(response)

    @staticmethod
    async def generate_api_key(http_client: HttpClient, token: Sensitive[str], register_key_request: RegisterAuthFactorRequest):
        api_key = await http_client.post("authenticate/generate/key", token, json=register_key_request.model_dump(mode="json"))
        return api_key

    @staticmethod
    async def register_password(http_client: HttpClient, token: Sensitive[str], register_password_request: RegisterPasswordRequest):
        await http_client.post("authenticate/register/password", token, json=register_password_request.model_dump(mode="json"))

    @staticmethod
    async def register_email(http_client: HttpClient, token: Sensitive[str], register_email_request: RegisterEmailRequest):
        await http_client.post("authenticate/register/email", token, json=register_email_request.model_dump(mode="json"))


    @staticmethod
    async def verify_email(http_client: HttpClient, token: Sensitive[str], email: str, code: str):
        await http_client.post(f"authenticate/register/email/verify/{email}/{code}", token)

    @staticmethod
    async def resend_email_otp(http_client: HttpClient, token: Sensitive[str], resend_email_verification_code_request: ResendEmailVerificationCodeRequest):
        await http_client.post("authenticate/register/email/resend/otp", token, json=resend_email_verification_code_request.model_dump(mode="json"))
