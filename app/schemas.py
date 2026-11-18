from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

    @field_validator('email')
    @classmethod
    def normalise_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

    @field_validator('email')
    @classmethod
    def normalise_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    expires_in: int
