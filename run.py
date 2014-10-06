from flask import Flask, request, abort

from elena.models import BooleanStatus, NumberStatus

from config import DEBUG

app = Flask("elena")
app.debug = DEBUG

stati = {}

@app.route("/")
def index():
    return "Are you still there?"

@app.route("/new/", methods=['POST'])
def new_status():
    name = request.form['name']
    type = request.form['type']
    if type == "bool":
        status = BooleanStatus(True)
    stati[name] = status
    return "Success!"

@app.route("/<string:name>/")
def query_status(name):
    try:
        return str(stati[name].status)
    except KeyError:
        abort(404)

if __name__ == "__main__":
    app.run()

