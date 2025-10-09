import pydantic


class BaseModel(pydantic.BaseModel):
    """Base model for all pydantic models"""

    class Config:
        extra = "ignore"
        arbitrary_types_allowed = True
