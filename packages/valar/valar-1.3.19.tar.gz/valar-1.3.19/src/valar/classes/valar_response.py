from django.http import JsonResponse


class ValarResponse(JsonResponse):
    def __init__(self, data=True, message='', code='info', status=200):
        self.valar_message = message
        self.valar_code = code
        self.status_code = status
        super(ValarResponse, self).__init__(data, safe=False)
