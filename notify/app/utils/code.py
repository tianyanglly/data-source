class ResponseCode(object):
    Success = 200
    Fail = -1
    NoResourceFound = 404
    InvalidParameter = 402
    FrequentOperation = 409
    ServerError = 500


ResponseMessage = {
    ResponseCode.Success: '成功',
    ResponseCode.Fail: '失败',
    ResponseCode.NoResourceFound: '未找到资源',
    ResponseCode.InvalidParameter: '参数无效',
    ResponseCode.FrequentOperation: '操作频繁,请稍后再试',
    ResponseCode.ServerError: '服务器开小差了'
}
