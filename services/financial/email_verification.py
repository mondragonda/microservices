import os
import redis
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets

class EmailVerificationSystem:
    def __init__(self):
        # Connect to Redis
        self.redis_client = redis.Redis(host='localhost', port=6379)

    def generate_verification_token(self, email):
        # Generate a random verification token
        token = secrets.token_urlsafe(16)
        # Set the token in Redis with a key that includes the email address
        self.redis_client.setex(f'verification_token:{email}', 3600, token)
        return token

    def send_verification_email(self, email, token):
        sender_email = os.environ.get('EMAIL_USER')
        sender_password = os.environ.get('EMAIL_PASSWORD')
        smtp_server = 'your_smtp_server_address'
        smtp_port = 587

        subject = 'Account Verification'
        verification_link = f'http://example.com/verify?token={token}'  # Replace with your verification endpoint

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = email
        message['Subject'] = subject

        body = f"Click the link below to verify your account:\n\n{verification_link}"
        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)

    def verify_account(self, email, token):
        # Retrieve the stored token from Redis based on the email address
        stored_token = self.redis_client.get(f'verification_token:{email}')
        if stored_token and token == stored_token.decode():
            # Account verified, update your database or user management system
            print("Account verified!")
        else:
            print("Invalid verification token")

    def run_example(self):
        email = 'destination_email'
        token = self.generate_verification_token(email)
        self.send_verification_email(email, token)

        # Simulate verification endpoint
        verification_token = "<token_from_verification_link>"
        self.verify_account(email, verification_token)

if __name__ == '__main__':
    evs = EmailVerificationSystem()
    evs.run_example()
