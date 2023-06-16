from pydantic import BaseModel, Field
from passlib.context import CryptContext
from datetime import datetime, timedelta
from os import getenv
from jose import jwt
from .database.models.user import User as UserModel
from .database.database import db, client
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from ..database import PyObjectId
from fastapi.encoders import jsonable_encoder
from secrets import token_urlsafe


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    _id: datetime
    user: PyObjectId = Field(default_factory=PyObjectId, exclude=True)
    access_token: str
    token_type: str


class Authorization:

    def verify_password(self, plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return pwd_context.hash(password)

    def get_url_safe_verification_token(self):
        return token_urlsafe(64)

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
            minutes=int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))  # type: ignore
        access_token = self.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {
            "_id": datetime.utcnow(),
            "user": user.id,
            "token_type": "bearer",
            "access_token": access_token,
        }

    async def email_password_register(self, user: UserModel):
        valid_user = UserModel.validate(user)
        if valid_user:
            saved_user_for_email = await self.get_user(valid_user.email)
            if saved_user_for_email:
                return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=jsonable_encoder({"detail": [
                    {"loc": ["body", "email"], "msg": "User already exists for email."}], "body": {"email": saved_user_for_email["email"]}}))
            async with await client.start_session() as session:
                created_token_result = None
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
                user_account_verification_token = self.get_url_safe_verification_token()
                # Persist token on redis indexed by user _id
                async with session.start_transaction():
                    if created_user_result:
                        token = await self.login_for_access_token(valid_user)
                        created_token_result = db.tokens.insert_one(
                            token, session=session)
                        if created_token_result:
                            return Token.parse_obj(token)


authorization_service = Authorization()
