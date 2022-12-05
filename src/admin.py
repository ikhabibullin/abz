from sqladmin import ModelView

from db.models import Employee


class UserAdmin(ModelView, model=Employee):
    column_list = [Employee.id, Employee.full_name, Employee.job_title, Employee.salary,
                   Employee.employment_date]
    column_searchable_list = [Employee.full_name, Employee.job_title, Employee.salary]
    column_sortable_list = [Employee.full_name, Employee.job_title, Employee.salary]
    page_size = 50
