from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Path, HTTPException, Depends
from fastapi.params import Query
from sqlalchemy import func, desc, asc
from starlette import status
from typing_extensions import Optional

from schemas.todo import TodoRequest,TodoResponse,PaginatedTodos
from models.todo import Todos
from db.database import DbDependency
from routes.auth import get_current_user
from utils.todo_helpers import get_user_todo_or_404
from schemas.todos import TodoUpdate

router = APIRouter()

# user dependency

user_dependency = Annotated[dict,Depends(get_current_user)]

@router.get('/',response_model=PaginatedTodos)
async def read_all(
        user:user_dependency,
        db: DbDependency,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        complete: Optional[bool] = Query(None),
        priority: Optional[int] = Query(None, ge=1),
        search_title: Optional[str] = Query(None),
        search_description: Optional[str] = Query(None),
        sort_by: Optional[str] = Query("id"),
        sort_order: Optional[str] = Query("asc"),
        date_from: Optional[datetime] = Query(None),
        date_to: Optional[datetime] = Query(None),
):
    query = db.query(Todos).filter(Todos.owner_id == user.get('id'))

    # Apply filters only if provided
    if complete is not None:
        query = query.filter(Todos.complete == complete)
    if priority is not None:
        query = query.filter(Todos.priority == priority)

    # Search by title (case-insensitive)
    if search_title:
        query = query.filter(func.lower(Todos.title).like(f"%{search_title.lower()}%"))

    # Search by description (case-insensitive)
    if search_description:
        query = query.filter(func.lower(Todos.description).like(f"%{search_description.lower()}%"))

    # ✅ Filter by date range
    if date_from:
        query = query.filter(Todos.created_at >= date_from)
    if date_to:
        query = query.filter(Todos.created_at <= date_to)

    # Allowed fields for sorting
    allowed_sort_fields = {
        "id": Todos.id,
        "priority": Todos.priority,
        "title": Todos.title,
        "complete": Todos.complete,
        "description": Todos.description,
        "created_at": Todos.created_at,
    }
    sort_column = allowed_sort_fields.get(sort_by, Todos.id)

    # Apply sorting
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    total_count = query.count()

    todos = query.order_by(Todos.id.asc()).offset(skip).limit(limit).all()

    return {
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "data": todos
    }

# get single todo by ID
@router.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def get_todo(user:user_dependency,db:DbDependency,todo_id:int = Path(gt=0)):

    todo_model = get_user_todo_or_404(todo_id, user, db)

    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo Not Found")

    return todo_model


# save todo
@router.post('/todo',status_code=status.HTTP_201_CREATED,response_model=TodoResponse)
async def add_todo(user:user_dependency,db:DbDependency,todo_request:TodoRequest):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication Failed'
        )
    todo_model = Todos(
        **todo_request.model_dump(),
        owner_id=user.get('id')
    )
    # type(todo_model)
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model

# update todo
@router.put('/todo/{todo_id}', status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def update_todo(
    user: user_dependency,
    db: DbDependency,
    todo_id: int,
    todo_request: TodoRequest
):
    # # ✅ Query todo only if it belongs to the logged-in user
    # todo_model = db.query(Todos).filter(
    #     Todos.id == todo_id,
    #     Todos.owner_id == user.get('id')  # check ownership
    # ).first()

    todo_model = get_user_todo_or_404(todo_id, user, db)

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo Not Found or Access Denied")

    # ✅ Update only allowed fields
    for key, value in todo_request.model_dump().items():
        setattr(todo_model, key, value)

    db.commit()
    db.refresh(todo_model)
    return todo_model


# patch
@router.patch('/todo/{todo_id}', status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def partial_update_todo(
    user: user_dependency,
    db: DbDependency,
    todo_id: int,
    todo_update: TodoUpdate
):
    todo_model = get_user_todo_or_404(todo_id, user, db)

    # Only update fields that are provided (not None)
    for key, value in todo_update.model_dump(exclude_unset=True).items():
        setattr(todo_model, key, value)

    db.commit()
    db.refresh(todo_model)
    return todo_model



# delete
@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency,
    db: DbDependency,
    todo_id: int
):
    # # ✅ Ensure the todo belongs to the current user
    # todo_model = db.query(Todos).filter(
    #     Todos.id == todo_id,
    #     Todos.owner_id == user.get('id')
    # ).first()

    todo_model = get_user_todo_or_404(todo_id, user, db)

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo Not Found or Access Denied")

    db.delete(todo_model)
    db.commit()
