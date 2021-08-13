from app.bootstrap import create_app
from app.utils.response import ResMsg
from flask import json
from werkzeug.exceptions import HTTPException
import os


app = create_app(config_name=os.getenv('FLASK_ENV'))
app.app_context().push()


@app.route('/')
def index():
    return 'hello world'


@app.errorhandler(404)
def page_not_found(e):
    res = ResMsg()
    return res.error(), 404


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "msg": e.description,
    })
    app.logger.error('http error:{}'.format(e))
    response.content_type = "application/json"
    return response


@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    res = ResMsg()
    app.logger.error('exception:{}'.format(e))
    return res.error(), 500


# flask run --host=0.0.0.0 --port 21001
# export FLASK_APP=main.py
# export FLASK_ENV=development
if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=21001
    )
