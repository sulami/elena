from flask import Flask, request

from elena.database import Database
from elena.models import BooleanStatus, NumberStatus
from elena.util import str_to_bool

from config import DefaultConfig

app = Flask("elena")
app.config.from_object('config.DefaultConfig')

def init_db():
    app.db = Database(app.config['DB_URI'])

@app.teardown_appcontext
def shutdown_session(exception=None):
    app.db.session.remove()

@app.route("/")
def index():
    return "Are you still there?"

@app.route("/set/<string:name>/", methods=['POST'])
def set_status(name):
    value = request.form['value']
    if value == "True" or value == "False":
        status = BooleanStatus.query.get(name)
        app.db.session.commit()
        if status:
            status.bstatus = str_to_bool(value)
        else:
            status = BooleanStatus(name, str_to_bool(value))
        app.db.session.add(status)
        app.db.session.commit()
    return "Success!", 201

@app.route("/get/<string:name>/")
def get_status(name):
    status = BooleanStatus.query.get(name)
    if status:
        return str(status.get_status()), 200
    return "ERROR: This status does not exist", 404

if __name__ == "__main__":
    init_db()
    app.run()

