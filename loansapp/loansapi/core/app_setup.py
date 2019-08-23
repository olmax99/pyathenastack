import os

from flask import current_app, make_response, request
from flask import send_file, render_template

from flask import url_for
from loansapi.core.worker import celery
import celery.states as states

from flask import Blueprint
route_blueprint = Blueprint('route_blueprint', __name__)


# Create a URL route in our current_application for "/home"
@route_blueprint.route('/main')
def main():
    """
    This function just responds to the browser ULR
    localhost:5000/home

    :return:        the rendered template 'home.html'
    """
    return render_template('home.html')


@route_blueprint.route('/log_test')
def log_test():
    current_app.logger.debug('this is a DEBUG message')
    current_app.logger.info('this is an INFO message')
    current_app.logger.warning('this is a WARNING message')
    current_app.logger.error('this is an ERROR message')
    current_app.logger.critical('this is a CRITICAL message')
    index_path = os.path.join(current_app.static_folder, 'index.html')
    return send_file(index_path)


@route_blueprint.route('/add/<int:param1>/<int:param2>')
def add(param1: int, param2: int) -> str:
    task = celery.send_task('tasks.add', args=[param1, param2], kwargs={})
    response = make_response(render_template('task.html', task_id=task))
    response.headers.set('Content-Security-Policy', "default-src 'self'")
    return response


@route_blueprint.route('/check/<string:task_id>')
def check_task(task_id: str) -> str:
    res = celery.AsyncResult(task_id)
    if res.state == states.PENDING:
        return res.state
    else:
        return str(res.result)


# Everything not declared before (not a Flask route / API endpoint)...
@route_blueprint.route('/<path:path>')
def route_frontend(path):
    # ...could be a static file needed by the front end that
    # doesn't use the `static` path (like in `<script src="bundle.js">`)
    file_path = os.path.join(current_app.template_folder, path)
    if os.path.isfile(file_path):
        return send_file(file_path)
    # ...or should be handled by the SPA's "router" in front end
    else:
        index_path = os.path.join(current_app.static_folder, 'index.html')
        return send_file(index_path)
