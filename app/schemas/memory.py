from pydantic import BaseModel, Field


class RememberRequest(BaseModel):
    session_id: str
    content: str
    namespace: str = "default"
    importance: float = Field(default=0.5, ge=0.0, le=1.0)


class RecallRequest(BaseModel):
    session_id: str
    query: str
    namespace: str = "default"
    limit: int = Field(default=5, ge=1, le=20)

