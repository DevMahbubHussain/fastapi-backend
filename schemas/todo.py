# schemas/todo.py
from datetime import datetime

from pydantic import BaseModel, Field

# pydantic data validation for post request
class TodoRequest(BaseModel):
    title:str=Field(min_length=3,max_length=10)
    description:str=Field(min_length=10,max_length=100)
    priority:int=Field(gt=0,lt=6)
    complete:bool

# inheriting TodoRequest inside TodoResponse to avoid repeating all the same fields (title, description, piority, complete). This is a clean
# and DRY (Don't Repeat Yourself) way to build layered schemas in FastAPI using Pydantic.
class TodoResponse(TodoRequest):
    id: int
    # user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedTodos(BaseModel):
    total: int
    skip: int
    limit: int
    data:list[TodoResponse]