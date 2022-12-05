import datetime
import random
import uuid
from typing import Union

from faker import Faker
from passlib.context import CryptContext
from pydantic import UUID4
from sqlalchemy import select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Employee
from schemas import PatchEmployee, Employee as EmployeeSchema, Register, Token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_employee(email: str, session: AsyncSession) -> Employee:
    result = await session.execute(select(Employee).where(Employee.email == email))
    return result.scalar()


async def get_employees(session: AsyncSession, ordering: str) -> list[Employee]:
    result = await session.execute(select(Employee).order_by(text(ordering)).limit(20))
    return result.scalars().all()


async def get_manager_children(manager_id: UUID4, session: AsyncSession) -> list[Employee]:
    result = await session.execute(select(Employee).where(Employee.manager_id == manager_id))
    return result.scalars().all()


async def add_employee(session: AsyncSession, employee: Union[EmployeeSchema, Register]):
    try:
        new_employee = Employee(**employee.dict())
        session.add(new_employee)
        await session.commit()
        return new_employee
    except IntegrityError as ex:
        await session.rollback()
        raise ex


async def generate_employee(session: AsyncSession):
    ranges = [1, 3, 12, 40]
    k = 0
    f = Faker()

    manager_ids = []

    for r in ranges:
        for i in range(r):
            k += 1
            new_employee = Employee(id=uuid.uuid4(),
                                    full_name=f.name(),
                                    job_title=f.job(),
                                    employment_date=f.date_between(start_date='-5y', end_date='today'),
                                    salary=random.randint(10_000, 50_000),
                                    manager_id=None if r == 1 else random.choice(manager_ids),
                                    email='user' + str(k) + '@user.com',
                                    password=get_password_hash('hackme'))
            manager_ids.append(new_employee.id)
            session.add(new_employee)
            await session.commit()


async def search_employee(session: AsyncSession, query: str) -> list[Employee]:
    result = await session.execute(select(Employee).where(
        (Employee.full_name.ilike("%"+query+"%") | (Employee.job_title.ilike("%"+query+"%"))
         )))
    return result.scalars().all()


async def update_employee(session: AsyncSession, employee_id: UUID4, data: PatchEmployee):
    query = update(Employee).where(Employee.id == employee_id).values(data.dict(exclude_none=True))
    query = query.returning(Employee.full_name, Employee.job_title, Employee.manager_id, Employee.salary,
                            Employee.employment_date)
    r = await session.execute(query)
    return r.fetchone()


def get_tokens(subject, authorize):
    access_token = authorize.create_access_token(subject=subject)
    refresh_token = authorize.create_refresh_token(subject=subject)
    return Token(access_token=access_token, refresh_token=refresh_token)
