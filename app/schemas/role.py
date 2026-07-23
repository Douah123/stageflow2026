from pydantic import BaseModel


class RoleResponse(BaseModel):
    id: int
    nom: str

    model_config = {"from_attributes": True}