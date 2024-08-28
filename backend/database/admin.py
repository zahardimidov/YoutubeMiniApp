from config import ADMIN_PASSWORD, ADMIN_USERNAME
from database.models import User, Plan, Quota, API_KEY
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
    column_list = [User.id, User.username, User.subscription_until]

    can_create = False
    can_edit = True
    form_widget_args_update = dict(
        id=dict(readonly=True), username=dict(readonly=True))
    
class PlanAdmin(ModelView, model=Plan):
    column_list = [Plan.id, Plan.days, Plan.price]

    can_create = True
    can_edit = True

class QuotaAdmin(ModelView, model=Quota):
    column_list = [Quota.quota]

    can_create = True
    can_edit = True

class ApiKeyAdmin(ModelView, model=API_KEY):
    column_list = [API_KEY.key]

    can_create = True
    can_edit = True


def init_admin(app, engine):
    admin = Admin(app, engine=engine,
                  authentication_backend=authentication_backend)
    admin.add_view(UserAdmin)
    admin.add_view(PlanAdmin)
    admin.add_view(QuotaAdmin)
    admin.add_view(ApiKeyAdmin)
