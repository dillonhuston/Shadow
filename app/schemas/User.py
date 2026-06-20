from pydantic import BaseModel, Field


class UserUsername(BaseModel):

    username: str




class UserSignup(BaseModel):
    username: str
    email: str
    password: str = Field(..., max_length=72)


class UserLogin(BaseModel):
    username:str
    password: str
    

class UserSignupResponse(BaseModel):
    id: str
    username: str
    email: str
    

class UserSignOnResponse(BaseModel):
    id: str
    username: str
    email: str
    access_token:str
    token_type: str

