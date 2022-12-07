import datetime
import uuid

from depot.fields.specialized.image import UploadedImageWithThumb
from depot.fields.sqlalchemy import UploadedFileField
from sqlalchemy import Column, Integer, String, Date, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import deferred

from .base import Base


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (UniqueConstraint('full_name', 'job_title', name='_fullname_jobtitle_uc'),
                      )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    email = Column(String(200), unique=True)
    password = deferred(Column(String))
    manager_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    full_name = Column(String(200))
    job_title = Column(String(100))
    employment_date = Column(Date, default=datetime.date.today())
    salary = Column(Integer)
    # photo = Column(UploadedFileField(upload_type=UploadedImageWithThumb))

