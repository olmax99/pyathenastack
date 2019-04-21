import os

from loansapi.api import app
from flask import send_file, render_template


@app.route("/")
def main():
    index_path = os.path.join(app.static_folder, 'index.html')
    return send_file(index_path)


# Create a URL route in our application for "/"
@app.route('/home')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    return render_template('home.html')


@app.route("/hello")
def hello():
    # This could also be returning an index.html
    return '''Hello ya'all from Flask in a uWSGI Nginx Docker container with \
     Python 3.7 (from the example template), 
     try also: <a href="/users/">/users/</a>'''


# Everything not declared before (not a Flask route / API endpoint)...
@app.route('/<path:path>')
def route_frontend(path):
    # ...could be a static file needed by the front end that
    # doesn't use the `static` path (like in `<script src="bundle.js">`)
    file_path = os.path.join(app.template_folder, path)
    if os.path.isfile(file_path):
        return send_file(file_path)
    # ...or should be handled by the SPA's "router" in front end
    else:
        index_path = os.path.join(app.static_folder, 'index.html')
        return send_file(index_path)
