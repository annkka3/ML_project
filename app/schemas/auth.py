from pydantic import BaseModel, EmailStr

class UserAuth(BaseModel):
    email: EmailStr
    password: str

class SignResponse(BaseModel):
    message: str
    user_id: str