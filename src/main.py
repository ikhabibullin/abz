from fastapi import FastAPI
from fastapi_jwt_auth.exceptions import AuthJWTException
from sqladmin import Admin
from starlette.requests import Request
from starlette.responses import JSONResponse

from admin import UserAdmin
from api.employee import router as employee_router
from api.auth import router as auth_router
from db.base import init_models, async_session, engine
from service import generate_employee

app = FastAPI(title='abz')
app.include_router(employee_router)
app.include_router(auth_router)
admin = Admin(app, engine)
admin.add_view(UserAdmin)


@app.on_event('startup')
async def startup():
    await init_models()

    async with async_session() as session:
        await generate_employee(session)


@app.on_event('shutdown')
async def shutdown():
    pass


@app.exception_handler(AuthJWTException)
def jwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={'detail': exc.message}
    )
