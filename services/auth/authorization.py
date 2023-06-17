import os
import redis
from os import getenv
from jose import jwt
from secrets import token_urlsafe
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from datetime import datetime, timedelta
from .database.models.user import User as UserModel
from .database.database import db, client
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from ..database import PyObjectId
from fastapi.encoders import jsonable_encoder
from typing import Any
from .email_verification import email_verification_service


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    _id: datetime
    user: PyObjectId = Field(default_factory=PyObjectId, exclude=True)
    access_token: str
    token_type: str


class Authorization:

    def __init__(self):
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOSTNAME", default=""),
            port=int(os.getenv("REDIS_PORT", default="0")),
            username=os.getenv("REDIS_USERNAME", default=""),
            password=os.getenv("REDIS_PASSWORD", default=""),

        )

    def verify_password(self, plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)

    def get_url_safe_token(self):
        return token_urlsafe(64)

    def get_password_hash(self, password: str):
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, getenv("SECRET_KEY"),  # type: ignore
                                 algorithm=getenv("ALGORITHM"))  # type: ignore
        return encoded_jwt

    async def get_user(self, email):
        return await db.users.find_one({"email": str.lower(email)})

    async def authenticate_user(self, email: str, password: str):
        user = await self.get_user(email)
        if not user:
            return False
        if not self.verify_password(password, user["password"]):
            return False
        return user

    async def login_for_access_token(self, user: UserModel):
        result = await self.authenticate_user(user.email, user.password.get_secret_value())
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(
            minutes=int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", default="0")))
        access_token = self.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {
            "_id": datetime.utcnow(),
            "user": user.id,
            "token_type": "bearer",
            "access_token": access_token,
        }

    def generate_account_verification(self, user, verification_token, verification_token_expiration_time):
        def send_verification(pipe):
            verification_token_cache_set = self.redis.set(name=user.id.__str__(
            ), value=verification_token, ex=verification_token_expiration_time)
            if verification_token_cache_set:
                verification_generate_email_send_ok = email_verification_service.send_verification_email(
                    user, verification_token)
                if verification_generate_email_send_ok == False:
                    raise BaseException("Failed to send verification email.")
            else:
                raise BaseException(
                    "Failed to save account verification token on cache.")
        self.redis.transaction(send_verification)

    async def email_password_register(self, user: UserModel):
        valid_user = UserModel.validate(user)
        if valid_user:
            saved_user_for_email = await self.get_user(valid_user.email)
            if saved_user_for_email:
                return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=jsonable_encoder({"detail": [
                    {"loc": ["body", "email"], "msg": "User already exists for email."}], "body": {"email": saved_user_for_email["email"]}}))
            async with await client.start_session() as session:
                created_user_result = None
                async with session.start_transaction():
                    created_user_result = await db.users.insert_one({
                        "_id": valid_user.id,
                        "email": valid_user.email,
                        "password": self.get_password_hash(valid_user.password.get_secret_value()),
                        "photo_url": valid_user.photo_url,
                        "first_name": valid_user.first_name,
                        "last_name": valid_user.last_name,
                        "date_of_birth": valid_user.date_of_birth.isoformat(),
                        "address": valid_user.address,
                        "_verified": False
                    }, session=session)
                if created_user_result.inserted_id:
                    async with session.start_transaction():
                        token = await self.login_for_access_token(valid_user)
                        created_token_result = await db.tokens.insert_one(
                            token, session=session)
                        if created_token_result.inserted_id:
                            user_account_verification_token = self.get_url_safe_token()
                            token_expiration_time = int(os.getenv(
                                "ACCOUNT_REGISTER_VERIFICATION_HASH_EXPIRE_SECS", default="0"))
                            self.generate_account_verification(
                                valid_user, user_account_verification_token, token_expiration_time)
                            return Token.parse_obj(token)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Registration process failed due to an internal error.')


authorization_service = Authorization()
