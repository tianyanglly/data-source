from flask import Blueprint, request
from app.utils.core import redis_client
from app.utils.response import ResMsg
import json

csgo = Blueprint("keep", __name__, url_prefix='/keep')

TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuYW5qaW5nIiwiaXNzIjoiR2FtZVNjb3Jla2VlcGVyIiwianRpIjoxNTIyNzUwOTg2MjAzMTE0MDEsImN1c3RvbWVyIjp0cnVlfQ.pQTeRnEAdNQgCULKewxZxTmGhrgLA42qneuF028Igwc'

@csgo.route('/live', methods=['GET', 'POST'])
def live():
    keys = request.headers.keys()
    if 'Authorization' not in keys:
        rsp = ResMsg()
        return rsp.error()
    if request.headers['Authorization'] != 'Bearer ' + TOKEN:
        rsp = ResMsg()
        return rsp.error()
    data = []
    for i in range(10):
        payload = redis_client.lpop('keep_csgo_live')
        if not payload:
            break
        data.append(json.loads(payload))
    rsp = ResMsg()
    return rsp.success(data)
