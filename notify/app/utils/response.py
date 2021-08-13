from app.utils.code import ResponseCode, ResponseMessage


class ResMsg(object):
    """
    封装响应文本
    """

    def __init__(self, data=None, code=ResponseCode.Success):
        self._data = data
        self._msg = ResponseMessage[code]
        self._code = code

    def success(self, data=None):
        return {
            'code': ResponseCode.Success,
            'msg': ResponseMessage[ResponseCode.Success],
            'data': data
        }

    def error(self, code=ResponseCode.Fail):
        return {
            'code': code,
            'msg': ResponseMessage[code]
        }
