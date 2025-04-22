from fastapi import APIRouter, HTTPException,Depends
from starlette import status

from db.database import DbDependency
from models.todo import Todos
from models.users import Users
from routes.todos import user_dependency
from schemas.todo import TodoResponse
from schemas.users import UserPublic
from utils.todo_helpers import get_user_todo_or_404

router = APIRouter()

# get all todos
@router.get('/todos/admin',response_model=list[TodoResponse])
async def get_all_todos(user:user_dependency,db:DbDependency):
    if user.get("role")!="admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins Only"
        )
    return db.query(Todos).order_by(Todos.id).all()


# get all users
@router.get('/users/admin',response_model=list[UserPublic])
async def get_all_users(user:user_dependency,db:DbDependency):
    if user.get("role")!="admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins Only"
        )
    return db.query(Users).order_by(Users.id).all()


# delete todo
@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency,
    db: DbDependency,
    todo_id: int
):
    todo_model = get_user_todo_or_404(todo_id, user, db)

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo Not Found or Access Denied")

    db.delete(todo_model)
    db.commit()


# delete user
@router.delete('/user/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db:DbDependency,
    user: user_dependency,
):
    # Ensure the requester has admin privileges
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only"
        )

    # Retrieve the user to be deleted
    user_to_delete = db.query(Users).filter(Users.id == user_id).first()

    if user_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user_to_delete)
    db.commit()