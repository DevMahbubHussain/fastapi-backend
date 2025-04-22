from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from fastapi import APIRouter, Depends
from starlette import status
from starlette.status import HTTP_401_UNAUTHORIZED
from typing_extensions import deprecated, Annotated
from jose import JWTError,jwt
from models.users import Users
from schemas.users import UserRequest
from schemas.token import Token,TokenData
from passlib.context import CryptContext
from db.database import DbDependency
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer


# configurations
SECRET_KEY = "ecdsa-0.19.1 pyasn1-0.4.8 python-jose-3.4.0 rsa-4.9.1"  # Change this! Use env variables in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

pwd_context = CryptContext(schemes=['bcrypt'],deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def authenticate_user(username:str,password:str,db):
    user = db.query(Users).filter(Users.username==username).first()
    if not user:
        return False
    if not pwd_context.verify(password,user.hashed_password):
        return False
    return user

# create access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Create a dependency to verify tokens:
async def get_current_user(token:Annotated[str,Depends(oauth2_scheme)], db:DbDependency=None):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role:str = payload.get("role")

        if username is None or user_id is None or role is None:
            raise credentials_exception
        token_data = TokenData(username = username)

    except JWTError:
        raise credentials_exception

    user = db.query(Users).filter(Users.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    # return user
    return {"id": user_id, "username": username, "role": role}

# create new user
@router.post('/',status_code = status.HTTP_201_CREATED)
async def save_user(db:DbDependency,user_request:UserRequest):
    users = Users(
        email = user_request.email,
        username = user_request.username,
        first_name = user_request.first_name,
        last_name = user_request.last_name,
        role = user_request.role,
        hashed_password = pwd_context.hash(user_request.password),
        is_active = True
    )
    db.add(users)
    db.commit()
    db.refresh(users)
    return users

# create token
@router.post('/token',response_model=Token)
async def user_login_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:DbDependency):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub":user.username,"user_id": user.id,"role":user.role},
        expires_delta=access_token_expires
    )
    return {"access_token":access_token,"token_type":"bearer"}
