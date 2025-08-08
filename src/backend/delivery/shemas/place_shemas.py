from pydantic import BaseModel, constr


class PointInfoRequestSchema(BaseModel):
    latitude: float
    longitude: float


class LikedPlaceCreateSchema(BaseModel):
    city_name: constr(min_length=1, max_length=100)
    latitude: float
    longitude: float


class LikedPlaceResponseSchema(BaseModel):
    id: int
    user_id: int
    city_name: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True
