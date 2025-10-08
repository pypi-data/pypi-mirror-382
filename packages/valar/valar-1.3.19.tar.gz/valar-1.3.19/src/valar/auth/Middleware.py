import base64
import json

from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from ..auth.Authentication import valid_request_token, ValaAuthError
from ..classes.valar_response import ValarResponse


class ValarMiddleware(MiddlewareMixin):
    @staticmethod
    def process_response(request: HttpRequest, response: ValarResponse):
        try:
            payload = valid_request_token(request)
            response["token"] = payload['token'] or '~~~'
            """此处可以加入数据级别的权限验证"""
        except ValaAuthError as e:
            if request.headers.get("Auth"):
                return ValarResponse(False, '无效权限', 'error', status=403)

        if type(response) == ValarResponse:
            valar_message, valar_code = response.valar_message, response.valar_code
            data = {
                'payload': json.loads(response.content),
                'message': valar_message,
                'code': valar_code,
            }
            response.content = json.dumps(data, ensure_ascii=False).encode("utf-8")
            response["Content-Type"] = "application/json; charset=utf-8"

        return response
