import os

from flask import Flask, request, render_template, url_for

app = Flask(__name__)

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@app.route('/')
def hey_world():
    return "Hey, World's stupid citizen! I have come to take  shelter and food."

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
    	return jsonify({"hello": "world"})
    else:
        return "Log In Form"

@app.route('/<name>')
def hello_world(name=None):
    return render_template('index.html', name=name)

@app.route('/bye/')
def bye_world():
    return "Bye, World's stupid citizens! I have come to take  shelter and food."