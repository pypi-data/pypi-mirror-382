import datetime
import json

import jwt
from django.conf import settings
from django.db.models import OneToOneRel
from django.contrib.auth.hashers import make_password

from ..auth.Authentication import auth_required
from ..classes.valar_response import ValarResponse
from ..dao import Dao
from ..models.auth import Account, AbstractUser, Menu


def sign_in(request):
    body = json.loads(request.body)
    username = body.get("username")
    email = body.get("email")
    password = body.get("password")
    signin = body.get("signin")
    dao = Dao('valar.Account')
    account = dao.search({"username": username}).first()
    if account is not None:
        if signin:
            if not account.is_auth(password):
                return ValarResponse(False, '密码错误', 'warning', status=400)
        else:
            return ValarResponse(False, f"{username}已被占用", 'warning', status=400)
    else:
        if signin:
            return ValarResponse(False, f"{username}不存在", 'warning', status=400)
        else:
            if username == 'admin' and password != settings.SECRET_KEY:
                return ValarResponse(False, "请输入正确的admin密码", 'warning', status=400)
            else:
                account = dao.save_one({
                    "username": username,
                    "email": email,
                    "password": make_password(password),
                    "is_admin": username == 'admin'
                })
    return ValarResponse(jwt.encode({
        "user_id": account.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=5)
    }, settings.SECRET_KEY, algorithm="HS256"))


def free_menus(request):
    body = json.loads(request.body)
    scope = body.get("scope", 'admin')
    menus = Menu.objects.filter(
        isLeaf=True, scope=scope, is_admin=False, path__isnull=False, is_auth=False,
        roles__isnull=True).values('path')
    payload = {"permissions": [m['path'] for m in menus]}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return ValarResponse(token)


@auth_required
def user_profile(request):
    body = json.loads(request.body)
    scope = body.get("scope", 'admin')
    account_id = request.user_id
    account = Account.objects.filter(id=account_id).first()
    if account is None:
        return ValarResponse(False, f"账户已不存在", 'warning', status=401)
    user_admin = account.is_admin
    user_roles = list(account.roles.values('id', 'name'))
    user_role_keys = [r['id'] for r in user_roles]
    permissions = []
    for m in Menu.objects.filter(isLeaf=True, scope=scope):
        _id = m.path
        if _id is None:
            continue
        if user_admin:
            permissions.append(_id)
        else:
            if not m.is_admin:
                menu_role_keys = [r['id'] for r in m.roles.all().values('id')]
                if len(menu_role_keys):
                    if bool(set(user_role_keys) & set(menu_role_keys)):
                        permissions.append(_id)
                else:
                    permissions.append(_id)
    payload = {
        "username": account.username,
        "roles": user_roles,
        "is_admin": user_admin,
        "email": account.email,
        "is_active": account.is_active,
        "temporary": account.token is not None,
        "permissions": permissions
    }
    field = (
        next((field for field in account.get_meta().get_fields()
              if type(field) == OneToOneRel
              and issubclass(field.related_model, AbstractUser)), None))
    if field:
        accessor = field.get_accessor_name()
        model = field.related_model
        entity = f'{model._meta.app_label}.{model.__name__}'
        payload.update({'user_entity': entity, 'user_accessor': accessor})
        if hasattr(account, accessor):
            user = getattr(account, accessor)
            name = getattr(user, 'name')
            key = getattr(user, 'id')
            payload.update({'name': name, 'user_key': key})
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return ValarResponse(token)
