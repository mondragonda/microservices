import os
from .database.models.user import User
import requests


class EmailVerificationService:

    def send_verification_email(self, account_user: User, generated_verification_token: str):
        verification_link = f'<a href="https://example.com/verify?token={generated_verification_token}">https://example.com/verify?token={generated_verification_token}</a>'
        message = {}
        message['from'] = f'NWM Financial Advising <{os.getenv("MAILGUN_EMAIL_USER")}>'
        message['to'] = f'{account_user.first_name} {account_user.last_name} <{account_user.email}>'
        message['subject'] = 'NWM Financial Advising - Account Verification'
        message["html"] = f"<html><p>Click on the link below to verify your account:</p><p>{verification_link}</p></html>"

        response = requests.post(os.getenv("MAILGUN_API_URL", default=""), auth=(
            "api", os.getenv("MAILGUN_API_KEY", default="")), data=message)

        if not response.ok:
            raise BaseException("Failed to send verification email.",
                                "Response: ", response.status_code, response.content)

        return response.ok

    def verify_account(self, email, token):
        pass


email_verification_service = EmailVerificationService()
