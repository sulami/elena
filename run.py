from flask import Flask, request

from elena.util import debug

from config import DEBUG

app = Flask("elena")
app.debug = DEBUG

@app.route("/")
def index():
    return "Are you still there?"

@app.route("/<int:id>/new/", methods=['POST'])
def new_status(id):
    name = request.form['name']
    debug("Adding new status {} for id {}".format(name, id))
    return "Success!"

if __name__ == "__main__":
    app.run()

