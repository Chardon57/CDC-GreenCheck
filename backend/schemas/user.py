from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    surname: str = Field(max_length=255)
    name: str = Field(max_length=255)
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=255)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_user: int
    surname: str
    name: str
    email: EmailStr