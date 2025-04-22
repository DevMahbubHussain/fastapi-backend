from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.todo import Todos

# def get_user_todo_or_404(todo_id: int, user_id: int, db: Session) -> Todos:
#     todo = db.query(Todos).filter(
#         Todos.id == todo_id,
#         Todos.user_id == user_id
#     ).first()
#
#     if not todo:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Todo Not Found or Access Denied"
#         )
#     return todo


def get_user_todo_or_404(todo_id: int, user: dict, db: Session) -> Todos:
    query = db.query(Todos).filter(Todos.id == todo_id)

    if user.get("role") != "admin":
        query = query.filter(Todos.user_id == user.get("id"))

    todo = query.first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo Not Found or Access Denied"
        )
    return todo
