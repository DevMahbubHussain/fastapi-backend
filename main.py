from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from routes import todos,auth,admin,user
from logger import logger
from db.database import Base,engine

# Create DB tables
Base.metadata.create_all(bind=engine)
app = FastAPI()

# app router
app.include_router(auth.router,prefix="/auth",tags=["Auth"])
app.include_router(todos.router,prefix="/todos",tags=["Todos"])
app.include_router(admin.router,prefix="/admin",tags=["Admin"])
app.include_router(user.router,prefix="/user",tags=["User Profile"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )