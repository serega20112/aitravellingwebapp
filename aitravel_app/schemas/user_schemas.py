from pydantic import BaseModel, constr

class UserCreateSchema(BaseModel):
    username: constr(min_length=3, max_length=80)
    password: constr(min_length=6)

class UserResponseSchema(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True
