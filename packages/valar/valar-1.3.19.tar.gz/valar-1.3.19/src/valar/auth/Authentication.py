import jwt
from django.conf import settings

from ..classes.valar_response import ValarResponse


class ValaAuthError(Exception):
    def __init__(self, message, code):
        self.code = code
        self.message = message


def auth_required(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            payload = valid_request_token(request)
            request.user_id = payload["user_id"]
            return view_func(request, *args, **kwargs)
        except ValaAuthError as e:
            return ValarResponse(False, e.message, e.code, status=401)

    return wrapper


def get_token_from_request(request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None


status = {
    0: (None, None, None),
    1: ('请登录系统', 'info', 401),
    2: ('状态已过期，请重新登录', 'warning', 401),
    3: ('错误状态，请重新登录', 'error', 401),
}


def valid_request_token(request):
    token = get_token_from_request(request)
    if not token: raise ValaAuthError('请登录系统', 'info')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        payload['token'] = token
        return payload
    except jwt.ExpiredSignatureError:
        raise ValaAuthError('状态已过期，请重新登录', 'warning')
    except jwt.InvalidTokenError:
        raise ValaAuthError('错误状态，请重新登录', 'error')
