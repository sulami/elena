from flask import Flask, request

from elena.models import BooleanStatus, NumberStatus
from elena.util import debug

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
    debug("Adding new {} status {}".format(type, name, id))
    if type == "bool":
        status = BooleanStatus(True)
    stati[name] = status
    return "Success!"

@app.route("/<string:name>")
def query_status(name):
    return str(stati[name].status)

if __name__ == "__main__":
    app.run()

