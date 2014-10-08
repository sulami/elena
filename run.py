from flask import Flask, request

from elena.database import Database
from elena.models import Status

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
    status = Status.query.all()
    r = ''
    for s in status:
        r += s.__repr__() + "\n"
    return r

@app.route("/set/<string:name>/", methods=['POST'])
def set_status(name):
    value = request.form['value']
    status = Status.query.get(name)
    if status:
        status.update(value)
    else:
        status = Status(name, value)
    app.db.session.add(status)
    app.db.session.commit()
    return "Success!", 201

@app.route("/get/<string:name>/")
def get_status(name):
    status = Status.query.get(name)
    if status:
        return str(status.get()), 200
    return "ERROR: This status does not exist", 404

@app.route("/del/<string:name>/")
def del_status(name):
    status = Status.query.get(name)
    if status:
        app.db.session.delete(status)
        app.db.session.commit()
        return "Success!", 204
    return "ERROR: This status does not exist", 404

@app.route("/status/")
def statusreport():
    # TODO elaborate status report
    return "Number of Stati:" + str(len(Status.query.all())), 200

if __name__ == "__main__":
    init_db()
    app.run()

