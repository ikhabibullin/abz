from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_jwt_auth import AuthJWT
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import service
from db.base import get_session, get_transaction_session
from schemas import Employee, PatchEmployee

router = APIRouter(prefix='/employee', tags=['employee'])


@router.get('/employees/', response_model=list[Employee], description='Получение списка сотрудников')
async def get_employees(ordering: str = 'full_name',
                        session: AsyncSession = Depends(get_session),
                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    if ordering not in Employee.__fields__:
        raise HTTPException(400, detail='У Employee нет поля {0}'.format(ordering))

    employees = await service.get_employees(session, ordering)
    return [Employee.from_orm(e) for e in employees]


@router.get('/{manager_id}/childs')
async def get_manager_children(manager_id: UUID4, session: AsyncSession = Depends(get_session)):
    children = await service.get_manager_children(manager_id, session)
    return children


@router.post('', status_code=201, description='Создание сотрудника')
async def add_employee(employee: Employee,
                       session: AsyncSession = Depends(get_session)):

    try:
        employee = await service.add_employee(session, employee)
        return employee
    except IntegrityError as ex:
        raise HTTPException(422, detail='The employee is already stored')


@router.get('/search/', description='Поиск по full name, job_title')
async def search_employee(query: str = Query(None, description='Поисковый запрос'),
                          session: AsyncSession = Depends(get_session)):
    employees = await service.search_employee(session, query)
    return employees


@router.patch('/{employee_id}')
async def patch_employee(employee_id: UUID4,
                         employee: PatchEmployee,
                         session: AsyncSession = Depends(get_transaction_session),
                         authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    current_user = authorize.get_jwt_subject()
    if current_user != str(employee_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    employee = await service.update_employee(session, employee_id, employee)
    return Employee.from_orm(employee)
