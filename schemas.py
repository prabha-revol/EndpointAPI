from pydantic import BaseModel


class UserRegister(BaseModel):

    username: str

    email: str

    password: str
class UserUpdate(BaseModel):
    username: str
    email: str
    password: str
class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):

    id: int

    username: str

    email: str

    class Config:

        from_attributes = True