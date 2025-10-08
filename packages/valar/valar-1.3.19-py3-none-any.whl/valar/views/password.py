import json
import secrets
from django.contrib.auth.hashers import check_password, make_password

from ..auth.Authentication import auth_required
from ..classes.valar_response import ValarResponse

from ..dao.engine import ValarEngine
from ..models.auth import Account, AbstractUser


def send_password(request):
    body = json.loads(request.body)
    account_id = body.get('account_id')
    account = Account.objects.filter(id=account_id).first()
    return __send__(account)


def retrieve_password(request):
    includes = json.loads(request.body)
    account = Account.objects.filter(**includes).first()
    account.token = account.token or secrets.token_hex(16)
    account.save()
    if account:
        return __send__(account)
    else:
        return ValarResponse(False, '该邮箱未在系统中注册', code='error')


@auth_required
def change_password(request):
    body = json.loads(request.body)
    old_password = body.get('old_password')
    new_password = body.get('new_password')
    account_id = request.user_id
    account = Account.objects.get(id=account_id)
    if not account:
        return ValarResponse(False, '账户不存在', code='error')
    if not account.is_auth(old_password):
        return ValarResponse(False, '当前密码错误', code='error')
    if old_password == new_password:
        return ValarResponse(False, '新密码不能与当前密码一致', code='error')
    account.password = make_password(new_password)
    account.token = None
    account.save()
    return ValarResponse(True)


def __send__(account):
    if not account:
        return ValarResponse(False, '账户不存在', code='error')
    token = account.token
    if not token:
        return ValarResponse(False, '未生成临时密码', code='error')
    email = account.email
    if not email:
        return ValarResponse(False, '该账户未登记邮箱信息', code='error')
    content = f'Your temporary password is {token}, please change it as soon as possible.'
    ValarEngine().send_email('Retrieve Password', content, email)
    return ValarResponse(True, '临时密码发送成功', 'success')
