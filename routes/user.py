from fastapi import APIRouter, HTTPException,Depends
from starlette import status
from db.database import DbDependency
from models.users import Users
from routes.todos import user_dependency
from passlib.context import CryptContext

from schemas.users import UserPublic, UserUpdate, PasswordChangeRequest

pwd_context = CryptContext(schemes=['bcrypt'],deprecated="auto")
router = APIRouter()


# user profile
@router.get('/user',status_code=status.HTTP_200_OK)
async def get_user_profile(user:user_dependency,db:DbDependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication Failed")

    return db.query(Users).filter(Users.id==user.get('id')).first()


# update profileroutes
@router.put('/user', status_code=status.HTTP_200_OK, response_model=UserPublic)
async def update_user_profile(
    user: user_dependency,
    db: DbDependency,
    update_data: UserUpdate
):
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(user_model, key, value)

    db.commit()
    db.refresh(user_model)
    return user_model

# user password change routes
@router.patch('/user/password', status_code=status.HTTP_200_OK)
async def change_user_password(
    user: user_dependency,
    db: DbDependency,
    password_data: PasswordChangeRequest
):
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not pwd_context.verify(password_data.current_password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    user_model.hashed_password = pwd_context.hash(password_data.new_password)
    db.commit()
    return {"detail": "Password updated successfully"}
