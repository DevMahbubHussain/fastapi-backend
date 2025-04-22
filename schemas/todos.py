from pydantic import BaseModel
from typing import Optional

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    complete: Optional[bool] = None
