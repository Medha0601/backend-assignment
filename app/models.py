from pydantic import BaseModel

class Document(BaseModel):
    user_id: str
    title: str
    content: str