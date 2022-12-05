from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db.base import get_session
from schemas import Register, RegisterOut, Login, Token
from service import add_employee, get_employee, verify_password, get_tokens

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', status_code=201)
async def register(employee: Register, authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)):
    try:
        employee = await add_employee(session, employee)
    except IntegrityError as ex:
        raise HTTPException(status_code=400, detail='It seems that such email already exists')

    return get_tokens(str(employee.id), authorize)


@router.post('/login')
async def login(login_data: Login, authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)):
    employee = await get_employee(email=login_data.email, session=session)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Wrong email or password.')

    if verify_password(login_data.password, employee.password):
        return get_tokens(str(employee.id), authorize)

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Wrong email or password.')


@router.post('/refresh')
def refresh(authorize: AuthJWT = Depends()):
    authorize.jwt_refresh_token_required()

    current_user = authorize.get_jwt_subject()
    new_access_token = authorize.create_access_token(subject=current_user)
    return {"access_token": new_access_token}
