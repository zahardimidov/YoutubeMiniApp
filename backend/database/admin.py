from config import ADMIN_PASSWORD, ADMIN_USERNAME
from database.models import User, Plan, Quota, Api
from fastapi import Request
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if not (username == ADMIN_USERNAME and password == ADMIN_PASSWORD):
            return False

        request.session.update(
            {"token": "fdbb0dd1-a368-4689-bd71-5888f69b438e"})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token == 'fdbb0dd1-a368-4689-bd71-5888f69b438e':
            return False
        return True


authentication_backend = AdminAuth(secret_key="secret")


class UserAdmin(ModelView, model=User):
    name = 'Пользователь'
    name_plural = 'Пользователи'

    column_list = [User.id, User.username, User.subscription_until]
    column_searchable_list = [User.username]
    column_labels = dict(username='Имя пользователя', subscription_until = 'Подписка до')

    can_create = False
    can_edit = True
    form_widget_args_update = dict(
        id=dict(readonly=True), username=dict(readonly=True))
    
class PlanAdmin(ModelView, model=Plan):
    name = 'Тариф'
    name_plural = 'Тарифы'

    column_list = [Plan.id, Plan.price, Plan.days]
    column_labels = dict(days='Продолжительность подписки в днях', price = 'Цена')

    can_create = True
    can_edit = True

class QuotaAdmin(ModelView, model=Quota): 
    name = 'Дневная квота'
    name_plural =  'Дневная квота'

    column_list = [Quota.quota]
    column_labels = dict(quota = 'Квота')

    can_create = True
    can_edit = True

class ApiAdmin(ModelView, model=Api):
    name = 'Youtube API ключ'
    name_plural = 'Youtube API ключ'
    
    column_list = [Api.key]
    column_labels = dict(key = 'Ключ')

    can_create = True
    can_edit = True


def init_admin(app, engine):
    admin = Admin(app, engine=engine,
                  authentication_backend=authentication_backend)
    admin.add_view(UserAdmin)
    admin.add_view(PlanAdmin)
    admin.add_view(QuotaAdmin)
    admin.add_view(ApiAdmin)
